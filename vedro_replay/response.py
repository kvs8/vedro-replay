import json
from abc import ABC, abstractmethod
from typing import Any, Dict

from requests_toolbelt.multipart import decoder


class Response(ABC):
    def __init__(self, status: int, headers: Dict[Any, Any], body: Any, request_url: str) -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self.request_url = request_url

    @classmethod
    @abstractmethod
    def from_response(cls, response: Any) -> "Response":
        pass

    def __repr__(self) -> str:
        r = f'REQUEST: {self.request_url}\n'
        r += f'STATUS CODE: {self.status}'
        return r


class JsonResponse(Response):
    @classmethod
    def from_response(cls, response: Any) -> "JsonResponse":
        return cls(
            status=response.status_code,
            headers=dict(response.headers),
            body=response.json(),
            request_url=response.request.url
        )


class MultipartResponse(Response):
    @classmethod
    def from_response(cls, response: Any) -> "MultipartResponse":
        return cls(
            status=response.status_code,
            headers=dict(response.headers),
            body=[json.loads(part.text) for part in decoder.MultipartDecoder.from_response(response).parts],
            request_url=response.request.url
        )
