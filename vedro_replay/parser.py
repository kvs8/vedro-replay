import json
import string
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import List

from pyparsing import (
    Combine,
    OneOrMore,
    Optional,
    ParseException,
    Suppress,
    Word,
    ZeroOrMore,
    alphas,
    printables,
)

from .request import Request


class RequestParserException(Exception):
    pass


class IncorrectContentsRequestFile(RequestParserException):
    pass


class UnsupportedRequestFileFormat(RequestParserException):
    pass


class RequestParser(ABC):
    @classmethod
    @abstractmethod
    def parse(cls, data: str) -> List[Request]:
        pass


class TxtRequestParser(RequestParser):
    @classmethod
    def parse(cls, data: str) -> List[Request]:
        return [Request(method="GET", request_uri=request_uri) for request_uri in data.splitlines()]


class HttpRequestParser(RequestParser):
    rus_alphas = "йцукеёнгшщзхъфывапролджэячсмитьбюЙЦУКЕЁНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
    symbols = printables + rus_alphas

    delimiter_string = Combine(
        Suppress("###") +
        Optional(Suppress(ZeroOrMore(" "))) +
        Optional(Word(symbols + " ")) +
        Suppress("\n")
    ).set_name("delimiter string with the format '### comment'").set_results_name("comment")

    method = Word(string.ascii_uppercase).set_name("http method").set_results_name("method")

    request_uri = Combine(
        "http" + Optional("s") +
        "://{{host}}" +
        Word(symbols)
    ).set_name("request uri with the format http(s)://{{host}}/...").set_results_name("request_uri")

    header_name = Word(alphas + "-").set_results_name("header_name")
    header_value = Word(printables + " ").set_results_name("header_value")
    header = (header_name + Suppress(":") + header_value).set_parse_action(
        lambda t: {"key": t.header_name, "value": t.header_value})
    headers = ZeroOrMore(header).set_results_name("headers").set_parse_action(
        lambda t: {h["key"]: h["value"] for h in t})

    json_body = Combine(
        "{" +
        Optional(Suppress("\n")) +
        OneOrMore(Word(symbols + " ") + Optional(Suppress("\n")))
    ).set_results_name("json_body")

    request = (
            delimiter_string +
            method +
            request_uri +
            Optional(headers) +
            Optional(json_body)
    ).set_results_name("request").set_parse_action(
        lambda t: {
            "comment": t.comment or "",
            "method": t.method,
            "request_uri": t.request_uri,
            "headers": t.headers or None,
            "json_body": json.loads(t.json_body) if t.json_body else None
        }
    )

    @classmethod
    def parse(cls, data: str) -> List[Request]:
        return [
            Request(**request_data)
            for request_data in OneOrMore(cls.request).parse_string(data, parse_all=True).as_list()
        ]


def parse_requests(requests_file: str) -> List[Request]:
    with open(requests_file) as f:
        data = f.read()

    try:
        if ".http" in requests_file:
            return HttpRequestParser.parse(data=data)
        elif ".txt" in requests_file:
            return TxtRequestParser.parse(data=data)
        else:
            raise UnsupportedRequestFileFormat(f"File format {requests_file} not supported")
    except ParseException as e:
        raise IncorrectContentsRequestFile(f"Failed to process file contents {requests_file}") from e
    except JSONDecodeError as e:
        raise IncorrectContentsRequestFile(f"Failed to process the json body in the file {requests_file}") from e
