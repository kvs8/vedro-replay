import os
from typing import List

import vedro
from contexts import added_request_file, execution_directory, mocked_api
from interfaces import VedroReplayCLI, VedroTestCLI
from jj_district42 import HistorySchema
from vedro import params

from vedro_replay.request import Request


class Scenario(vedro.Scenario):
    subject = 'launch vedro-replay tests by requests with headers: {subject}'

    @params('GET requests from .http file',
            'requests',
            'get_secure_resource.http',
            [
                Request(
                    comment='Request with the "Authorization" header setting to access a protected resource',
                    method="GET",
                    url="/secure-resource",
                    headers={
                        "X-Forwarded-For": "213.87.224.239",
                        "Authorization": "Bearer 25b4fe6e-89d1-4b1a-8bd9-05624f7e7488"
                    }
                ),
                Request(
                    comment='Request with cookie',
                    method="GET",
                    url="/secure-resource?query=value",
                    headers={
                        "Cookie": "session_id=25b4fe6e-89d1-4b1a-8bd9-05624f7e7488",
                    }
                ),
            ]
            )
    @params('POST requests from .http file',
            'requests',
            'post_v1_users.http',
            [
                Request(
                    comment='POST request with headers',
                    method="POST",
                    url="/v1/users",
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
                    },
                    json_body={"name": "John Doe", "email": "johndoe@example.com"}
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
        execution_directory(dir_launch=self.dir_launch)

    def given_added_file_with_requests(self):
        added_request_file(os.path.join(self.dir_launch, self.dir_requests, self.file_requests))

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
            subject = f"do request: {request.method} {request.path} (comment='{request.comment}')"
            assert subject in self.stdout_vedro_test

    def and_then_number_requests_sent_should_be_correct(self):
        assert self.api_mock.history == HistorySchema % [
            {
                'request': {
                    'method': request.method,
                    'path': request.path,
                    'headers': [...] + [[hn, hv] for hn, hv in request.headers.items()] + [...]
                }
            } for request in [r for r in reversed(self.requests) for _ in range(2)]
        ]
