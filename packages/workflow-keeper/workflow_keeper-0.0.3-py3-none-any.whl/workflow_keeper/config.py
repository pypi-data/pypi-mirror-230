import argparse
import dataclasses
import os
import os.path as osp
from typing import Optional, Dict, Any, Tuple, List

import yaml
from loguru import logger
from vyper import Vyper

_HOME = os.path.expanduser('~')
_CONFIG_CONFIG_NAME = "autoTrain"
_CONFIG_PROJECT_NAME = "unifolding"


@dataclasses.dataclass
class Config:
    debug: bool = dataclasses.field(default=False)
    api_host: str = dataclasses.field(default="0.0.0.0")
    api_port: int = dataclasses.field(default=8082)
    workflowsDir: str = dataclasses.field(default="/data")
    logDir: str = dataclasses.field(default="./logs")
    envFile: str = dataclasses.field(default="./env_file")
    remoteEndpoint: str = dataclasses.field(default="")  # set to empty string to disable remote endpoint

    const_db_collection: str = dataclasses.field(default="logs")

    @logger.catch
    def from_dict(self, d: Dict[str, Any]):
        self.debug = d["debug"]
        self.api_host = d["api"]["host"]
        self.api_port = d["api"]["port"]
        self.workflowsDir = d["workflowsDir"]
        self.logDir = d["logDir"]
        self.envFile = d["envFile"]
        self.remoteEndpoint = d["remoteEndpoint"]
        return self

    @logger.catch
    def from_vyper(self, v: Vyper):
        self.debug = v.get_bool("debug")
        self.api_host = v.get_string("api.host")
        self.api_port = v.get_int("api.port")
        self.workflowsDir = v.get_string("workflowsDir")
        self.logDir = v.get_string("logDir")
        self.envFile = v.get_string("envFile")
        self.remoteEndpoint = v.get_string("remoteEndpoint")

        return self

    def to_dict(self):
        return {
            "debug": self.debug,
            "api": {
                "host": self.api_host,
                "port": self.api_port,
            },
            "workflowsDir": self.workflowsDir,
            "logDir": self.logDir,
            "envFile": self.envFile,
            "remoteEndpoint": self.remoteEndpoint,
        }


def get_default_config() -> Vyper:
    """
    service:
      debug: false
      api:
        port: 8080
        host: '0.0.0.0'
      workflowsDir: /data
      logDir: ./logs
      envFile: ./env_file
      remoteEndpoint: http://localhost:8080
    """
    v = Vyper()
    _DEFAULT = Config()
    v.set_default("debug", _DEFAULT.debug)
    v.set_default("api.host", _DEFAULT.api_host)
    v.set_default("api.port", _DEFAULT.api_port)
    v.set_default("workflowsDir", _DEFAULT.workflowsDir)
    v.set_default("logDir", _DEFAULT.logDir)
    v.set_default("envFile", _DEFAULT.envFile)
    v.set_default("remoteEndpoint", _DEFAULT.remoteEndpoint)

    return v


def get_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", type=bool, help="debug mode")
    parser.add_argument("--config", type=str, help="config file path", default=None)
    parser.add_argument("--api.host", type=str, help="api host")
    parser.add_argument("--api.port", type=int, help="api port")
    parser.add_argument("--workflowsDir", type=str, help="workflows dir")
    parser.add_argument("--logDir", type=str, help="log dir")
    parser.add_argument("--envFile", type=str, help="env file")
    parser.add_argument("--remoteEndpoint", type=str, help="remote endpoint")
    return parser


def load_config(argv: List[str]) -> Tuple[Vyper, Optional[Exception]]:
    parser = get_cli_parser()
    args = parser.parse_args(argv)

    v = get_default_config()
    v.set_config_name(_CONFIG_CONFIG_NAME)
    v.set_config_type("yaml")
    v.add_config_path(f"/etc/{_CONFIG_PROJECT_NAME}")
    v.add_config_path(osp.join(_HOME, f".{_CONFIG_PROJECT_NAME}"))
    v.add_config_path(".")
    if args.config is not None:
        v.set_config_file(args.config)
    try:
        v.merge_in_config()
        logger.debug(f"load config form : {v._config_file}")
    except FileNotFoundError:
        v = get_default_config()
        logger.warning(f"config file not found")

    v.set_env_prefix(_CONFIG_PROJECT_NAME.upper())
    v.set_env_key_replacer(".", "_")

    v.bind_args(vars(args))
    v.bind_env("debug")
    v.bind_env("api.host")
    v.bind_env("api.port")
    v.bind_env("workflowsDir")
    v.bind_env("logDir")
    v.bind_env("envFile")
    v.bind_env("remoteEndpoint")

    logger.debug(f"config: {Config().from_vyper(v).to_dict()}")

    return v, None


def save_config(v: Vyper, path: str = None) -> Optional[Exception]:
    if path is None:
        path = osp.join(_HOME, f".{_CONFIG_PROJECT_NAME}", f"{_CONFIG_CONFIG_NAME}.yaml")

    _DIR = osp.dirname(path)
    if not osp.exists(_DIR):
        os.makedirs(_DIR, exist_ok=True)

    _VALUE = Config().from_vyper(v).to_dict()

    logger.debug(f"save path: {path}")
    logger.debug(f"save config: {_VALUE}")

    with open(path, "w") as f:
        yaml.dump(_VALUE, f, default_flow_style=False)

    return None
