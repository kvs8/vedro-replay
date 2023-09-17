import copy
import json
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from jinja2 import Template


class Request:
    def __init__(
            self, method: str, request_uri: str,
            comment: str = "", headers: Optional[Dict[Any, Any]] = None, json_body: Optional[Dict[Any, Any]] = None
    ) -> None:
        self.comment = comment
        self.method = method
        self.request_uri = request_uri
        self.path = urlparse(request_uri).path
        self.headers = headers
        self.json_body = json_body

    def specify_host(self, host: str) -> "Request":
        prepared_request = copy.deepcopy(self)
        prepared_request.request_uri = Template(prepared_request.request_uri).render(host=host)
        return prepared_request

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        result = "{method} {request_uri}\n".format(method=self.method, request_uri=self.request_uri)

        if self.headers:
            for key, value in self.headers.items():
                result += f"{key}: {value}\n"

        if self.json_body:
            result += f"{json.dumps(self.json_body)}\n"

        return result
