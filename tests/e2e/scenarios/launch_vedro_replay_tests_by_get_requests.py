import os
from typing import List

import vedro
from contexts import added_request_file, execution_directory, mocked_api
from interfaces import VedroReplayCLI, VedroTestCLI
from jj_district42 import HistorySchema
from vedro import params

from vedro_replay.request import Request


class Scenario(vedro.Scenario):
    subject = 'launch vedro-replay by GET requests: {subject}'

    @params('.txt file',
            'requests',
            'get_1_1_items.txt',
            [
                Request(
                    method="GET",
                    url="/1.1/items?q=123",
                ),
                Request(
                    method="GET",
                    url="/1.1/items?q=example",
                ),
            ]
            )
    @params('.http file. Generate with --requests-dir',
            'special_requests',
            'get_1_0_items.http',
            [
                Request(
                    comment='GET Request',
                    method="GET",
                    url="/1.0/items",
                ),
                Request(
                    method="GET",
                    url="/1.0/items?data=all&search=value",
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
                }
            } for request in [r for r in reversed(self.requests) for _ in range(2)]
        ]
