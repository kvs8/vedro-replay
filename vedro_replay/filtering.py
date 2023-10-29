from typing import Any, Dict, List

from .parse_excludes import parse_excludes
from .response import Response


def filter_response(response: Response, exclude_headers: List[Any], exclude_body: List[Any]) -> Response:
    filter_data(raw_excludes=exclude_headers, data=response.headers)

    if isinstance(response.body, list):
        for body_part in response.body:
            filter_data(raw_excludes=exclude_body, data=body_part)
    else:
        filter_data(raw_excludes=exclude_body, data=response.body)

    return response


def filter_data(raw_excludes: List[str], data: Dict[str, Any]) -> None:
    for exclude in parse_excludes(raw_excludes):
        exclude.execute(data)
