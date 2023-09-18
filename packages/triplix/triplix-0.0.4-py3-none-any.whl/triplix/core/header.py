
import sys
import gzip
import time
import pathlib
import hashlib
import importlib
import json
import re
# from dataclasses import dataclass
from typing import Union

import pysam
import h5py

from triplix.core import configurations
from triplix.core.utilities import get_random_string
from triplix.core.hdf5 import HDF5Container
from triplix._logging import get_logger

logger = get_logger(__name__)


class PGNode:
    def __init__(self, pg_info: Union[str, dict]):
        if isinstance(pg_info, str):
            assert pg_info.startswith('@PG')
            pg_info = dict(field.split(':', maxsplit=1) for field in pg_info.split('\t')[1:])
            if 'PS' in pg_info:
                if pg_info['PS'] == '':
                    pg_info['PS'] = []
                else:
                    pg_info['PS'] = pg_info['PS'].split(',')

        if 'VN' not in pg_info:
            pg_info['VN'] = 'NA'
        if 'CL' not in pg_info:
            pg_info['CL'] = ' '.join(sys.argv)
        if 'PS' not in pg_info:
            if 'PP' in pg_info:
                pg_info['PS'] = [pg_info['PP']]
            else:
                pg_info['PS'] = []
        assert isinstance(pg_info['PS'], list), 'PS field should be a list of parent(s)'
        # else:
        #     if isinstance(pg_info['PS'], str):
        #         pg_info['PS'] = [pg_info['PS']]

        self.data = pg_info
        self.children_ids = []

    def hash(self):
        hasher = hashlib.md5()
        hasher.update(json.dumps(self.data, sort_keys=True).encode())
        return hasher.hexdigest()

    def __getitem__(self, field_name: str):
        return self.data[field_name]

    def __setitem__(self, field_name: str, value: str):
        self.data[field_name] = value

    def __contains__(self, item):
        return item in self.data

    def __str__(self):
        out = ['@PG:']
        for key, value in self.data.items():
            if isinstance(value, str):
                out += [f'{key}:{value}']
            else:
                out += [f'{key}:{",".join(value)}']
        return '\t'.join(out)

    def __repr__(self):
        out = []
        for key, value in self.data.items():
            out += [f'{key}> {value}']
        for child_id in self.children_ids:
            out += [f'Child --> {child_id}']
        return '\n'.join(out)


class ProcessHistoryDAG:

    def __init__(self, sam_headers=None):
        self.headers = {'HD': {}, 'SQ': []}
        self.programs = {}
        self.source_ids = []
        self.destination_id = None
        if sam_headers is not None:
            self.from_sam_headers(sam_headers)

    def from_sam_headers(self, sam_headers):
        for hdr_idx, sam_header in enumerate(sam_headers):
            if sam_header[:3] in ['@HD', '@SQ']:
                fields = sam_header.split('\t')
                values = dict(field.split(':', maxsplit=1) for field in fields[1:])
                if fields[0] == '@HD':
                    self.headers['HD'] = values
                else:
                    self.headers['SQ'].append(values)
            else:
                assert sam_header.startswith('@PG')
                pg_node = PGNode(sam_header)
                self.add_pg(pg_node)

    def to_sam_headers(self):

        # sam headers
        sam_headers = [
            f'@HD\t' +
            '\t'.join([f'{key}:{value}' for key, value in self.headers['HD'].items()])
        ]
        for sq_item in self.headers['SQ']:
            sam_headers.append(
                f'@SQ\t' +
                '\t'.join([f'{key}:{value}' for key, value in sq_item.items()])
            )

        # processing history
        for program_id, program in self.programs.items():
            row = ['@PG:']
            for key, value in program.data.items():
                if isinstance(value, str):
                    row += [f'{key}:{value}']
                elif key in ['PS']:
                    if len(value) > 0:
                        row += [f'{key}:{",".join(value)}']
                else:
                    row += [f'{key}:{",".join(value)}']
            sam_headers += ['\t'.join(row)]
        return sam_headers

    def add_pg(self, pg_node: Union[PGNode, dict], is_destination=True):
        if isinstance(pg_node, dict):
            pg_node = PGNode(pg_node)
        assert pg_node['ID'] not in self.programs
        self.programs[pg_node['ID']] = pg_node

        if len(pg_node['PS']) == 0:
            self.source_ids.append(pg_node['ID'])
        else:
            for parent_id in pg_node['PS']:
                assert parent_id in self.programs
                self.programs[parent_id].children_ids.append(pg_node['ID'])

        if is_destination:
            self.destination_id = pg_node['ID']

    def __repr__(self):
        if len(self.source_ids) == 0:
            return 'Empty History'
        out = ''
        for source_id in self.source_ids:
            out += f'--- Source: {self.programs[source_id]["ID"]}\n'
            out += self._print_children(self.programs[source_id], level=0)
            out += f'--- End of: {self.programs[source_id]["ID"]}\n'
        return out

    def _print_children(self, pg_node: PGNode, level=0):
        out = "|\t" * level + f'{pg_node}\n'
        for child_id in pg_node.children_ids:
            out += self._print_children(self.programs[child_id], level=level + 1)
        return out

    def visualize(self, output_path=None, **kwargs):
        igraph_installed = importlib.util.find_spec('igraph') is not None
        assert igraph_installed, '"igraph" library is not installed. Please install it using: `pip install igraph`'
        import igraph
        from matplotlib import pyplot as plt
        import matplotlib as mpl

        # generate the graph
        ph_graph = igraph.Graph(directed=True)
        ph_graph.add_vertices(list(self.programs.keys()))
        ph_graph.vs['label'] = ph_graph.vs['name']
        ph_graph.vs['color'] = '#4fd1fc'
        root_idxs = []
        for pg_idx, (pg_name, pg_node) in enumerate(self.programs.items()):

            # annotate the source nodes
            if len(pg_node['PS']) == 0:
                ph_graph.vs[pg_idx]['color'] = '#81fd90'
                root_idxs.append(pg_idx)

            # adding edges
            for child_id in pg_node.children_ids:
                ph_graph.add_edge(pg_name, child_id)
            # if ph_graph.ecount() > 20:
            #     break

        # filtering isolated vertices
        ph_graph.vs.select(_degree=0).delete()

        # plt.close('all')
        fig_h = plt.figure(figsize=kwargs.get('figsize', (10, 7)))
        ax = plt.gca()

        # graph_layout = ph_graph.layout('kamada_kawai')
        # graph_layout = ph_graph.layout(kwargs.get('layout', 'reingold_tilford'))
        # graph_layout = ph_graph.layout_reingold_tilford(root=root_idxs)
        # graph_layout = ph_graph.layout_reingold_tilford_circular(root=root_idxs)
        graph_layout = ph_graph.layout_sugiyama()
        # graph_layout = ph_graph.layout_davidson_harel()
        ax.img_h = igraph.plot(
            ph_graph,
            target=ax,
            layout=graph_layout,
            vertex_shape='rectangle',
            vertex_label=ph_graph.vs['name'],
            vertex_label_size=kwargs.get('fontsize', 4),
            vertex_size=15,
            vertex_color=ph_graph.vs['color'],
            vertex_frame_color='none',
            alpha=1.0,
            **kwargs,
        )
        # possible shapes:
        #         "rectangle": "s", # always a square
        #         "circle": "o",
        #         "hidden": "none",
        #         "triangle-up": "^",
        #         "triangle-down": "v",
        # shape_size = [len(label) * 2 for label in ph_graph.vs['label']]
        # text_size = np.array([len(label) for label in ph_graph.vs['name']])
        # label_dist = (text_size - text_size.min()) / (text_size.max() - text_size.min())
        ax.invert_yaxis()
        plt.axis('off')
        plot_title = kwargs.get('title', None)
        if plot_title is not None:
            ax.set_title(plot_title, fontweight='bold')
            # plt.suptitle(plot_title, fontweight='bold')
        # fig_h.set_visible(not fig_h.get_visible())
        # plt.draw()

        # align text objects
        for child in ax.get_children():
            if isinstance(child, mpl.text.Text):
                child.set_horizontalalignment('center')
                child.set_verticalalignment('center')
        # todo: adding a rectangle for each node, to make its size adjustable
        # ax.collections[0].get_offsets().data

        # store the graph if requested
        if output_path is None:
            plt.show()
        else:
            output_path = pathlib.Path(output_path).expanduser()

            # logger_fonttools = logging.getLogger('fontTools.subset')
            # loglevel_prev = logger_fonttools.level
            # logger_fonttools.setLevel(logging.WARNING)
            plt.savefig(fname=output_path)  # , bbox_inches='tight'
            # logger_fonttools.setLevel(loglevel_prev)
            plt.close()
            logger.info(f'The processing history plot is stored in: {output_path}')


class TriplixHeader:
    FORMAT_VERSION = '1.0.0'

    def __init__(self, file_path=None, exclusive=False):
        self.exclusive = exclusive

        self.format_version = TriplixHeader.FORMAT_VERSION
        self.triplix_version = configurations.configs['version']
        self.creation_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.cell_type = None
        self.assay_name = None
        self.experiment_name = None
        self.source_file = None
        self.assembly_name = None
        self.assembly_length = None
        self.chrom_lengths = {}
        self.stored_chunks = []
        self.shape = 'upper triangle'
        self.sort_order = []
        self.anchor_width = None
        self.transformations = []
        self.background_normalizations = {}
        # self.sam_headers = []
        self.column_names = []
        self.process_history = ProcessHistoryDAG()

        # todo: add column_dtypes to headers
        # self.column_dtypes = []

        self.file_path = file_path
        if self.file_path is not None:
            self.extract_header(self.file_path)

    def __repr__(self):
        return self.to_string()

    def extract_header(self, file_path):
        self.file_path = pathlib.Path(file_path).expanduser()
        assert self.file_path.is_file(), f'File not found: {self.file_path}'
        self.file_path = str(self.file_path)

        # extract using appropriate method
        if self.file_path.endswith('.bam'):
            _verbosity_level = pysam.set_verbosity(0)
            with pysam.AlignmentFile(self.file_path, 'r') as bam_file:
                pysam.set_verbosity(_verbosity_level)
                sam_headers = str(bam_file.header).rstrip().split('\n')
                self.process_history = ProcessHistoryDAG(sam_headers)
                self.chrom_lengths = {}
                for sq_item in self.process_history.headers['SQ']:
                    self.chrom_lengths[sq_item['SN']] = int(sq_item['LN'])
        elif self.file_path.endswith('.concatemers.h5'):
            logger.debug(f'Opening (mode=r): {self.file_path}')
            with h5py.File(self.file_path, 'r') as h5_file:
                cnct_grp = h5_file['concatemers']
                self.format_version = cnct_grp.attrs['format_version']
                self.triplix_version = cnct_grp.attrs['triplix_version']
                self.creation_timestamp = cnct_grp.attrs['creation_timestamp']
                self.assay_name = cnct_grp.attrs['assay_name']
                self.cell_type = cnct_grp.attrs['cell_type']
                self.experiment_name = cnct_grp.attrs['experiment_name']
                self.source_file = cnct_grp.attrs['source_file']
                if 'genome_name' in cnct_grp.attrs:
                    self.assembly_name = cnct_grp.attrs['genome_name']
                else:
                    self.assembly_name = cnct_grp.attrs['assembly_name']
                if 'genome_length' in cnct_grp.attrs:
                    self.assembly_length = cnct_grp.attrs['genome_length']
                else:
                    self.assembly_length = cnct_grp.attrs['assembly_length']
                self.chrom_lengths = dict(zip(
                    cnct_grp.attrs['chrom_names'],
                    cnct_grp.attrs['chrom_lengths'],
                ))
                stored_chunks = [re.split(r'[:-]', range_str) for range_str in cnct_grp.attrs['stored_chunks']]
                self.stored_chunks = [[chrom, int(start), int(end)] for (chrom, start, end) in stored_chunks]
                self.shape = 'upper triangle'
                self.sort_order = []
                sam_headers = cnct_grp.attrs['sam_headers'].tolist()
                self.process_history = ProcessHistoryDAG(sam_headers)
                self.column_names = [
                    'chrom_A', 'start_A', 'end_A',
                    'chrom_B', 'start_B', 'end_B',
                    'chrom_C', 'start_C', 'end_C',
                    'strand_A', 'strand_B', 'strand_C',
                    'mapq_A', 'mapq_B', 'mapq_C',
                    'frag_index_A', 'frag_index_B', 'frag_index_C',
                    'read_name', 'read_length_nbp', 'read_length_nfrag',
                    'experiment_name',
                ]
        elif self.file_path.endswith(('.tri-alignments.tsv.bgz', '.btrp')):
            with gzip.open(self.file_path, 'rt') as gz_file:

                # get file type
                file_type = next(gz_file).rstrip()
                assert file_type in ['## Triplets', '## Triplix'], 'Unknown file format'

                sam_headers = []
                for line in gz_file:
                    line = line.rstrip()
                    if not line.startswith('#'):
                        raise ValueError('Unknown header format')

                    # process key, values
                    key, attr_value = line[1:].split(': ')
                    attr_name = key.replace(' ', '_')
                    if attr_name in ['sort_order', 'column_names']:
                        setattr(self, attr_name, attr_value.split('\t'))
                        if attr_name == 'sort_order' and len(attr_value) == 0:
                            setattr(self, 'sort_order', [])
                    elif attr_name == 'transformation':
                        transformation = dict(field.split(':') for field in attr_value.split('\t'))
                        self.transformations.append(transformation)
                    elif attr_name == 'chrom_lengths':
                        self.chrom_lengths = {}
                        for chr2len_pair in attr_value.split('\t'):
                            chr_name, chr_len = chr2len_pair.split(':')
                            self.chrom_lengths[chr_name] = int(chr_len)
                    elif attr_name in ['stored_chunks', 'table_chunks']:  # todo: 'table_chunks' should be removed, added for compatibility
                        self.stored_chunks = []
                        for chr2rng_pair in attr_value.split('\t'):
                            chr_name, chr_rng = chr2rng_pair.split(':')
                            chr_start, chr_end = [int(item) for item in chr_rng.split('-')]
                            self.stored_chunks.append([chr_name, chr_start, chr_end])
                    elif attr_name == 'sam_header':
                        sam_headers.append(attr_value)
                    elif attr_name in ['resolution', 'anchor_width', 'genome_length', 'assembly_length']:
                        # if attr_name == 'anchor_width':
                        #     logger.warning('Anchor width is ignored')
                        #     setattr(self, attr_name, None)
                        #     continue
                        setattr(self, attr_name, int(attr_value))
                    else:
                        setattr(self, attr_name, attr_value)
                    if attr_name == 'column_names':
                        break
            self.process_history = ProcessHistoryDAG(sam_headers)
        elif self.file_path.endswith('.triplets.h5'):
            with HDF5Container(self.file_path, mode='r', exclusive=self.exclusive) as container:
                expr_grp = container.h5_file['experiments']
                self.experiment_name = list(expr_grp.keys())[0]
                self.anchor_width = expr_grp[self.experiment_name].attrs['anchor_width']

                chrom_grp = expr_grp[self.experiment_name]['chroms']
                self.chrom_lengths = {chr_name.decode(): chr_length for chr_name, chr_length in zip(chrom_grp['name'], chrom_grp['length'])}
        else:
            raise ValueError('Unknown file extension.')

    def to_string(self):
        outputs = ['## Triplix']
        headers_ordered = [
            'format version',
            'triplix version',
            'creation timestamp',
            'cell type',
            'assay name',
            'experiment name',
            'source file',
            'assembly name',
            'assembly length',
            'chrom lengths',
            'stored chunks',
            'shape',
            'sort order',
            'anchor width',
            'transformations',
            'background normalizations',
            'sam headers',
            'column names',
        ]

        # iterate over headers and add their string representation
        for header in headers_ordered:
            attr_name = header.replace(' ', '_')
            if attr_name in ['sam_headers']:
                attr_value = self.process_history.to_sam_headers()
            else:
                if not hasattr(self, attr_name):
                    logger.warning(f'Missing attribute: {attr_name}')
                    continue
                attr_value = getattr(self, attr_name)
            if header == 'chrom lengths':
                chrom_lengths_str = [f'{chr_name}:{chr_len:d}' for chr_name, chr_len in self.chrom_lengths.items()]
                outputs += [f'#chrom lengths: ' + '\t'.join(chrom_lengths_str)]
            elif header == 'sam headers':
                for sam_header in self.process_history.to_sam_headers():
                    outputs += ['#sam header: ' + sam_header]
            elif header == 'stored chunks':
                stored_chunks = [f'{chr_name}:{start:d}-{end:d}' for chr_name, start, end in self.stored_chunks]
                outputs += [f'#stored chunks: ' + '\t'.join(stored_chunks)]
            elif header == 'transformations':
                for transformation in self.transformations:
                    outputs += [f'#transformation: ' + '\t'.join(f'{key}:{value}' for key, value in transformation.items())]
            elif header == 'background normalizations':
                if len(self.background_normalizations) > 0:
                    outputs += [f'#background normalizations: ' + '\t'.join(f'{feat_name}:{norm["name"]}' for feat_name, norm in self.background_normalizations.items())]
            elif isinstance(attr_value, list):
                if len(attr_value) != 0:  # second-level if is needed
                    outputs += [f'#{header}: ' + '\t'.join(attr_value)]
            elif attr_value is not None:
                outputs += [f'#{header}: {attr_value}']

        return '\n'.join(outputs)

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def merge_process_histories(self, headers, check_uniqueness=False):
        assert len(headers) > 0
        self.process_history = ProcessHistoryDAG()
        self.process_history.headers['HD'] = headers[0].process_history.headers['HD']
        self.process_history.headers['SQ'] = headers[0].process_history.headers['SQ']

        # validate HD rows, they all should be identical
        for header in headers:
            if self.process_history.headers['HD'] != header.process_history.headers['HD']:
                raise SyntaxError(
                    f'Inconsistent @HD lines:\n'
                    f'      One @HD is: {self.process_history.headers["HD"]}\n'
                    f'The other @HD is: {header.process_history.headers["HD"]}'
                )

        # validate SQ rows, they all should be identical. The order is kept
        for seq_info in self.process_history.headers['SQ']:
            for header in headers:
                try:
                    header.process_history.headers['SQ'].index(seq_info)
                except ValueError:
                    raise ValueError(f'Inconsistent @SQ: Missing {seq_info}')

        # merge process histories
        for header in headers:
            for pg_id, pg_node in header.process_history.programs.items():
                if pg_node['ID'] in self.process_history.programs:
                    if check_uniqueness:
                        raise ValueError(
                            f'Duplicated PG:ID is found:\n'
                            f'Prog 1: {self.process_history.programs[pg_node["ID"]]}\n'
                            f'Prog 2: {pg_node}'
                        )
                else:
                    self.process_history.programs[pg_node['ID']] = pg_node
                    if len(pg_node['PS']) == 0:
                        self.process_history.source_ids.append(pg_node['ID'])
        self.process_history.destination_id = None
