import io
import multiprocessing as mp
import queue
import threading
import time
import uuid
from multiprocessing.pool import Pool, AsyncResult
from os import path as osp
from typing import Dict, Tuple, Optional, List, Any

from loguru import logger
from starlette.websockets import WebSocket

from workflow_keeper.actions import get_action
from workflow_keeper.config import Config
from workflow_keeper.datamodels import Workflow, HeartbeatRequest, JobStep, Job


class Engine:
    @classmethod
    def execute_step(cls, job_step: JobStep, log_output: Optional[io.TextIOWrapper]) -> Tuple[str, Optional[Exception]]:
        action = get_action(job_step)
        return action.run(job_step, log_output)

    @classmethod
    def execute_jobs(cls, jobs: List[Job], job_id: str, log_output: Optional[io.TextIOWrapper]) -> Dict[
        str, Dict[str, Tuple[str, Optional[Exception]]]]:
        logger.info(f"executing job: {job_id}")
        res = {}
        for job in jobs:
            job_res = {}
            for step in job.steps:
                msg, err = cls.execute_step(step, log_output)
                log_output.flush()
                job_res[step.name] = (msg, err)
                if err is not None:
                    break
            res[job.name] = job_res
        return res

    @classmethod
    def execute_workflow(cls, workflow: Workflow, job_id: str, log_output_path: str) -> Dict[
        str, Dict[str, Tuple[str, Optional[Exception]]]]:
        log_output = open(log_output_path, "w+")
        # execute jobs
        res = cls.execute_jobs(workflow.jobs, job_id, log_output)
        return res


class RunnerManager:
    def __init__(self, opt: Config):
        self.opt = opt

        # database
        self.ongoing_jobs: Dict[str, Tuple[Pool, AsyncResult]] = {}
        self.concurrency_events: Dict[str, mp.Event] = {}
        self.expire_queue = queue.Queue()

        # cleanup thread
        self.cleanup_thread_stop_ev = threading.Event()
        self.cleanup_thread = None

    def _check_concurrency(self, workflow: Workflow) -> bool:
        """
        Check if the workflow can be triggered under the concurrency limit.
        """
        if workflow.name not in self.concurrency_events.keys():
            self.concurrency_events[workflow.name] = mp.Event()

        if not workflow.concurrency:  # if concurrency is set to True, then no limit
            if self.concurrency_events[workflow.name].is_set():
                return False
            else:
                self.concurrency_events[workflow.name].set()
                return True
        else:
            return True

    def trigger(self, workflow: Workflow) -> Tuple[str, Optional[Exception]]:
        """
        Trigger a workflow.
        """
        job_id = str(uuid.uuid4())
        if not self._check_concurrency(workflow):
            return '', Exception("concurrency limit exceeded")

        log_output_path = osp.join(self.opt.logDir, f"{job_id}.log")

        pool = mp.Pool(processes=1)
        job = pool.apply_async(
            Engine.execute_workflow,
            args=(workflow, job_id, log_output_path),
            callback=lambda _: self.concurrency_events[workflow.name].clear()
        )
        pool.close()

        # add to database
        self.ongoing_jobs[job_id] = (pool, job)  # add pool to enable force release
        self.expire_queue.put((job_id, time.time()))
        return job_id, None

    def _cleanup(self, stop_ev: threading.Event):
        """
        Cleanup thread.
        """
        logger.info("starting release_job_resource_thread")
        while True:
            if stop_ev.is_set():
                break
            if self.expire_queue.empty():
                time.sleep(2)
                continue
            for _ in range(self.expire_queue.qsize()):
                job_id, timestamp = self.expire_queue.get()
                if time.time() - timestamp > 86400:
                    logger.debug(f"job {job_id} expired with timestamp {timestamp}")
                    if job_id in self.ongoing_jobs.keys():
                        pool, job = self.ongoing_jobs[job_id]
                        try:
                            success = job.successful()
                        except Exception as _:
                            success = False

                        if success:
                            pool.join()
                            logger.info(f"job {job_id} released")
                        else:
                            pool.terminate()
                            logger.warning(f"job {job_id} force released")

                        del self.ongoing_jobs[job_id]

                    else:
                        logger.warning(f"job {job_id} not in self.ongoing_jobs")
                else:
                    self.expire_queue.put((job_id, timestamp))

            time.sleep(2)

    def begin(self):
        """
        Start the cleanup thread.
        """
        self.cleanup_thread_stop_ev.clear()
        self.cleanup_thread = threading.Thread(target=self._cleanup, args=(self.cleanup_thread_stop_ev,),
                                               daemon=True)
        self.cleanup_thread.start()

    def shutdown(self):
        """
        Stop the cleanup thread.
        """
        self.cleanup_thread_stop_ev.set()
        self.cleanup_thread.join()
        logger.info("cleanup_thread stopped")

    def get_job(self, job_id) -> Tuple[
        Optional[Dict[str, Dict[str, Tuple[str, Optional[Exception]]]]], Optional[Exception]]:
        """
        Get job result.
        """
        res = self.ongoing_jobs.get(job_id, None)
        if res is None:
            return None, Exception(f"job not found: {job_id}")
        else:
            pool, job = res
            if job.ready():
                return job.get(), None
            else:
                return None, None

    @property
    def jobs(self) -> List[str]:
        """
        List all jobs.
        """
        return list(self.ongoing_jobs.keys())

    def cancel_job(self, job_id) -> Optional[Exception]:
        """
        Cancel a job.
        """
        res = self.ongoing_jobs.get(job_id, None)
        if res is None:
            return Exception(f"job not found: {job_id}")
        else:
            pool, job = res
            if job.ready():
                return Exception(f"job {job_id} already finished")
            else:
                try:
                    # by terminating the pool
                    pool.terminate()
                    del self.ongoing_jobs[job_id]
                    return None
                except Exception as e:
                    return Exception(f"job {job_id} not canceled: {e}")

    def __del__(self):
        pass


class WorkerManager:
    def __init__(self):
        """
        Worker manager. Manage all connected workers via websocket.
        """
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_locks: Dict[str, threading.Lock] = {}  # connection lock for each client

    @property
    def clients(self):
        """
        List all connected clients.
        """
        return list(self.active_connections.keys())

    async def connect(self, client_id: str, websocket: WebSocket) -> bool:
        """
        Handle websocket connection.
        """
        await websocket.accept()
        if client_id in self.active_connections.keys():
            await websocket.close(code=4000, reason=f"client {client_id} already connected")
            return False
        self.active_connections[client_id] = websocket
        self.connection_locks[client_id] = threading.Lock()
        return True

    async def send_recv_individual(
            self,
            message: Dict[str, Any],
            client_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
        try:
            self.connection_locks[client_id].acquire(timeout=10)
        except Exception as e:
            logger.error(f"error: {e}")
            return None, e

        try:
            await self.send_individual(message, client_id)
            res = await self.active_connections[client_id].receive_json()
            return res, None
        except Exception as e:
            logger.error(f"error: {e}")
            return None, e
        finally:
            self.connection_locks[client_id].release()

    async def heartbeat(self, client_id: str) -> Optional[Exception]:
        """
        Send heartbeat to client.
        """
        req = HeartbeatRequest()
        res, err = await self.send_recv_individual(req.dict(), client_id)
        if err is not None:
            return err
        else:
            if res.get("msg", None) != "pong":
                return Exception("heartbeat failed")
            else:
                return None

    def disconnect(self, client_id: str):
        """
        Disconnect a client.
        """
        self.connection_locks[client_id].acquire()
        del self.active_connections[client_id]
        self.connection_locks[client_id].release()
        del self.connection_locks[client_id]

    async def send_individual(self, message: Dict[str, Any], client_id: str):
        if client_id in self.active_connections:
            return await self.active_connections[client_id].send_json(message)
        else:
            return None

    async def broadcast(self, message: str):
        for _, connection in self.active_connections.items():
            await connection.send_text(message)
