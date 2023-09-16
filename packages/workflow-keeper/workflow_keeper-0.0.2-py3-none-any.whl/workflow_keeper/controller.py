import asyncio
import json
import os
import os.path as osp
import socket
import threading
import time
from typing import Optional, Dict, Any

from uvicorn import Config, Server
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse, StreamingResponse, HTMLResponse
from loguru import logger
from starlette.websockets import WebSocketState
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from websockets.sync.client import connect

from workflow_keeper.components import RunnerManager, WorkerManager
from workflow_keeper.datamodels import (
    Context, Response,
    ListWorkflowsResponse, TriggerWorkflowRequest, TriggerWorkflowResponse,
    GetJobResultRequest, GetJobResultResponse, CancelJobRequest, CancelJobResponse, ListJobsRequest, ListJobsResponse,
    ListWorkersResponse, HeartbeatResponse, Workflow
)
from workflow_keeper.utils import parse_yaml_workflow, search_workflows, get_workflow_path

controller = FastAPI()
context: Optional[Context] = None

runner_manager: Optional[RunnerManager] = None
worker_manager: Optional[WorkerManager] = None


@controller.get("/")
def root():
    return RedirectResponse(url='/docs')


@controller.get("/v1/workflows", response_model=ListWorkflowsResponse)
async def list_workflows():
    """
    List all workflows
    """
    global context
    try:
        workflow_paths = search_workflows(context.opt.workflowsDir)
        return ListWorkflowsResponse(code=200, msg="success", workflows=workflow_paths.items())
    except Exception as e:
        return ListWorkflowsResponse(code=500, msg=str(e))


@controller.post("/v1/workflows", response_model=TriggerWorkflowResponse)
async def trigger_workflow_raw(workflow_raw: Dict[str, Any]):
    """
    Trigger a workflow with workflow as payload
    """
    global context, runner_manager

    # trigger workflow
    try:
        workflow = Workflow(**workflow_raw)
        job_id, err = runner_manager.trigger(workflow)
        if err is not None:
            return TriggerWorkflowResponse(code=500, msg=str(err))
        else:
            return TriggerWorkflowResponse(code=200, msg=f"workflow triggered", job_id=job_id)
    except Exception as e:
        return TriggerWorkflowResponse(code=500, msg=str(e))


@controller.post("/v1/workflows/{workflow_name}", response_model=TriggerWorkflowResponse)
async def trigger_workflow(workflow_name: str, params: Dict[str, Any] = None):
    """
    Trigger a workflow and create a job, if the workflow has host specified, it will be triggered on remote host
    """
    global context, runner_manager
    # check if workflow exists
    workflow_path = get_workflow_path(context.opt.workflowsDir, workflow_name)
    if workflow_path is None:
        return TriggerWorkflowResponse(code=404, msg=f"workflow not found: {workflow_name}")

    # parse workflow and render
    workflow, err = parse_yaml_workflow(workflow_path, params)
    if err is not None:
        return TriggerWorkflowResponse(code=500, msg=str(err))

    # trigger workflow
    try:
        if workflow.host is None or workflow.host == "localhost":
            job_id, err = runner_manager.trigger(workflow)
        else:
            # trigger workflow on remote host
            result = await proxy_trigger_workflow(workflow.host, workflow_name, params)
            job_id, err = result.job_id, Exception(result.msg) if result.code != 200 else None
        if err is not None:
            logger.warning(f"failed to trigger workflow {workflow_name}: {err}")
            return TriggerWorkflowResponse(code=500, msg=str(err))
        else:
            logger.info(f"workflow {workflow_name} triggered on {workflow.host if workflow.host else 'localhost'}")
            return TriggerWorkflowResponse(code=200, msg=f"workflow {workflow_name} triggered", job_id=job_id)
    except Exception as e:
        logger.error(f"failed to trigger workflow {workflow_name}: {e}")
        return TriggerWorkflowResponse(code=500, msg=str(e))


@controller.get("/v1/logs/{job_id}")
def get_job_log(job_id: str):
    """
    Get job log if a job is created
    """
    global context

    log_path = osp.join(context.opt.logDir, f"{job_id}.log")

    def iterfile():  # (1)
        with open(log_path, mode="rb") as file_like:  # (2)
            yield from file_like

    if not osp.exists(log_path):
        return HTMLResponse(content=f"<h1>log not found: {job_id}</h1>", status_code=404)
    else:
        return StreamingResponse(iterfile(), media_type="text/plain")


@controller.get("/v1/jobs/{job_id}", response_model=GetJobResultResponse)
async def get_job_result(job_id: str):
    """
    Get job result (std, err, etc.) if a job is finished
    """
    global context, runner_manager

    # check if job exists
    job_result, err = runner_manager.get_job(job_id)
    if err is not None:
        return GetJobResultResponse(code=500, msg=str(err))

    # check if job finished
    if job_result is None:
        return GetJobResultResponse(code=500, msg=f"job {job_id} not finished")
    else:
        return GetJobResultResponse(code=200, msg=f"job {job_id} finished", result=job_result)


@controller.delete("/v1/jobs/{job_id}", response_model=CancelJobResponse)
async def cancel_job(job_id: str):
    """
    Cancel a job, if the job is running, it will be force killed
    """
    global context, runner_manager

    # just cancel the job
    err = runner_manager.cancel_job(job_id)
    if err is not None:
        return CancelJobResponse(code=500, msg=str(err))
    else:
        return CancelJobResponse(code=200, msg=f"job {job_id} canceled")


@controller.get("/v1/jobs", response_model=ListJobsResponse)
async def list_jobs():
    """
    List all jobs
    """
    global context, runner_manager
    return ListJobsResponse(code=200, jobs=runner_manager.jobs)


@controller.websocket("/v1/register/{client_id}")
async def register(websocket: WebSocket, client_id: str):
    """
    Register a worker
    """
    global worker_manager
    success = await worker_manager.connect(client_id, websocket)
    if not success:
        return
    try:
        while True:
            ret = await worker_manager.heartbeat(client_id)
            if ret is not None:
                logger.warning(f"heartbeat failed: {ret}")
                break
            if websocket.client_state != WebSocketState.CONNECTED:
                break
            else:
                await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

    logger.info(f"client #{client_id} disconnected")
    worker_manager.disconnect(client_id)


@controller.get("/v1/workers", response_model=ListWorkersResponse)
async def list_workers():
    """
    List all connected workers
    """
    global worker_manager
    return ListWorkersResponse(code=200, workers=worker_manager.clients)


@controller.post("/v1/proxy/{client_id}/workflows/{workflow_name}", response_model=TriggerWorkflowResponse)
async def proxy_trigger_workflow(client_id: str, workflow_name: str, params: Dict[str, Any] = None):
    """
    Proxy trigger workflow to client, workflow is read from localfile and trigger on client
    """
    global context, worker_manager

    # check if workflow exists
    workflow_path = get_workflow_path(context.opt.workflowsDir, workflow_name)
    if workflow_path is None:
        return TriggerWorkflowResponse(code=404, msg=f"workflow not found: {workflow_name}")

    # parse workflow and render
    workflow, err = parse_yaml_workflow(workflow_path, params)
    if err is not None:
        return TriggerWorkflowResponse(code=500, msg=str(err))

    req = TriggerWorkflowRequest(
        workflow=workflow.dict()
    )
    if client_id not in worker_manager.clients:
        return TriggerWorkflowResponse(code=404, msg=f"client not found: {client_id}")
    else:
        res, err = await worker_manager.send_recv_individual(req.dict(), client_id)
        if err is not None:
            return TriggerWorkflowResponse(code=500, msg=str(err))
        else:
            return TriggerWorkflowResponse(**res)


@controller.get("/v1/proxy/{client_id}/jobs/{job_id}", response_model=GetJobResultResponse)
async def proxy_get_job_result(client_id: str, job_id: str):
    """
    Proxy get job result to client
    """
    global context, worker_manager
    req = GetJobResultRequest(
        job_id=job_id
    )
    if client_id not in worker_manager.clients:
        return GetJobResultResponse(code=404, msg=f"client not found: {client_id}")
    else:
        res, err = await worker_manager.send_recv_individual(req.dict(), client_id)
        if err is not None:
            return GetJobResultResponse(code=500, msg=str(err))
        else:
            return GetJobResultResponse(**res)


@controller.delete("/v1/proxy/{client_id}/jobs/{job_id}", response_model=CancelJobResponse)
async def proxy_cancel_job(client_id: str, job_id: str):
    """
    Proxy cancel job to client
    """
    global context, worker_manager
    req = CancelJobRequest(
        job_id=job_id
    )
    if client_id not in worker_manager.clients:
        return CancelJobResponse(code=404, msg=f"client not found: {client_id}")
    else:
        res, err = await worker_manager.send_recv_individual(req.dict(), client_id)
        if err is not None:
            return CancelJobResponse(code=500, msg=str(err))
        else:
            return CancelJobResponse(**res)


@controller.get("/v1/proxy/{client_id}/jobs", response_model=ListJobsResponse)
async def proxy_list_jobs(client_id: str):
    """
    Proxy list jobs to client
    """
    global context, worker_manager
    req = ListJobsRequest()
    if client_id not in worker_manager.clients:
        return ListJobsResponse(code=404, msg=f"client not found: {client_id}")
    else:
        res, err = await worker_manager.send_recv_individual(req.dict(), client_id)
        if err is not None:
            return ListJobsResponse(code=500, msg=str(err))
        else:
            return ListJobsResponse(**res)


async def update_scheduler():
    global context, runner_manager
    observer = Observer()
    context.scheduler = AsyncIOScheduler()
    context.scheduler.start()
    context.scheduler_lock = threading.Lock()

    def reset_scheduler():
        logger.debug("reset scheduler")
        context.scheduler.remove_all_jobs()

        workflow_paths = search_workflows(context.opt.workflowsDir)

        # parse workflows and render
        workflows = {}
        for workflow_name, workflow_path in workflow_paths.items():
            workflow, err = parse_yaml_workflow(workflow_path, None)
            if err is not None:
                logger.error(f"error: {err}")
                continue
            workflows[workflow_name] = workflow

        for workflow_name, workflow in workflows.items():
            if workflow.schedule is not None:
                cron_args = {k: v for k, v in
                             zip(('minute', 'hour', 'day', 'month', 'day_of_week'), workflow.schedule.split(' '))}

                context.scheduler.add_job(
                    trigger_workflow,
                    'cron',
                    args=(workflow_name, None),
                    id=workflow.name,
                    **cron_args
                )
                logger.debug(f"add job {workflow.name} with schedule {workflow.schedule}")

    class WorkflowUpdatedHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith(".yaml") or event.src_path.endswith(".yml"):
                with context.scheduler_lock:
                    reset_scheduler()

    event_handler = WorkflowUpdatedHandler()
    observer.schedule(event_handler, context.opt.workflowsDir)
    observer.start()

    with context.scheduler_lock:
        reset_scheduler()

    try:
        logger.info("observer started")
        while True:
            await asyncio.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("observer stopped")
    observer.join()


async def register_worker(remote_endpoint: str):
    """
    Register a worker to remote endpoint
    """
    # get hostname
    client_id = socket.gethostname()
    # initiate websocket connection
    while True:
        try:
            with connect(remote_endpoint + f"/v1/register/{client_id}") as websocket:
                logger.info(f"connected to {remote_endpoint}")
                while True:
                    message = websocket.recv()
                    logger.debug(f"received: {message}")

                    # parse message
                    try:
                        message = json.loads(message)
                        message_type = message.get("type", None)
                    except Exception as e:
                        logger.error(f"error: {e}")
                        websocket.send(Response(code=500, msg=str(e)).json())
                        continue

                    # handle message
                    if message_type == "ListWorkflowsRequest":
                        res = await list_workflows()
                        websocket.send(res.json())
                    elif message_type == "TriggerWorkflowRequest":
                        res = await trigger_workflow_raw(message.get("workflow", None))
                        websocket.send(res.json())
                    elif message_type == "GetJobResultRequest":
                        res = await get_job_result(message.get("job_id", None))
                        websocket.send(res.json())
                    elif message_type == "CancelJobRequest":
                        res = await cancel_job(message.get("job_id", None))
                        websocket.send(res.json())
                    elif message_type == "ListJobsRequest":
                        res = await list_jobs()
                        websocket.send(res.json())
                    elif message_type == "HeartbeatRequest":
                        res = HeartbeatResponse()
                        websocket.send(res.json())
                    else:
                        websocket.send(Response(code=500, msg="message type not found").json())
                        continue
        except Exception as e:
            logger.error(f"error: {e}")
            time.sleep(10)
            continue


@controller.on_event("startup")
async def startup():
    pass


def serve_forever(context_in: Context, port: int, host: str = '0.0.0.0'):
    global context, runner_manager, worker_manager

    # set context
    context = context_in

    # init runner manager
    runner_manager = RunnerManager(context_in.opt)
    runner_manager.begin()

    try:
        loop = asyncio.get_event_loop()

        if context.opt.remoteEndpoint == "":
            # run in server mode
            worker_manager = WorkerManager()
            loop.create_task(update_scheduler())
            config = Config(controller, host=host, port=port, loop=loop, log_level="info", reload=False)
            ser = Server(config=config)
            loop.run_until_complete(ser.serve())
        else:
            # run in worker mode
            loop.create_task(register_worker(context.opt.remoteEndpoint))
            loop.run_forever()

        # uvicorn.run(app=controller, port=port, host=host)
    except KeyboardInterrupt:
        print(f"got KeyboardInterrupt")
        runner_manager.shutdown()
        os._exit(1)
