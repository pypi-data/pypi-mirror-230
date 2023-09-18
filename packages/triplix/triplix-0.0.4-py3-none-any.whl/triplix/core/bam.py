import copy
import pathlib
from dataclasses import dataclass

import pysam


@dataclass
class Alignment:
    chrom: str = None
    start: int = -1
    end: int = -1
    strand: str = None
    map_quality: int = -1
    flag: int = -1
    seq_start: int = -1
    seq_end: int = -1
    read_idx: int = -1
    read_name: str = None
    read_length: int = -1
    # cigar: str = None
    pysam_alignment: pysam.AlignedSegment = None


class BAMReader:
    def __init__(self, file_path):
        path_obj = pathlib.Path(file_path).expanduser()
        assert path_obj.is_file(), f'File not found: {file_path}'
        self.file_path = file_path
        _verbosity_level = pysam.set_verbosity(0)
        self.file_handle = pysam.AlignmentFile(path_obj, 'r')
        pysam.set_verbosity(_verbosity_level)
        self.chroms = [chrom['SN'] for chrom in self.file_handle.header['SQ']]
        self.chrom_sizes = [chrom['LN'] for chrom in self.file_handle.header['SQ']]

    def get_reads(self, return_pysam_object=False):
        read_idx = 0
        alignments = []
        for aln_idx, aln in enumerate(self.file_handle):

            alignment = Alignment(
                chrom=aln.reference_name,
                start=aln.reference_start,
                end=aln.reference_end,
                strand='-' if aln.is_reverse else '+',
                map_quality=aln.mapping_quality,
                flag=aln.flag,
                read_idx=read_idx,
                read_name=aln.query_name,
                read_length=aln.infer_read_length(),
                # cigar=aln.cigarstring,
            )

            # infer the alignment position over read
            # PySam regular functions wont work: https://github.com/pysam-developers/pysam/issues/903#issuecomment-1240695780
            # S	BAM_CSOFT_CLIP	4
            # H	BAM_CHARD_CLIP	5
            skip_start = aln.cigartuples[0][1] if aln.cigartuples[0][0] in [4, 5] else 0
            skip_end = aln.cigartuples[-1][1] if aln.cigartuples[-1][0] in [4, 5] else 0
            if aln.is_reverse:
                alignment.seq_start = skip_end
                alignment.seq_end = alignment.read_length - skip_start
            else:
                alignment.seq_start = skip_start
                alignment.seq_end = alignment.read_length - skip_end

            if return_pysam_object:
                alignment.pysam_alignment = copy.deepcopy(aln)

            # check if the current alignment should be appended
            if len(alignments) == 0 or alignments[0].read_name == alignment.read_name:
                alignments.append(alignment)
            else:
                yield alignments
                read_idx += 1
                alignment.read_idx = read_idx
                alignments = [alignment]
        yield alignments

    # def get_alignments(self, chrom=None, start=None, end=None, return_pysam_object=False):
    #     if chrom is None:
    #         alignments_iter = self.file_handle
    #     else:
    #         alignments_iter = self.file_handle.fetch(contig=chrom, start=start, end=end)

