import glob
import io
import os
import os.path as osp
import re
import time
from typing import Optional, Tuple, Dict, Any

import yaml
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

from workflow_keeper.datamodels import Job, Workflow


def search_workflows(base_dir: str) -> Dict[str, str]:
    """
    search for yaml files in base_dir, return a dict of {name: path}
    """
    path_yaml = glob.glob(osp.join(base_dir, "*.yaml"))
    path_yml = glob.glob(osp.join(base_dir, "*.yml"))
    items_yaml = {
        osp.splitext(osp.basename(x))[0]: x for x in path_yaml
    }
    items_yml = {
        osp.splitext(osp.basename(x))[0]: x for x in path_yml
    }

    items = dict(**items_yaml, **items_yml)
    return items


def get_workflow_path(base_dir: str, workflow_name: str) -> Optional[str]:
    """
    get workflow path from base_dir + workflow_name, return None if not found
    """
    if osp.exists(osp.join(base_dir, workflow_name + ".yaml")):
        return osp.join(base_dir, workflow_name + ".yaml")
    elif osp.exists(osp.join(base_dir, workflow_name + ".yml")):
        return osp.join(base_dir, workflow_name + ".yml")
    else:
        return None


def parse_yaml_workflow(
        path: str,
        kv: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[Workflow], Optional[Exception]]:
    with open(path, "r") as f:
        template_str = f.read()

    if kv is None:
        kv = {}

    def replace(match):
        key = match.group(1)
        if key not in kv.keys():
            logger.debug(f"key {key} not found in params, searching env")
            if key not in os.environ.keys():
                logger.warning(f"key {key} not found in env, using empty string as default")
            value = os.environ.get(key, default='')
            kv[key] = value  # cache the value

        else:
            value = str(kv.get(key, ''))
        return value  # 使用 kv 字典中的值替换

    pattern = r'\$\{\{\s*(\w+)\s*\}\}'  # 匹配 ${{ key }}
    template_str = re.sub(pattern, replace, template_str)

    try:
        workflow = yaml.safe_load(io.StringIO(template_str))
    except Exception as e:
        logger.exception(e)
        return None, e

    if "name" not in workflow.keys():
        return None, Exception("missing 'name' attribute in yaml file")

    if "jobs" not in workflow.keys():
        return None, Exception("no jobs found in yaml file")

    try:
        res = []
        for job_name, job in workflow["jobs"].items():
            res.append(Job(name=job_name, steps=job["steps"]))

    except Exception as e:
        logger.exception(e)
        return None, e

    name = workflow["name"]
    concurrency = workflow.get("concurrency", False)
    schedule = workflow.get("schedule", None)
    host = workflow.get("host", None)

    try:
        return Workflow(name=name, concurrency=concurrency, jobs=res, schedule=schedule, host=host), None
    except Exception as e:
        logger.exception(e)
        return None, e


def make_response(status_code, **kwargs):
    data = {'code': status_code, 'timestamp': time.time()}
    data.update(**kwargs)
    json_compatible_data = jsonable_encoder(data)
    resp = JSONResponse(content=json_compatible_data, status_code=status_code)
    return resp
