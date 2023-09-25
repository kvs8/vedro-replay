from typing import Any

import vedro
from config import Config
from interfaces.api import Api

from vedro_replay import Request, Response


@vedro.context
async def golden_response(request: Request, prepare_response_method: Any) -> Response:
    api = Api(Config.GOLDEN_API_URL)
    response = await api.do_request(request=request)
    return prepare_response_method(response)


@vedro.context
async def testing_response(request: Request, prepare_response_method) -> Response:
    api = Api(Config.TESTING_API_URL)
    response = await api.do_request(request=request)
    return prepare_response_method(response)
