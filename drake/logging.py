import logging
import logging.config

import yaml


def setup_logging(filename: str = "logging.yml"):
    with open(filename, encoding="utf8") as f:
        cfg = yaml.safe_load(f)
        logging.config.dictConfig(cfg)
