import requests

from foreverbull import models

from .http import api_call


@api_call(response_model=models.finance.Asset)
def get_assets() -> requests.Request:
    return requests.Request(
        method="GET",
        url="/finance/api/assets",
        params={},
    )
