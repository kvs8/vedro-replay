import pytest

from vedro_replay import Request, parse_requests


@pytest.mark.parametrize("request_file,expected_requests", [
    (
            "test_data/get_requests.txt",
            [
                Request(
                    method="GET",
                    url="/1.0/secure-resource?q=123",
                ),
                Request(
                    method="GET",
                    url="/1.0/secure-resource?q=example",
                ),
            ]
    ),
    (
            "test_data/get_requests.http",
            [
                Request(
                    comment="Request without parameters",
                    method="GET",
                    url="/",
                ),
                Request(
                    comment="API request to get a list of all users",
                    method="GET",
                    url="/users",
                ),
                Request(
                    comment="Request to search for a book by title",
                    method="GET",
                    url="/search?query=Harry+Potter",
                ),
                Request(
                    comment="Request for information about a product by its ID",
                    method="GET",
                    url="/product?id=12345",
                ),
                Request(
                    comment='Request with setting the "Authorization" header to access a protected resource',
                    method="GET",
                    url="/secure-resource",
                    headers={'Authorization': 'Bearer 25b4fe6e-89d1-4b1a-8bd9-05624f7e7488'}
                ),
                Request(
                    comment='Request with the header "User-Agent"',
                    method="GET",
                    url="/secure-resource",
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
                    }
                ),
                Request(
                    comment='Request specifying the "Accept" header for requesting JSON data',
                    method="GET",
                    url="/data",
                    headers={'Accept': 'application/json'}
                ),
                Request(
                    comment='Request with custom header "X-Custom-Header" for transmitting additional data',
                    method="GET",
                    url="/resource",
                    headers={'X-Custom-Header': 'SomeCustomValue'}
                ),
                Request(
                    comment='Request with the "Accept-Language" header to specify the preferred language',
                    method="GET",
                    url="/data",
                    headers={'Accept-Language': 'en-US'}
                ),
                Request(
                    comment='Request with custom header "X-Request-Id" to identify the request',
                    method="GET",
                    url="/data",
                    headers={'X-Request-Id': '12345'}
                ),
                Request(
                    comment='Request with the transfer of a session cookie for user authentication',
                    method="GET",
                    url="/dashboard",
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
                    url="/post",
                    headers={'Content-Type': 'application/json'},
                    json_body={"id": 999, "value": "content"}
                ),
                Request(
                    method="POST",
                    url="/post",
                    json_body={"id": 999, "value": "content"}
                ),
                Request(
                    comment="Send POST request with json body",
                    method="POST",
                    url="/api/user/1",
                    headers={'Content-Type': 'application/json',
                             'Authorization': 'Bearer 25b4fe6e-89d1-4b1a-8bd9-05624f7e7488'},
                    json_body={"name": "John Doe", "email": "johndoe@example.com", "data": {"key": "value"}}
                ),
                Request(
                    comment="Send a POST request with a comment in different languages to the json text",
                    method="POST",
                    url="/articles/123/comments",
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
        assert expected_requests[request_number].url == actual_requests[request_number].url
        assert expected_requests[request_number].headers == actual_requests[request_number].headers
        assert expected_requests[request_number].json_body == actual_requests[request_number].json_body
