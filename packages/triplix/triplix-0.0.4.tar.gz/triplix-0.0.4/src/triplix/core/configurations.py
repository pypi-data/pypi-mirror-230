
from importlib import resources, metadata
import pathlib
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

configs = {}


def load_config(config_path: str = None) -> None:
    global configs

    triplix_path = pathlib.Path(__file__).parent
    # if config_path is None:
    #     config_path = triplix_path / 'config.toml'

    if config_path is None:
        with resources.files('triplix').joinpath('config.toml').open('rb') as config_file:
            configs = tomllib.load(config_file)
        configs['version'] = metadata.version('triplix')
        configs['triplix_path'] = triplix_path
        if configs['debug']:
            print('Configs are being loaded.')
