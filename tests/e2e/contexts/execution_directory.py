import os
import subprocess

import vedro


@vedro.context
def execution_directory(dir_launch: str, dir_requests: str, file_requests: str, requests: str) -> None:
    if os.path.exists(dir_launch):
        subprocess.run(['rm', '-r', dir_launch], check=True)
    os.mkdir(dir_launch)

    os.mkdir(dir_launch + '/' + dir_requests)

    with open(f'{dir_launch}/{dir_requests}/{file_requests}', 'w') as file:
        file.write(requests)

    os.environ.setdefault('GOLDEN_API_URL', 'http://localhost:8080')
    os.environ.setdefault('TESTING_API_URL', 'http://localhost:8080')
