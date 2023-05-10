import os
from typing import Any, Callable

from vedro import params


def replay(requests_file: str) -> Callable[..., Any]:
    assert os.path.exists(requests_file)

    def wrapped(fn: Callable[..., Any]) -> Callable[..., Any]:
        with open(requests_file) as f:
            for request in f.read().splitlines():
                params(request)(fn)
        return fn

    return wrapped
