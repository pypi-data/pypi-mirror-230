import importlib
import signal
import socket
import time
from threading import Event, Thread

import pynng
import typer
from rich.console import Console
from typing_extensions import Annotated

from foreverbull import Foreverbull, broker, models

from .backtest import backtest
from .service import service

cli = typer.Typer()

cli.add_typer(backtest, name="backtest", help="asfk")
cli.add_typer(service, name="service")


std = Console()
std_err = Console(stderr=True)

file_name = Annotated[str, typer.Argument(help="file name containing the alorigthm")]
backtest = Annotated[str, typer.Option(help="name of backtest to use")]


@cli.command()
def run(
    file_name: file_name,
    backtest: backtest = None,
):
    foreverbull = Foreverbull()

    try:
        importlib.import_module(file_name.replace("/", ".").split(".py")[0])
    except Exception as e:
        std_err.log(f"Could not import {file_name}: {e}")
        exit(1)

    if backtest:
        session = broker.backtest.create_session(backtest)
        std.log("session created, waiting for session to start...")
        while session.socket is None:
            if session.error:
                raise Exception("backtest failed to start: ", session.error)
            time.sleep(0.2)
            session = broker.backtest.get_session(session.id)
        std.log("session started: ", session)
        with session as session, foreverbull as fb:
            execution = session.new_execution()
            std.log("execution created: ", execution)
            execution.socket.host = "127.0.0.1"
            fb.configure_execution(execution)
            fb.run_execution()
            session.run(execution)
        return

    def socket_runner(fb: Foreverbull, socket_config: models.service.SocketConfig, stop_event: Event):
        socket = pynng.Rep0(listen=f"tcp://{socket_config.host}:{socket_config.port}")
        while not stop_event.is_set():
            ctx = socket.new_context()
            try:
                req = models.service.Request.load(ctx.recv())
                match req.task:
                    case "info":
                        ctx.send(models.service.Response(task="info", data=fb.info()).model_dump())
                    case "configure_execution":
                        data = fb.configure_execution(models.backtest.Execution(**req.data))
                        ctx.send(models.service.Response(task="configure_execution", data=data).model_dump())
                    case "run_execution":
                        data = fb.run_execution()
                        ctx.send(models.service.Response(task="run_execution", data=data).model_dump())
                    case "stop":
                        ctx.send(models.service.Response(task="stop").model_dump())
                        break
            except pynng.exceptions.Timeout:
                pass
            except Exception as e:
                std_err.log(f"Error in socket runner: {e}")
            finally:
                ctx.close()
        socket.close()

    stop_event = Event()
    socket_config = models.service.SocketConfig(
        host=socket.gethostname(),
        port=5555,
        socket_type=models.service.SocketType.REPLIER,
        listen=True,
    )

    with foreverbull as fb:
        t = Thread(target=socket_runner, args=(fb, socket_config, stop_event))
        t.start()
        broker.service.update_instance(socket.gethostname(), socket_config)
        signal.signal(signal.SIGINT, lambda x, y: stop_event.set())
        signal.signal(signal.SIGTERM, lambda x, y: stop_event.set())
        t.join()
        broker.service.update_instance(socket.gethostname(), None)
