
import time
import logging


from triplix.core import cli
from triplix.core import configurations
from triplix import _logging

logger = _logging.get_logger('triplix')


def main():

    """Main function of Triplix"""
    ctime = time.time()

    # processing CLI input arguments
    cli_parser = cli.define_cli_arguments()
    cli_args = cli_parser.parse_args()

    # activate debug mode, if requested
    configurations.configs['debug'] = cli_args.debug
    if configurations.configs['debug']:
        for logger_name in _logging._loggers:
            _logging._loggers[logger_name].setLevel(logging.DEBUG)
        logger.debug('Debug mode is now active.')

    if cli_args.command is None:
        logger.error('No command is specified. See below for available commands.')
        cli_parser.print_help(file=sys.stderr)
        exit(1)
    cli_args.func(cli_args)
    # print(cli_args)
    
    if configurations.configs['debug']:
        print(f'Program ended. It took {time.time() - ctime:0.4f}s')


if __name__ == "__main__":
    main()
