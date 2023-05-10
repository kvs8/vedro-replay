import re
from copy import deepcopy
from typing import Any, Dict, List

from vedro_replay.response import Response


class Excluder:
    @staticmethod
    def excludes_headers(excludes: List[Any], headers: Dict[str, str]) -> None:
        for exclude in excludes:
            if exclude in headers.keys():
                del headers[exclude]

    @classmethod
    def exclude_by_several_path(cls, excluded_paths: List[Any], data: Dict[str, Any]) -> None:
        for excluded_path in excluded_paths:
            cls.exclude_by_path(data=data, excluded_path=excluded_path)

    @classmethod
    def exclude_by_path(cls, data: Dict[str, Any], excluded_path: str) -> None:
        if isinstance(excluded_path, str):
            cls.exclude(
                data=data,
                excluded_path=excluded_path.split('.'),
                reg_for_exclude=''
            )
        elif isinstance(excluded_path, dict):
            for key in excluded_path.keys():
                cls.exclude(
                    data=data,
                    excluded_path=key.split('.'),
                    reg_for_exclude=excluded_path[key]
                )

    @classmethod
    def exclude(cls, data: Dict[str, Any], excluded_path: List[str], reg_for_exclude: str) -> None:
        current_path_part = excluded_path[0]
        excluded_path.pop(0)

        if len(excluded_path) == 0:
            if current_path_part in data.keys():
                if reg_for_exclude != '':
                    value = re.search(reg_for_exclude, data[current_path_part])
                    if value is not None:
                        data[current_path_part] = value[0]
                else:
                    del data[current_path_part]
            return

        if isinstance(data, list) and current_path_part == '*':
            for elem in data:
                cls.exclude(elem, deepcopy(excluded_path), reg_for_exclude)
        else:
            if isinstance(data, dict) and current_path_part in data.keys():
                cls.exclude(data[current_path_part], deepcopy(excluded_path), reg_for_exclude)


def filter_response(response: Response, exclude_headers: List[Any], exclude_body: List[Any]) -> Response:
    Excluder.excludes_headers(exclude_headers, response.headers)
    if isinstance(response.body, list):
        for part in response.body:
            Excluder.exclude_by_several_path(exclude_body, part)
    else:
        Excluder.exclude_by_several_path(exclude_body, response.body)
    return response
