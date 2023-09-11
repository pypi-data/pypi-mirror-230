import time
from datetime import datetime
from typing import List

import typer
from rich.console import Console
from typing_extensions import Annotated

from foreverbull import broker, models

name_argument = Annotated[str, typer.Argument(help="name of the backtest")]
name_option = Annotated[str, typer.Option(help="name of the backtest")]
session_option = Annotated[str, typer.Option(help="session id of the backtest")]
backtest_service_option = Annotated[str, typer.Option(help="backtest service to use")]
start_option = Annotated[datetime, typer.Option(help="start time of the backtest")]
end_option = Annotated[datetime, typer.Option(help="end time of the backtest")]
symbol_option = Annotated[
    List[str], typer.Option(help="symbol to use, require multiple --symbol entries for multiple values")
]
benchmark_option = Annotated[str, typer.Option(help="benchmark to use")]

backtest = typer.Typer()

std = Console()
std_err = Console(stderr=True)


@backtest.command()
def list():
    std.print(broker.backtest.list())


@backtest.command()
def create(
    name: name_argument,
    backtest_service: backtest_service_option,
    start: start_option,
    end: end_option,
    symbol: symbol_option,
    benchmark: benchmark_option = None,
):
    backtest = models.backtest.Backtest(
        name=name,
        backtest_service=backtest_service,
        start_time=start,
        end_time=end,
        symbols=symbol,
        benchmark=benchmark,
    )
    backtest = broker.backtest.create(backtest)
    std.print("Created successfully")
    with std.status("Waiting for backtest to be ready"):
        for _ in range(60):
            backtest = broker.backtest.get(name)
            if backtest.status == "READY":
                std.print("Backtest is ready")
                std.print(backtest)
                break
            time.sleep(0.5)
        else:
            std_err.print("Failed to create backtest")


@backtest.command()
def get(backtest_name: name_argument):
    std.print(broker.backtest.get(backtest_name))


@backtest.command()
def sessions(backtest_name: name_option = None):
    std.print(broker.backtest.list_sessions(backtest_name))


@backtest.command()
def executions(session_id: session_option = None):
    std.print(broker.backtest.list_executions(session_id))
