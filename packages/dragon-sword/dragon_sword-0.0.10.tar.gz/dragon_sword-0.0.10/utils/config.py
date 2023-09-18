import os
from dataclasses import dataclass
import yaml

from utils.errno import Error, OK, MISS_CONFIG, BROKEN_CONFIG
from utils.log import logger

# 全局配置，不要直接使用。
_GLOBAL_CONFIG: dict
_ConfigPath: str
_RUNNING_KEY: str = "__tool_running_conf__"


@dataclass
class RunningConf:
    log_f_prefix: str


def get_global_config() -> dict:
    name = "_GLOBAL_CONFIG"
    if name not in locals() and name not in globals():
        return {}
    return _GLOBAL_CONFIG


def get_config_path() -> str:
    return _ConfigPath


def init_global_conf(conf):
    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG = conf


def init_conf(config_path: str, log_f_prefix: str) -> Error:
    """
    初始化全局配置
    kwargs:
        server_id:
    """
    global _ConfigPath
    _ConfigPath = os.path.abspath(config_path)
    if not os.path.exists(_ConfigPath):
        return MISS_CONFIG

    with open(_ConfigPath, "r", encoding="utf-8") as f:
        try:
            err = OK
            conf = yaml.safe_load(f)
        except yaml.YAMLError:
            print(f"init_conf get broken yaml")
            err = BROKEN_CONFIG
            return err
    init_global_conf(conf)

    global _GLOBAL_CONFIG
    _GLOBAL_CONFIG[_RUNNING_KEY] = RunningConf(
        log_f_prefix=log_f_prefix,
    )
    return err


def get_running_conf() -> RunningConf:
    return _GLOBAL_CONFIG[_RUNNING_KEY]


def get_conf(key: str) -> dict:
    """
    获取配置文件中的一级项，不要直接使用。用model.config中的方法
    :param key:
    :return:
    """
    item = get_global_config().get(key, {})
    if not item:
        logger.error(f"get_conf no {key}, check your config, or will use default config")
        return {}
    return item


def log_conf() -> list[dict]:
    """
    获取日志配置
    :return:
    """
    return get_global_config().get("log", [])


def user_service_name() -> str:
    return "user"


def set_default(value, obj, field, default):
    if not value:
        setattr(obj, field, default)
    else:
        logger.info(f"{obj.__class__.__name__} {field} use default {default}")
        setattr(obj, field, value)


def get_default(config: dict, name: str, default):
    value = config.get(name)
    if not value:
        logger.info(f"no {name} use default {default}")
        return default
    else:
        return value
