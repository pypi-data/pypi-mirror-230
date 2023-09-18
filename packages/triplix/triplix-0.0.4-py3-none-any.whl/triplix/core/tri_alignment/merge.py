
import glob
import io
import time
import pathlib
import subprocess
import copy


from triplix.core.header import TriplixHeader
from triplix.core import configurations
from triplix.core.utilities import generate_prog_id, get_random_string, merge_intervals
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.merge'
COMMAND_ID = f'{COMMAND_NAME}>{generate_prog_id()}'
logger = get_logger(COMMAND_NAME)


class TripletMerger:

    def __init__(self, input_patterns, output_dir=None, output_name=None, concatenate_only=False, check_coverage=False, sort_by=None, metadata=None):
        self.concatenate_only = concatenate_only
        self.check_coverage = check_coverage
        self.sort_by = sort_by
        operation_str = 'concatenated' if self.concatenate_only else 'merged'

        # collecting of input files details
        logger.info('Collecting Triplets headers ...')
        self.input_files = []
        for pattern in input_patterns.split(','):
            pattern = str(pathlib.Path(pattern).expanduser())
            for file_path in glob.glob(pattern):
                file = {
                    'pattern': pattern,
                    'path': pathlib.Path(file_path).expanduser(),
                }
                file['header'] = TriplixHeader(file_path=file['path'])
                assert len(file['header'].sort_order) > 0, f'An input file is unsorted: {file["path"]}'
                self.input_files.append(file)
                assert file['header'].column_names == self.input_files[0]['header'].column_names, f'Column order is consistent in: \n{self.input_files[0]["path"]}\n{file["path"]}'
        assert len(self.input_files) > 1, f'Number of input Triplet files should be > 1, only {len(self.input_files)} files are given'

        # sorting input files
        logger.info('Ordering the input files according to their chunks\' chromosomal positions ...')
        self.chrom_order = {chr_name: chr_idx for chr_idx, chr_name in enumerate(self.input_files[0]['header'].chrom_lengths)}
        if self.sort_by == 'chrom':
            self.input_files = sorted(self.input_files, key=lambda inp_file: (self.chrom_order[inp_file['header'].stored_chunks[0][0]], inp_file['header'].stored_chunks[0][1], inp_file['header'].stored_chunks[0][2]))
        logger.info(f'The following {len(self.input_files):d} files will be {operation_str}:')
        for file_idx, file in enumerate(self.input_files):
            logger.info(f'\t#{file_idx + 1:d}: {file["path"]}')

        # prepare output directory and file names
        if output_dir is None:
            output_dir = self.input_files[0]['path'].parent
        if output_name is None:
            output_name = self.input_files[0]['path'].stem.replace('.sorted', '') + f'.{operation_str}' + self.input_files[0]['path'].suffix
        self.output_path = pathlib.Path(output_dir).expanduser() / output_name
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if self.output_path.is_file():
            self.output_path.unlink()

        # use the header from the first file, and update any given meta-data attributes
        self.header = copy.deepcopy(self.input_files[0]['header'])
        for key, value in metadata.items():
            logger.debug(f'Attribute update: {key}={value}')
            setattr(self.header, key, value)

        # adjusting PG:ID headers: making sure these tags are unique
        hash2id = {}
        for input_file in self.input_files:
            prog_suffix = f'_{get_random_string(5)}'
            id_translator = {}
            for prog_name, pg_node in input_file['header'].process_history.programs.items():
                pg_hash = pg_node.hash()
                if pg_hash in hash2id:  # have we seen this PG node before?
                    pg_id = hash2id[pg_hash]
                else:
                    if pg_node['ID'] in hash2id.values():  # can we continue using this id?
                        pg_id = pg_node['ID'] + prog_suffix
                    else:
                        pg_id = pg_node['ID']
                    hash2id[pg_hash] = pg_id
                id_translator[pg_node['ID']] = pg_id

                pg_node['ID'] = id_translator[pg_node['ID']]
                if 'PP' in pg_node:
                    pg_node['PP'] = id_translator[pg_node['PP']]
                pg_node['PS'] = [id_translator[ps_id] for ps_id in pg_node['PS']]

    def merge_triplets(self, n_thread, memory, ignore_headers):
        # assert n_thread > 2, 'Number of threads must be more than 2'

        if self.concatenate_only:
            merge_command = (
                f"/bin/bash -c \"cat "
            )
        else:
            col2num = {col_name: col_idx + 1 for col_idx, col_name in enumerate(self.input_files[0]['header'].column_names)}
            separator = r"\t"
            merge_command = (
                f"/bin/bash -c \"export LC_COLLATE=C; export LANG=C; sort "
                f"-k {col2num['chrom_A']},{col2num['chrom_A']} "
                f"-k {col2num['chrom_B']},{col2num['chrom_B']} "
                f"-k {col2num['chrom_C']},{col2num['chrom_C']} "
                f"-k {col2num['start_A']},{col2num['start_A']}n "
                f"-k {col2num['start_B']},{col2num['start_B']}n "
                f"-k {col2num['start_C']},{col2num['start_C']}n "
                f"--merge "
                f"--field-separator=$'{separator}'  "
                f"--parallel={n_thread:d} "
                f"--temporary-directory=./ "
                f"--buffer-size={memory:s} "
            )

        # add input files as stdin
        for input_file in self.input_files:
            merge_command += (
                # f"<(bgzip --decompress --stdout --threads 1 {input_file['path']} | sed -n -e '/^[^#]/,$p') "
                f"<(bgzip --decompress --stdout --threads 1 {input_file['path'].resolve()} | grep -v '^#') "
            )
        merge_command += f"\""

        # prepare the output file
        # output_file = bgzip.BGZipWriter(self.output_path, 'wt', compresslevel=3)
        # output_file = gzip.open(self.output_path, 'wt', compresslevel=3)
        # pipe_template = pipes.Template()
        # pipe_template.append("bgzip --stdout --threads 1 --compress-level=3", "--")
        # output_file = pipe_template.open(str(self.output_path), "w")

        # combine table chunks and merge the adjacent ones
        stored_chunks = []
        for inp_file in self.input_files:
            stored_chunks.extend(inp_file['header'].stored_chunks)
        self.header.stored_chunks = merge_intervals(stored_chunks, chroms_order=list(self.chrom_order))

        # check if every chromosome is fully covered by chunks
        if self.check_coverage:
            seen_chroms = set()
            for chunk in self.header.stored_chunks:
                chrom_size = self.header.chrom_lengths[chunk[0]]
                assert chunk[0] not in seen_chroms, f'Duplicated chromosomes are found in chunks: {self.header.stored_chunks}'
                assert chunk[1] == 0, f'Missing the start of {chunk[0]}. The smallest chunk starts at {chunk[1]:,d}'
                assert chunk[2] >= chrom_size, f'Missing the end of {chunk[0]} (length={chrom_size:,d}). Current chunk ends at {chunk[2]:,d}'
                seen_chroms.add(chunk[0])
            logger.debug('Coverage test: All chromosomes are fully covered.')
            for chrom in self.header.chrom_lengths:
                if chrom != 'unmapped':
                    assert chrom in seen_chroms, (
                        f'Missing {chrom} in the merged file. \n'
                        f'Only seen the following chromosomes:{seen_chroms}'
                    )
            logger.debug('Coverage test: No missing chromosome is detected.')
            for chrom in seen_chroms:
                assert chrom in self.header.chrom_lengths, (
                    f'An extra chromosome is detected: {chrom}.\n'
                    f'Known chromosomes are:{list(self.header.chrom_lengths)}'
                )
            logger.debug('Coverage test: Every chromosome (stored in the merging files) is known.')

        # preparing compressor process
        compr_command = 'bgzip --stdout --threads 2 --compress-level=3'
        output_file = open(self.output_path, "w")
        compr_proc = subprocess.Popen(compr_command, stdin=subprocess.PIPE, stdout=output_file, bufsize=-1, shell=True)
        compr_input = io.TextIOWrapper(compr_proc.stdin, "utf-8")

        # update and add triplets header
        if ignore_headers:
            # todo: to be removed, when header merger is functional
            logger.info(f'Avoid merging sam headers ...')
            self.header.process_history.programs = {}
            self.header.process_history.source_ids = []
            self.header.process_history.destination_id = None
            merge_pg = dict(
                ID=COMMAND_ID,
                PN=COMMAND_NAME,
                VN=configurations.configs['version'],
                PS=[],
            )
            self.header.process_history.add_pg(merge_pg, is_destination=True)
        else:
            logger.info(f'Merging headers ...')
            headers = [input_file['header'] for input_file in self.input_files]
            self.header.merge_process_histories(headers)
            merge_pg = dict(
                ID=COMMAND_ID,
                PN=COMMAND_NAME,
                VN=configurations.configs['version'],
                PS=[prog['ID'] for prog in self.header.process_history.programs.values() if len(prog.children_ids) == 0],
            )
            self.header.process_history.add_pg(merge_pg, is_destination=True)
        self.header.update(
            creation_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            format_version=TriplixHeader.FORMAT_VERSION,
        )
        compr_input.write(self.header.to_string() + '\n')
        compr_input.flush()
        output_file.flush()
        logger.info(f'The merged header is added to: {self.output_path}')

        # prepare the merge process
        # stdout_wrapper = io.TextIOWrapper(output_file, "utf-8")
        # subprocess.check_call(merge_command, shell=True, stdout=stdout_wrapper)
        # print(merge_command)
        merge_proc = subprocess.Popen(merge_command, stdout=subprocess.PIPE, bufsize=-1, shell=True)
        merge_output = io.TextIOWrapper(merge_proc.stdout, "utf-8")

        # performing the merge
        log_time = 0
        n_trialgn = 0
        operation_str = 'concatenated' if self.concatenate_only else 'merged'
        logger.info(f'Storing {operation_str} tri-alignments in: {self.output_path}')
        for triplet_str in merge_output:
            n_trialgn += 1
            if time.time() - log_time > configurations.configs['log_interval']:
                logger.info(f'\tcurrently at tri-alignment #{n_trialgn:,d}')
                log_time = time.time()
            compr_input.write(triplet_str)
        compr_input.flush()
        merge_proc.communicate()
        compr_proc.communicate()
        output_file.close()
        assert merge_proc.returncode == 0 and compr_proc.returncode == 0, 'Merge process has failed.'

        logger.info(f'In total {n_trialgn:,d} tri-alignments are {operation_str} and stored in: {self.output_path}')


