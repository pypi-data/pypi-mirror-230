import time
from typing import Optional, List, Union, Dict, Any

import croniter
from loguru import logger
from pydantic import BaseModel, validator

from workflow_keeper.config import Config


class JobStep(BaseModel):
    name: str
    uses: Optional[str]
    env: Optional[List[str]] = None
    run: Union[str, List[str]]
    params: Optional[dict] = None

    @validator("uses")
    def check_uses(cls, v):
        assert v in [None, "shell", "ssh", "docker"]
        return v

    @validator("run")
    def check_run(cls, v):
        if isinstance(v, list):
            v = '\n'.join(v)
        if v is None or v == "":
            raise ValueError("cannot be empty string")
        return v


class Job(BaseModel):
    name: str
    steps: List[JobStep]

    @validator("steps")
    def check_uses(cls, v):
        assert isinstance(v, list)
        for index in range(len(v)):
            if not isinstance(v[index], JobStep):
                v[index] = JobStep(**v[index])
        return v


class Workflow(BaseModel):
    name: str
    concurrency: bool = False
    jobs: List[Job]
    schedule: Optional[str] = None
    host: Optional[str] = None

    @validator("name")
    def check_name(cls, v):
        v = str(v)
        return v

    @validator("concurrency")
    def check_concurrency(cls, v):
        if not isinstance(v, bool):
            v = bool(v)
        return v

    @validator("jobs")
    def check_jobs(cls, v):
        if not isinstance(v, list):
            v = list(v)
        for index in range(len(v)):
            if not isinstance(v[index], Job):
                v[index] = Job(**v[index])
        return v

    @validator("schedule")
    def check_schedule(cls, v):
        """
        check if the schedule is valid cron expression
        """
        if v is not None:
            try:
                croniter.croniter(str(v))
                return str(v)
            except Exception as e:
                logger.error(f"invalid cron expression: {v}")
                return None
        else:
            return v


class Context(BaseModel):
    opt: Config
    scheduler: Optional[Any] = None
    scheduler_lock: Optional[Any] = None


class HeartbeatRequest(BaseModel):
    type: str = "HeartbeatRequest"


class HeartbeatResponse(BaseModel):
    msg: str = "pong"


class Response(BaseModel):
    code: int = 200
    timestamp: Optional[float] = None
    msg: str = ""

    @validator("timestamp")
    def check_timestamp(cls, v):
        if v is None:
            v = time.time()
        return float(v)


class ListWorkflowsRequest(BaseModel):
    type: str = "ListWorkflowsRequest"


class ListWorkflowsResponse(Response):
    workflows: Optional[List[str]] = None


class TriggerWorkflowRequest(BaseModel):
    type: str = "TriggerWorkflowRequest"
    workflow: Optional[Dict[str, Any]] = None


class TriggerWorkflowResponse(Response):
    job_id: Optional[str] = None


class GetJobResultRequest(BaseModel):
    type: str = "GetJobResultRequest"
    job_id: str


class GetJobResultResponse(Response):
    result: Optional[Dict[str, Any]] = None


class CancelJobRequest(BaseModel):
    type: str = "CancelJobRequest"
    job_id: str


class CancelJobResponse(Response):
    pass


class ListJobsRequest(BaseModel):
    type: str = "ListJobsRequest"


class ListJobsResponse(Response):
    jobs: Optional[List[str]] = None


class ListWorkersResponse(Response):
    workers: Optional[List[str]] = None
