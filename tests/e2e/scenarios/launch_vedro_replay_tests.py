import vedro
from contexts.execution_directory import execution_directory
from contexts.mocked_api import mocked_api
from interfaces import VedroReplayCLI, VedroTestCLI
from jj_district42 import HistorySchema
from vedro import params


class Scenario(vedro.Scenario):
    subject = 'launch vedro-replay tests: {subject}'

    @params('default generate',
            'requests',
            'get.txt',
            '/get\n/get',
            )
    @params('generate with --path-requests',
            'special_requests',
            'list.txt',
            '/list\n/list',
            )
    def __init__(self, subject: str, dir_request: str, file_requests: str, requests: str):
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
            requests=self.requests
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

    def then_number_requests_sent_should_be_correct(self):
        assert self.api_mock.history == HistorySchema % [
            {
                'request': {
                    'path': request
                }
            } for request in self.requests.split('\n') * 2
        ]
