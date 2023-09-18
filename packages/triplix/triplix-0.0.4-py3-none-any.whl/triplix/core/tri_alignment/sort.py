

import io
import gzip
import time
import pathlib
import subprocess

from triplix.core.header import TriplixHeader
from triplix.core import configurations
from triplix.core.utilities import generate_prog_id
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.sort'
COMMAND_ID = f'{COMMAND_NAME}>{generate_prog_id()}'
logger = get_logger(COMMAND_NAME)


class TriAlignmentSorter:
    def __init__(self, trialign_path, output_dir=None, output_name=None):
        self.trialign_path = pathlib.Path(trialign_path).expanduser()
        self.header = TriplixHeader(file_path=trialign_path)

        if output_dir is None:
            output_dir = self.trialign_path.parent
        if output_name is None:
            output_name = self.trialign_path.stem + '.sorted.tri-alignments.tsv.bgz'
        self.output_path = pathlib.Path(output_dir).expanduser() / output_name
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if self.output_path.is_file():
            self.output_path.unlink()

    def sort_tri_alignments(self, n_thread, memory):
        col2num = {col_name: col_idx + 1 for col_idx, col_name in enumerate(self.header.column_names)}

        separator = r"\t"
        sort_command = (
            f"/bin/bash -c \"export LC_COLLATE=C; export LANG=C; sort "
            f"-k {col2num['chrom_A']},{col2num['chrom_A']} "
            f"-k {col2num['chrom_B']},{col2num['chrom_B']} "
            f"-k {col2num['chrom_C']},{col2num['chrom_C']} "
            f"-k {col2num['start_A']},{col2num['start_A']}n "
            f"-k {col2num['start_B']},{col2num['start_B']}n "
            f"-k {col2num['start_C']},{col2num['start_C']}n "
            f"--stable "
            f"--field-separator=$'{separator}'  "
            f"--parallel={n_thread:d} "
            f"--temporary-directory=./ "
            f"--buffer-size={memory:s}"
            f"\""
        )

        # ignoring header lines
        input_file = gzip.open(self.trialign_path, 'rt')
        for line in input_file:
            if line.startswith('#column names:'):
                break

        # prepare the output file
        output_file = gzip.open(self.output_path, 'wt', compresslevel=3)

        # add Tri-alignment header
        self.header.update(
            creation_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            format_version=TriplixHeader.FORMAT_VERSION,
            sort_order=['chrom_A', 'chrom_B', 'chrom_C', 'start_A', 'start_B', 'start_C'],
        )
        self.header.process_history.add_pg(dict(ID=COMMAND_ID, PN=COMMAND_NAME, VN=configurations.configs['version'], PS=[self.header.process_history.destination_id]))
        output_file.write(self.header.to_string() + '\n')
        output_file.flush()

        # performing the sort
        logger.info(f'Reading tri-alignments from: {self.trialign_path}')
        logger.log_time = time.time()
        with subprocess.Popen(sort_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=-1, shell=True) as sort_process:
            stdin_wrapper = io.TextIOWrapper(sort_process.stdin, "utf-8")
            # shutil.copyfileobj(input_file, stdin_wrapper)
            n_tri_algn = 0
            for line in input_file:
                # if line_idx % 500e3 == 0:
                n_tri_algn += 1
                if time.time() - logger.log_time > configurations.configs['log_interval']:
                    logger.log_time = time.time()
                    logger.info(f'\tcurrently at tri-alignments #{n_tri_algn:,d}')
                stdin_wrapper.write(line)
            stdin_wrapper.flush()
            sort_process.stdin.close()

            logger.info(f'Sorting {n_tri_algn:,d} tri-alignments ...')

            logger.info(f'Writing sorted tri-alignments to: {self.output_path}')
            stdout_wrapper = io.TextIOWrapper(sort_process.stdout, "utf-8")
            logger.log_time = time.time()
            for line_idx, line in enumerate(stdout_wrapper):
                # if line_idx % 500e3 == 0:
                if time.time() - logger.log_time > configurations.configs['log_interval']:
                    logger.log_time = time.time()
                    logger.info(f'\tcurrently at tri-alignments #{line_idx:,d}')
                output_file.write(line)

        assert sort_process.returncode == 0, 'Sort process has failed.'

        input_file.close()
        output_file.close()
