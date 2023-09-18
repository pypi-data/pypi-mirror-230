

import pathlib
import subprocess

from triplix._logging import get_logger

COMMAND_NAME = 'triplix.index'
logger = get_logger(COMMAND_NAME)


class TripletIndexer:
    def __init__(self, triplet_path):
        self.triplet_path = pathlib.Path(triplet_path).expanduser().resolve()
        assert self.triplet_path.is_file(), f'File not found: {self.triplet_path}'

    def index(self):
        logger.info(f'Indexing tri-alignment container: {self.triplet_path}')

        # pairix options (v0.3.7):
        #          -s INT     sequence name column [1]
        #          -d INT     second sequence name column [null]
        #          -b INT     start1 column [4]
        #          -e INT     end1 column; can be identical to '-b' [5]
        #          -u INT     start2 column [null]
        #          -v INT     end2 column; can be identical to '-u' [null or identical to the start2 specified by -u]
        index_command = (
            f"/bin/bash -c \"pairix -s1 -d4 -b2 -e3 -u5 -v6 "
            f"{self.triplet_path} "
            f"\""
        )
        logger.debug(f'Executing: {index_command}')
        subprocess.check_call(index_command, shell=True)
        logger.info(f'Index generation is finished successfully.')
