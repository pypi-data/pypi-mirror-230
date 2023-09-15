import logging
import os

import appdirs
import yaml

from komora_syncer import __appname__

logger = logging.getLogger(__name__)

os.environ["XDG_CONFIG_DIRS"] = "/etc"
CONFIG_DIRS = (
    appdirs.user_config_dir(__appname__),
    appdirs.site_config_dir(__appname__),
)
CONFIG_FILENAME = "config.yml"

def get_config():
    """
    Get config file and load it with yaml
    :returns: loaded config in yaml, as a dict object
    """
    
    if getattr(get_config, "cache", None):
        return get_config.cache

    if os.environ.get("CONFIG_FOLDER_PATH"):
        config_path = os.path.join(os.environ.get("CONFIG_FOLDER_PATH"), CONFIG_FILENAME)
    else:
        for d in CONFIG_DIRS:
            config_path = os.path.join(d, CONFIG_FILENAME)
            if os.path.isfile(config_path):
                break
        else:
            logger.error(
                "No configuration file can be found. Please create a "
                "config.yml in one of these directories:\n"
                "{}".format(", ".join(CONFIG_DIRS))
            )
            exit(0)

    try:
        with open(config_path, "r") as config_file:
            conf = yaml.safe_load(config_file)
            get_config.cache = conf
            return conf
    except FileNotFoundError as e:
        logger.error(e)
        exit(0)


def setup_logger():
    logging_config = get_config().get("logging", {})
    level = logging_config.get('LOG_LEVEL', 'DEBUG')
    disable_existing_loggers = logging_config.get('DISABLE_EXISTING_LOGGERS', False)
    formatting = logging_config.get('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')

    # create logger
    logger = logging.getLogger(__appname__)
    logger.setLevel(level)

    # create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter(formatting)

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    if disable_existing_loggers:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

