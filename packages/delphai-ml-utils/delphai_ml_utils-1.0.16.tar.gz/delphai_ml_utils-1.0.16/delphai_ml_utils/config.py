import logging
import os
from base64 import b64decode
from time import sleep

from dotenv import load_dotenv
from omegaconf import OmegaConf
from memoization import cached

logger = logging.getLogger(__name__)


env_path = os.path.abspath(".env")
load_dotenv(dotenv_path=env_path)

CURRENT_CONFIG = None
CONFIG_IS_LOADING = False


def __load_config(config_dir: str = "./config"):
    global CURRENT_CONFIG, CONFIG_IS_LOADING
    while CONFIG_IS_LOADING:
        sleep(0.05)
    if CURRENT_CONFIG is not None:
        return CURRENT_CONFIG
    while CONFIG_IS_LOADING:
        sleep(0.05)
    CONFIG_IS_LOADING = True
    try:
        if "DELPHAI_ENVIRONMENT" not in os.environ:
            raise Exception("DELPHAI_ENVIRONMENT is not defined")
        default_config = OmegaConf.load(f"{config_dir}/default.yml")
        delphai_environment = os.environ.get("DELPHAI_ENVIRONMENT")
        if os.path.isfile(f"{config_dir}/{delphai_environment}.yml"):
            delphai_env_config = OmegaConf.load(
                f"{config_dir}/{delphai_environment}.yml"
            )
        else:
            delphai_env_config = OmegaConf.create()
        CURRENT_CONFIG = OmegaConf.merge(default_config, delphai_env_config)
        OmegaConf.set_readonly(CURRENT_CONFIG, True)
        return CURRENT_CONFIG
    finally:
        CONFIG_IS_LOADING = False


@cached
def get_config(path: str = "", config_dir: str = "./config"):
    config = __load_config(config_dir=config_dir)
    if path is None:
        return config
    selected = OmegaConf.select(config, path)
    if OmegaConf.is_config(selected):
        return OmegaConf.to_container(selected, resolve=True)
    else:
        return selected
