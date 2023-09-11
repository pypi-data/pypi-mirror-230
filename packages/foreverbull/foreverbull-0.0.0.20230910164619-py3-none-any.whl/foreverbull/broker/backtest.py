import requests

from foreverbull import models

from .http import api_call


@api_call(response_model=models.backtest.Backtest)
def list() -> requests.Request:
    return requests.Request(
        method="GET",
        url="/backtest/api/backtests",
    )


@api_call(response_model=models.backtest.Backtest)
def create(backtest: models.backtest.Backtest) -> requests.Request:
    return requests.Request(
        method="POST",
        url="/backtest/api/backtests",
        json=backtest.model_dump(),
    )


@api_call(response_model=models.backtest.Backtest)
def get(name: str) -> requests.Request:
    return requests.Request(
        method="GET",
        url=f"/backtest/api/backtests/{name}",
    )


@api_call(response_model=models.backtest.Session)
def list_sessions(backtest: str = None) -> requests.Request:
    return requests.Request(
        method="GET",
        url="/backtest/api/sessions",
        params={"backtest": backtest},
    )


@api_call(response_model=models.backtest.Session)
def create_session(backtest: str, source: str = "testing", source_key: str = "testing") -> requests.Request:
    return requests.Request(
        method="POST",
        url="/backtest/api/sessions",
        json={"backtest": backtest, "source": source, "source_key": source_key},
    )


@api_call(response_model=models.backtest.Session)
def get_session(session_id: str) -> requests.Request:
    return requests.Request(
        method="GET",
        url=f"/backtest/api/sessions/{session_id}",
    )


@api_call(response_model=models.backtest.Execution)
def list_executions(session: str = None) -> requests.Request:
    return requests.Request(
        method="GET",
        url="/backtest/api/executions",
        params={"session": session},
    )


@api_call(response_model=models.backtest.Execution)
def get_execution(execution_id: str) -> requests.Request:
    return requests.Request(
        method="GET",
        url=f"/backtest/api/executions/{execution_id}",
    )
