from logging.config import dictConfig
from os import path

from yaml import safe_load

script_dir = path.dirname(__file__)
with open(path.join(script_dir, 'logging_conf.yml')) as file:
    loaded_config = safe_load(file)
    dictConfig(loaded_config)
