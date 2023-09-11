import logging
import os
from multiprocessing import Event

import pynng

from foreverbull import environment, models, worker


class Session:
    def __init__(self, surveyor: pynng.Surveyor0, states: pynng.Sub0, workers: list[worker.Worker]):
        self._surveyor = surveyor
        self._states = states
        self._workers = workers
        self.logger = logging.getLogger(__name__)

    def info(self):
        return models.service.Info(type="worker", version="0.0.1", parameters=environment.parameters)

    def configure_execution(self, execution: models.backtest.Execution):
        self.logger.info("configuring workers")
        self._surveyor.send(models.service.Request(task="configure_execution", data=execution.model_dump()).dump())
        responders = 0
        while True:
            try:
                rsp = models.service.Response.load(self._surveyor.recv())
                if rsp.error:
                    raise worker.ConfigurationError(rsp.error)
                responders += 1
                if responders == len(self._workers):
                    break
            except pynng.exceptions.Timeout:
                raise worker.ConfigurationError("Workers did not respond in time")
        self.logger.info("workers configured")

    def run_execution(self):
        self.logger.info("running backtest")
        self._surveyor.send(models.service.Request(task="run_execution").dump())
        responders = 0
        while True:
            try:
                self._surveyor.recv()
                responders += 1
                if responders == len(self._workers):
                    break
            except pynng.exceptions.Timeout:
                raise Exception("Workers did not respond in time")
        self.logger.info("backtest running")


class Foreverbull:
    def __init__(self, executors=2):
        self._worker_surveyor_address = "ipc:///tmp/worker_pool.ipc"
        self._worker_surveyor_socket: pynng.Surveyor0 = None
        self._worker_states_address = "ipc:///tmp/worker_states.ipc"
        self._worker_states_socket: pynng.Sub0 = None
        self._worker_stop_event: Event = None
        self._workers = []
        self._executors = executors
        self.logger = logging.getLogger(__name__)

    def __enter__(self) -> Session:
        if environment.func is None:
            raise Exception("No algorithm configured")
        self._worker_surveyor_socket = pynng.Surveyor0(listen=self._worker_surveyor_address)
        self._worker_surveyor_socket.send_timeout = 30000
        self._worker_surveyor_socket.recv_timeout = 30000
        self._worker_states_socket = pynng.Sub0(listen=self._worker_states_address)
        self._worker_states_socket.subscribe(b"")
        self._worker_states_socket.recv_timeout = 30000
        self._worker_stop_event = Event()
        self.logger.info("starting workers")
        for i in range(self._executors):
            self.logger.info("starting worker %s", i)
            if os.getenv("THREADED_EXECUTION"):
                w = worker.WorkerThread(
                    self._worker_surveyor_address,
                    self._worker_states_address,
                    self._worker_stop_event,
                    environment.file_path,
                )
            else:
                w = worker.WorkerProcess(
                    self._worker_surveyor_address,
                    self._worker_states_address,
                    self._worker_stop_event,
                    environment.file_path,
                )
            w.start()
            self._workers.append(w)
        responders = 0
        while True:
            try:
                self._worker_states_socket.recv()
                responders += 1
                if responders == self._executors:
                    break
            except pynng.exceptions.Timeout:
                raise Exception("Workers did not respond in time")
        self.logger.info("workers started")
        return Session(self._worker_surveyor_socket, self._worker_states_socket, self._workers)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._worker_stop_event.is_set():
            self._worker_stop_event.set()
        [worker.join() for worker in self._workers]
        self.logger.info("workers stopped")
        self._worker_surveyor_socket.close()
        self._worker_states_socket.close()
        self._worker_stop_event = None
