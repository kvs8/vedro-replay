import json
from typing import Any, Dict, Optional
from urllib.parse import urlparse


class Request:
    def __init__(
            self, method: str, url: str,
            comment: str = "", headers: Optional[Dict[Any, Any]] = None, json_body: Optional[Dict[Any, Any]] = None
    ) -> None:
        self.comment = comment
        self.method = method
        self.url = url
        self.path = urlparse(url).path
        self.headers = headers
        self.json_body = json_body

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        result = f"{self.method} {self.url}\n"

        if self.headers:
            for key, value in self.headers.items():
                result += f"{key}: {value}\n"

        if self.json_body:
            result += f"{json.dumps(self.json_body)}\n"

        return result
