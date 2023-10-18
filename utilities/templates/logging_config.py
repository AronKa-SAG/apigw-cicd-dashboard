import logging.config
import yaml
import os

config_file = 'configuration/log_config.yaml'

if os.path.exists(config_file):
    with open(config_file, 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
