import jj
import vedro
from jj.mock import Mocked, mocked


@vedro.context
def mocked_api() -> Mocked:
    matcher = jj.match("*")
    response = jj.Response(status=200, json={'code': 'ok'}, headers={'Date': ''})
    return mocked(matcher, response)
