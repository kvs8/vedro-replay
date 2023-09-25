import asyncio
import os
from abc import ABC
from typing import Tuple

import vedro


class AbstractCLI(ABC, vedro.Interface):
    @staticmethod
    async def _run(command: str, **kwargs) -> Tuple[str, str]:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode(), stderr.decode()


class VedroReplayCLI(AbstractCLI):
    def __init__(self, dir_launch: str, dir_requests: str) -> None:
        self.dir_launch = dir_launch
        self.dir_requests = dir_requests

    async def run(self) -> Tuple[str, str]:
        return await self._run(
            command=f'vedro-replay generate {self.__requests_dir()}',
            cwd=f'{os.getcwd()}/{self.dir_launch}'
        )

    def __requests_dir(self) -> str:
        return '' if self.dir_requests == 'requests' else f'--requests-dir={self.dir_requests}'


class VedroTestCLI(AbstractCLI):
    def __init__(self, dir_launch: str) -> None:
        self.dir_launch = dir_launch

    async def run(self) -> Tuple[str, str]:
        return await self._run(
            command='vedro run -vvv',
            cwd=f'{os.getcwd()}/{self.dir_launch}'
        )
