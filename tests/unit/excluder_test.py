from typing import Any, Dict, List

import pytest

from vedro_replay import filter_data


@pytest.mark.parametrize("data,excludes,expected_data", [
    pytest.param(
        {"data": 1, "random": 2},
        ["random"],
        {"data": 1},
        id='single path cutting'
    ),
    pytest.param(
        {"data": {"rand_index": 5, "id": 123}},
        ["data.rand_index"],
        {"data": {"id": 123}},
        id='cutting in more than one path'
    ),
    pytest.param(
        {"data": [{"rand_index": 1, "id": 123}, {"rand_index": 8, "id": 124}]},
        ["data.*.rand_index"],
        {"data": [{"id": 123}, {"id": 124}]},
        id='cutting by list items'
    ),
    pytest.param(
        {"data": "2_liu23hdl823hdo823hd"},
        [r"data:\d+"],
        {"data": "2"},
        id='cutting out a value by a regular expression'
    ),
    pytest.param(
        {"data": 1},
        ["item"],
        {"data": 1},
        id='cutting by a non-existent single path'
    ),
    pytest.param(
        {"data": 1},
        ["data.id"],
        {"data": 1},
        id='cutting by non-existent more than one path'
    ),
    pytest.param(
        {"data": 1},
        [r"data:\d+"],
        {"data": 1},
        id='cutting out a non-string value by a regular expression'
    ),
    pytest.param(
        {"data": "1"},
        [r"data:\D*"],
        {"data": "1"},
        id='cutting out a value by a regular expression without matches'
    ),
    pytest.param(
        {"data": [{"id": 123}, {"id": 124}]},
        ["data.1"],
        {"data": [{"id": 123}]},
        id='cutting list item by index'
    ),
    pytest.param(
        {"data": [{"id": 123}, {"id": 124}]},
        ["data.-1"],
        {"data": [{"id": 123}, {"id": 124}]},
        id='cutting list item by negative index'
    ),
    pytest.param(
        {"data": [{"id": 123}, {"id": 124}]},
        ["data.2"],
        {"data": [{"id": 123}, {"id": 124}]},
        id='cutting list item by non-existent index'
    ),
    pytest.param(
        {"data": [{"id": 123}, {"id": 124}]},
        ["data.id"],
        {"data": [{"id": 123}, {"id": 124}]},
        id='cutting list item by not numeric index'
    ),
])
def test_exclude(data: Dict[str, Any], excludes: List[str], expected_data: Dict[str, Any]):
    filter_data(excludes, data)

    assert data == expected_data
