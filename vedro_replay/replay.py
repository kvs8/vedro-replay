import os
from typing import Any, Callable

from vedro import params

from .parser import parse_requests


def replay(requests_file: str) -> Callable[..., Any]:
    assert os.path.exists(requests_file)

    def wrapped(fn: Callable[..., Any]) -> Callable[..., Any]:
        for request in parse_requests(requests_file):
            params(request.comment, request)(fn)
        return fn

    return wrapped
