import os
import subprocess

import vedro


@vedro.context
def clean_directory(dir_launch: str) -> None:
    if os.path.exists(dir_launch):
        subprocess.run(['rm', '-r', dir_launch], check=True)
    os.mkdir(dir_launch)


@vedro.context
def added_request_file(file_path_with_requests: str) -> None:
    os.makedirs(os.path.dirname(file_path_with_requests), exist_ok=True)
    subprocess.run([
        'cp',
        os.path.join('test_data', os.path.basename(file_path_with_requests)),
        file_path_with_requests
    ], check=True)


@vedro.context
def execution_directory(dir_launch: str) -> None:
    clean_directory(dir_launch)

    os.environ.setdefault('GOLDEN_API_URL', 'http://localhost:8080')
    os.environ.setdefault('TESTING_API_URL', 'http://localhost:8080')
