import logging
import logging.config
import yaml
from os.path import exists
from pathlib import Path


def get_logger(logger_name='airflow_plugins'):
    """
    create logger as per the config present in file - ../resources/log_config.yaml
    """
    config_file_path = Path(__file__).parent.parent/'resources/log_config.yaml'
    if exists(config_file_path):
        with open(config_file_path, 'r') as f:
            log_cfg = yaml.safe_load(f.read())

        logging.config.dictConfig(log_cfg)
        logger = logging.getLogger(logger_name)
        return logger
    else:
        raise ValueError('logger config file not found')
