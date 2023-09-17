from typing import List

import vedro
from contexts import execution_directory, mocked_api
from interfaces import VedroReplayCLI, VedroTestCLI
from jj_district42 import HistorySchema
from vedro import params

from vedro_replay.request import Request


class Scenario(vedro.Scenario):
    subject = 'launch vedro-replay tests: {subject}'

    @params('default generate by .txt file',
            'requests',
            'get_requests.txt',
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
            )
    @params('default generate by GET requests from .http file',
            'requests',
            'get_requests.http',
            [
                Request(
                    comment='Запрос с установкой заголовка "Authorization" для доступа к защищенному ресурсу',
                    method="GET",
                    request_uri="http://{{host}}/1.0/secure-resource",
                ),
                Request(
                    method="GET",
                    request_uri="http://{{host}}/1.0/secure-resource",
                ),
            ]
            )
    @params('generate with --path-requests by POST requests from .http file',
            'special_requests',
            'post_requests.http',
            [
                Request(
                    comment='Назначение прав пользователю',
                    method="POST",
                    request_uri="http://{{host}}/1.0/admin-users",
                    json_body={
                        "id": 17399, "user": "a82ec47d-9b72-41d7-9b4d-f36427561dd6", "data": [
                            {"item": {"value": "Значение"}}
                        ]
                    }
                ),
                Request(
                    comment='Назначение прав пользователю',
                    method="POST",
                    request_uri="http://{{host}}/1.0/admin-users",
                    json_body={
                        "id": 17399, "user": "a82ec47d-9b72-41d7-9b4d-f36427561dd6", "data": [
                            {"item": {"value": "Значение"}}
                        ]
                    }
                ),
            ]
            )
    def __init__(self, subject: str, dir_request: str, file_requests: str, requests: List[Request]):
        self.subject = subject
        self.dir_launch = 'launch'
        self.dir_requests = dir_request
        self.file_requests = file_requests
        self.requests = requests

    def given_prepared_execution_directory(self):
        execution_directory(
            dir_launch=self.dir_launch,
            dir_requests=self.dir_requests,
            file_requests=self.file_requests,
        )

    async def given_vedro_replay_tests(self):
        self.stdout_vedro_replay, self.stderr_vedro_replay = await VedroReplayCLI(
            dir_launch=self.dir_launch,
            dir_requests=self.dir_requests
        ).run()

    async def when_replay_tests_running(self):
        async with mocked_api() as self.api_mock:
            self.stdout_vedro_test, self.stderr_vedro_test = await VedroTestCLI(
                dir_launch=self.dir_launch
            ).run()

    def then_test_was_started_with_correct_subject(self):
        for request in self.requests:
            assert f'do request: {request.path}. {request.comment}' in self.stdout_vedro_test

    def and_then_number_requests_sent_should_be_correct(self):
        assert self.api_mock.history == HistorySchema % [
            {
                'request': {
                    'method': request.method,
                    'path': request.path,
                    'body': request.json_body or b'',
                }
            } for request in self.requests * 2
        ]
