import os
from typing import Any, Callable

from vedro import params

from .parse_requests import parse_requests


def replay(requests_file: str) -> Callable[..., Any]:
    assert os.path.exists(requests_file)

    def wrapped(fn: Callable[..., Any]) -> Callable[..., Any]:
        for request in reversed(parse_requests(requests_file)):
            params(request)(fn)
        return fn

    return wrapped
