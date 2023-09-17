import pytest

from vedro_replay import Request, parse_requests


@pytest.mark.parametrize("request_file,expected_requests", [
    (
            "test_data/get_requests.txt",
            [
                Request(
                    method="GET",
                    request_uri="http://{{host}}/1.0/secure-resource?q=123",
                ),
                Request(
                    method="GET",
                    request_uri="http://{{host}}/1.0/secure-resource?q=example",
                ),
            ]
    ),
    (
            "test_data/get_requests.http",
            [
                Request(
                    comment="Запрос без параметров",
                    method="GET",
                    request_uri="https://{{host}}/",
                ),
                Request(
                    comment="Запрос к API для получения списка всех пользователей",
                    method="GET",
                    request_uri="https://{{host}}/users",
                ),
                Request(
                    comment="Запрос для поиска книги по названию",
                    method="GET",
                    request_uri="https://{{host}}/search?query=Harry+Potter",
                ),
                Request(
                    comment="Запрос для получения информации о товаре по его ID",
                    method="GET",
                    request_uri="https://{{host}}/product?id=12345",
                ),
                Request(
                    comment='Запрос с установкой заголовка "Authorization" для доступа к защищенному ресурсу',
                    method="GET",
                    request_uri="https://{{host}}/secure-resource",
                    headers={'Authorization': 'Bearer 25b4fe6e-89d1-4b1a-8bd9-05624f7e7488'}
                ),
                Request(
                    comment='Запрос с установкой заголовка "User-Agent"',
                    method="GET",
                    request_uri="https://{{host}}/secure-resource",
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
                    }
                ),
                Request(
                    comment='Запрос с указанием заголовка "Accept" для запроса JSON-данных',
                    method="GET",
                    request_uri="https://{{host}}/data",
                    headers={'Accept': 'application/json'}
                ),
                Request(
                    comment='Запрос с кастомным заголовком "X-Custom-Header" для передачи дополнительных данных',
                    method="GET",
                    request_uri="https://{{host}}/resource",
                    headers={'X-Custom-Header': 'SomeCustomValue'}
                ),
                Request(
                    comment='Запрос с заголовком "Accept-Language" для указания предпочтительного языка',
                    method="GET",
                    request_uri="https://{{host}}/data",
                    headers={'Accept-Language': 'en-US'}
                ),
                Request(
                    comment='Запрос с кастомным заголовком "X-Request-Id" для идентификации запроса',
                    method="GET",
                    request_uri="https://{{host}}/data",
                    headers={'X-Request-Id': '12345'}
                ),
                Request(
                    comment='Запрос с передачей сессионной куки для аутентификации пользователя',
                    method="GET",
                    request_uri="https://{{host}}/dashboard",
                    headers={'Cookie': 'session_id=25b4fe6e-89d1-4b1a-8bd9-05624f7e7488'}
                ),
            ]
    ),
    (
            "test_data/post_requests.http",
            [
                Request(
                    comment="Send POST request with json body",
                    method="POST",
                    request_uri="https://{{host}}/post",
                    headers={'Content-Type': 'application/json'},
                    json_body={"id": 999, "value": "content"}
                ),
                Request(
                    method="POST",
                    request_uri="https://{{host}}/post",
                    json_body={"id": 999, "value": "content"}
                ),
                Request(
                    comment="Send POST request with json body",
                    method="POST",
                    request_uri="https://{{host}}/api/user/1",
                    headers={'Content-Type': 'application/json',
                             'Authorization': 'Bearer 25b4fe6e-89d1-4b1a-8bd9-05624f7e7488'},
                    json_body={"name": "John Doe", "email": "johndoe@example.com", "data": {"key": "value"}}
                ),
                Request(
                    comment="Send a POST request with a comment in different languages to the json text",
                    method="POST",
                    request_uri="https://{{host}}/articles/123/comments",
                    headers={'Content-Type': 'application/json'},
                    json_body={
                        "comment_en": "Great article! Thanks for sharing.",
                        "comment_rus": "Комментарий на русском"
                    }
                ),
            ]
    ),
])
def test_parse(request_file, expected_requests):
    actual_requests = parse_requests(request_file)

    assert len(expected_requests) == len(actual_requests)

    for request_number in range(len(expected_requests)):
        assert expected_requests[request_number].comment == actual_requests[request_number].comment
        assert expected_requests[request_number].method == actual_requests[request_number].method
        assert expected_requests[request_number].request_uri == actual_requests[request_number].request_uri
        assert expected_requests[request_number].headers == actual_requests[request_number].headers
        assert expected_requests[request_number].json_body == actual_requests[request_number].json_body
