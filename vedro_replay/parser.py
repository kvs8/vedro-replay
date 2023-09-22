import json
import string
from abc import ABC, abstractmethod
from json import JSONDecodeError
from pathlib import PurePosixPath
from typing import List

from pyparsing import (
    CharsNotIn,
    Combine,
    OneOrMore,
    Optional,
    ParseException,
    Suppress,
    Word,
    ZeroOrMore,
    alphas,
    printables,
    restOfLine,
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
        return [Request(method="GET", url=url) for url in data.splitlines()]


class HttpRequestParser(RequestParser):
    delimiter_string = Combine(
        Suppress("###") +
        Optional(Suppress(ZeroOrMore(" "))) +
        restOfLine
    ).set_name("delimiter string with the format '### comment'").set_results_name("comment")

    method = Word(string.ascii_uppercase).set_name("http method").set_results_name("method")

    url = Combine(
        Suppress("http" + Optional("s")) +
        Suppress("://{{host}}") +
        restOfLine
    ).set_name("request uri with the format http(s)://{{host}}/...").set_results_name("url")

    header_name = Word(alphas + "-").set_results_name("header_name")
    header_value = Word(printables + " ").set_results_name("header_value")
    header = (header_name + Suppress(":") + header_value).set_parse_action(
        lambda t: {"key": t.header_name, "value": t.header_value})
    headers = ZeroOrMore(header).set_results_name("headers").set_parse_action(
        lambda t: {h["key"]: h["value"] for h in t})

    json_body = Combine(
        "{" +
        Optional(Suppress("\n")) +
        OneOrMore(CharsNotIn("\n") + Optional(Suppress("\n")))
    ).set_results_name("json_body")

    request = (
            delimiter_string +
            method +
            url +
            Optional(headers) +
            Optional(json_body)
    ).set_results_name("request").set_parse_action(
        lambda t: {
            "comment": t.comment or "",
            "method": t.method,
            "url": t.url,
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

    file_suffix = PurePosixPath(requests_file).suffix

    try:
        if file_suffix == ".http":
            return HttpRequestParser.parse(data=data)
        elif file_suffix == ".txt":
            return TxtRequestParser.parse(data=data)
        else:
            raise UnsupportedRequestFileFormat(f"File format {requests_file} not supported")
    except ParseException as e:
        raise IncorrectContentsRequestFile(f"Failed to process file contents {requests_file}") from e
    except JSONDecodeError as e:
        raise IncorrectContentsRequestFile(f"Failed to process the json body in the file {requests_file}") from e
