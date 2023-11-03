import re
from copy import deepcopy
from typing import Any, Dict, List


class Exclude:
    def __init__(self, parts_path: List[str], reg_exp: str) -> None:
        self.parts_path = parts_path
        self.reg_exp = reg_exp

    def execute(self, data: Dict[str, Any]) -> None:
        self._exclude(data, deepcopy(self.parts_path))

    def _exclude(self, data: Dict[str, Any], excluded_path: List[str]) -> None:
        current_path_part = excluded_path[0]
        excluded_path.pop(0)

        if not excluded_path:
            if isinstance(data, dict) and current_path_part in data.keys():
                if self.reg_exp:
                    if isinstance(data[current_path_part], str):
                        result = re.search(self.reg_exp, data[current_path_part])
                        if result is not None and result[0]:
                            data[current_path_part] = result[0]
                else:
                    del data[current_path_part]
            elif isinstance(data, list) and current_path_part.isdigit() and len(data) > int(current_path_part):
                data.pop(int(current_path_part))
            return

        if isinstance(data, list) and current_path_part == '*':
            for elem in data:
                self._exclude(elem, deepcopy(excluded_path))
        elif isinstance(data, dict) and current_path_part in data.keys():
            self._exclude(data[current_path_part], deepcopy(excluded_path))
