import os
import sys
from typing import Optional, Tuple

from loguru import logger

from workflow_keeper.controller import serve_forever
from workflow_keeper.config import Config
from workflow_keeper.datamodels import Context


@logger.catch
def prepare_run(opt: Config) -> Tuple[Optional[Context], Optional[Exception]]:
    if not opt.debug:
        logger.info("running in production mode")
        # disable debug logging
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    if not os.path.exists(opt.workflowsDir):
        logger.error(f"workflowsDir not exists: {opt.workflowsDir}")
        return None, Exception(f"workflowsDir not exists: {opt.workflowsDir}")

    if not os.path.exists(opt.logDir):
        logger.error(f"jobsDir not exists: {opt.logDir}")
        os.makedirs(opt.logDir, exist_ok=True)

    if os.path.exists(opt.envFile):
        # populate env
        logger.info(f"loading env from file: {opt.envFile}")
        with open(opt.envFile, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line == "" or line.startswith("#"):
                    continue
                key, value = line.split("=")
                os.environ[key] = value

    return Context(opt=opt), None


def run(opt: Config):
    logger.info(f"start backend thread")

    context, err = prepare_run(opt)
    if err is not None:
        return err

    serve_forever(context_in=context, port=opt.api_port, host=opt.api_host)
