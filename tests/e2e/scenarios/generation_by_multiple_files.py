import os
from operator import itemgetter

import vedro
from contexts import added_request_file, execution_directory, mocked_api
from d42 import from_native
from interfaces import VedroReplayCLI, VedroTestCLI


class Scenario(vedro.Scenario):
    subject = 'generation by multiple files'

    def __init__(self):
        self.dir_launch = 'launch'
        self.dir_requests = 'requests'

    def given_prepared_execution_directory(self):
        execution_directory(self.dir_launch)

    def given_added_files_with_requests(self):
        added_request_file(
            os.path.join(self.dir_launch, self.dir_requests, 'items', 'get_1_0_items.http')
        )
        added_request_file(
            os.path.join(self.dir_launch, self.dir_requests, 'items', 'get_1_1_items.txt')
        )
        added_request_file(
            os.path.join(self.dir_launch, self.dir_requests, 'users/create', 'post_v1_users.http')
        )
        added_request_file(
            os.path.join(self.dir_launch, self.dir_requests, 'users/create', 'post_v2_admin_users.http')
        )
        added_request_file(
            os.path.join(self.dir_launch, self.dir_requests, 'get_secure_resource.http')
        )

    async def given_vedro_replay_tests(self):
        self.stdout_vedro_replay, self.stderr_vedro_replay = await VedroReplayCLI(
            dir_launch=self.dir_launch,
            dir_requests=self.dir_requests
        ).run()
        self.generated_structure = sorted(
            [[a, sorted(d), sorted(f)] for a, d, f in os.walk(self.dir_launch)],
            key=itemgetter(0)
        )

    async def when_replay_tests_running(self):
        async with mocked_api() as self.api_mock:
            self.stdout_vedro_test, self.stderr_vedro_test = await VedroTestCLI(
                dir_launch=self.dir_launch
            ).run()

    def then_tests_ended_with_correct_statistics(self):
        assert '# 9 scenarios, 9 passed, 0 failed, 0 skipped' in self.stdout_vedro_test

    def and_then_generated_project_structure_is_correct(self):
        assert self.generated_structure == from_native([
            ['launch', ['contexts', 'helpers', 'interfaces', 'requests', 'scenarios'], ['config.py', 'vedro.cfg.py']],
            ['launch/contexts', [], ['__init__.py', 'api.py']],
            ['launch/helpers', [], ['__init__.py', 'helpers.py']],
            ['launch/interfaces', [], ['__init__.py', 'api.py']],
            ['launch/requests', ['items', 'users'], ['get_secure_resource.http']],
            ['launch/requests/items', [], ['get_1_0_items.http', 'get_1_1_items.txt']],
            ['launch/requests/users', ['create'], []],
            ['launch/requests/users/create', [], ['post_v1_users.http', 'post_v2_admin_users.http']],
            ['launch/scenarios', ['items', 'users'], ['get_secure_resource.py']],
            ['launch/scenarios/items', [], ['get_1_0_items.py', 'get_1_1_items.py']],
            ['launch/scenarios/users', ['create'], []],
            ['launch/scenarios/users/create', [], ['post_v1_users.py', 'post_v2_admin_users.py']]
        ])
