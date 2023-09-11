from datetime import datetime, timezone
from typing import List, Optional

import pandas as pd
import pynng
from pydantic import field_serializer

from foreverbull import models
from foreverbull.models.finance import Order, Portfolio
from foreverbull.models.service import Database, SocketConfig

from .base import Base
from .service import Parameter


class Backtest(Base):
    name: str
    status: str | None = None
    created_at: Optional[datetime] = None
    backtest_service: str
    worker_service: Optional[str] = None
    calendar: str = "XNYS"
    start_time: datetime
    end_time: datetime
    benchmark: str | None = None
    symbols: List[str]
    ingested_at: Optional[datetime] = None
    sessions: int | None = None

    @field_serializer("start_time")
    def start_time_iso(self, start_time: datetime, _info):
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        return start_time.isoformat()

    @field_serializer("end_time")
    def end_time_iso(self, end_time: datetime, _info):
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        return end_time.isoformat()


class Session(Base):
    id: Optional[str] = None
    backtest: str
    source: str
    source_key: str
    created_at: Optional[datetime]
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    _socket: pynng.Socket | None = None
    socket: SocketConfig | None = None
    error: str | None = None
    executions: int

    def new_execution(self) -> "Execution":
        self._socket.send(models.service.Request(task="new_execution").dump())
        rsp = models.service.Response.load(self._socket.recv())
        return Execution(**rsp.data)

    def run(self, execution: "Execution"):
        self._socket.send(models.service.Request(task="run_execution", data=execution).dump())
        rsp = models.service.Response.load(self._socket.recv())
        if rsp.error:
            raise Exception(rsp.error)
        return rsp.data

    def __enter__(self) -> "Session":
        self._socket = self.socket.get_socket()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Execution(Base):
    id: Optional[str] = None
    calendar: str = "XNYS"
    backtest_service: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    benchmark: Optional[str] = None
    symbols: Optional[List[str]] = None
    capital_base: int = 100000
    database: Optional[Database] = None
    parameters: Optional[List[Parameter]] = []
    socket: Optional[SocketConfig] = None

    @field_serializer("start_time")
    def start_time_iso(self, start_time: datetime, _info):
        if start_time is None:
            return None

        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        return start_time.isoformat()

    @field_serializer("end_time")
    def end_time_iso(self, end_time: datetime, _info):
        if end_time is None:
            return None

        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        return end_time.isoformat()


class IngestConfig(Base):
    calendar: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    symbols: List[str] = []


class Period(Base):
    timestamp: datetime = None
    portfolio: Optional[Portfolio] = None
    symbols: List[str] = None
    new_orders: List[Order] = None
    shorts_count: Optional[int] = None
    pnl: Optional[int] = None
    long_value: Optional[int] = None
    short_value: Optional[int] = None
    long_exposure: Optional[int] = None
    starting_exposure: Optional[int] = None
    short_exposure: Optional[int] = None
    capital_used: Optional[int] = None
    gross_leverage: Optional[int] = None
    net_leverage: Optional[int] = None
    ending_exposure: Optional[int] = None
    starting_value: Optional[int] = None
    ending_value: Optional[int] = None
    starting_cash: Optional[int] = None
    ending_cash: Optional[int] = None
    returns: Optional[int] = None
    portfolio_value: Optional[int] = None
    longs_count: Optional[int] = None
    algo_volatility: Optional[int] = None
    sharpe: Optional[int] = None
    alpha: Optional[int] = None
    beta: Optional[int] = None
    sortino: Optional[int] = None
    max_drawdown: Optional[int] = None
    max_leverage: Optional[int] = None
    excess_return: Optional[int] = None
    treasury_period_return: Optional[int] = None
    benchmark_period_return: Optional[int] = None
    benchmark_volatility: Optional[int] = None
    algorithm_period_return: Optional[int] = None

    @classmethod
    def from_backtest(cls, period):
        return Period(
            timestamp=period["period_open"].to_pydatetime().replace(tzinfo=timezone.utc),
            portfolio=None,
            symbols=[],
            new_orders=[],
            shorts_count=int(period["shorts_count"] * 100),
            pnl=int(period["pnl"] * 100),
            long_value=int(period["long_value"] * 100),
            short_value=int(period["short_value"] * 100),
            long_exposure=int(period["long_exposure"] * 100),
            starting_exposure=int(period["starting_exposure"] * 100),
            short_exposure=int(period["short_exposure"] * 100),
            capital_used=int(period["capital_used"] * 100),
            gross_leverage=int(period["gross_leverage"] * 100),
            net_leverage=int(period["net_leverage"] * 100),
            ending_exposure=int(period["ending_exposure"] * 100),
            starting_value=int(period["starting_value"] * 100),
            ending_value=int(period["ending_value"] * 100),
            starting_cash=int(period["starting_cash"] * 100),
            ending_cash=int(period["ending_cash"] * 100),
            returns=int(period["returns"] * 100),
            portfolio_value=int(period["portfolio_value"] * 100),
            longs_count=int(period["longs_count"] * 100),
            algo_volatility=None if pd.isnull(period["algo_volatility"]) else int(period["algo_volatility"] * 100),
            sharpe=None if pd.isnull(period["sharpe"]) else int(period["sharpe"] * 100),
            alpha=None if period["alpha"] is None or pd.isnull(period["alpha"]) else int(period["alpha"] * 100),
            beta=None if period["beta"] is None or pd.isnull(period["beta"]) else int(period["beta"] * 100),
            sortino=None if pd.isnull(period["sortino"]) else int(period["sortino"] * 100),
            max_drawdown=None if pd.isnull(period["max_drawdown"]) else int(period["max_drawdown"] * 100),
            max_leverage=None if pd.isnull(period["max_leverage"]) else int(period["max_leverage"] * 100),
            excess_return=None if pd.isnull(period["excess_return"]) else int(period["excess_return"] * 100),
            treasury_period_return=None
            if pd.isnull(period["treasury_period_return"])
            else int(period["treasury_period_return"] * 100),
            benchmark_period_return=None
            if pd.isnull(period["benchmark_period_return"])
            else int(period["benchmark_period_return"] * 100),
            benchmark_volatility=None
            if pd.isnull(period["benchmark_volatility"])
            else int(period["benchmark_volatility"] * 100),
            algorithm_period_return=None
            if pd.isnull(period["algorithm_period_return"])
            else int(period["algorithm_period_return"] * 100),
        )


class Result(Base):
    periods: List[Period]
