import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from types import FunctionType
from typing import Any, List

from jinja2 import Environment, FileSystemLoader, Template

from .parser import parse_requests


class GeneratorException(Exception):
    pass


class DirectoryWithRequestsNotFound(GeneratorException):
    pass


class Generator(ABC):
    def __init__(self, force: bool, log: logging.Logger):
        self.force = force
        self.log = log

    @abstractmethod
    def _get_template(self, template_name: str) -> Template:
        pass

    def _generate_by_template(self, file_path: str, template_name: str, **kwargs: Any) -> None:
        if not os.path.exists(file_path) or self.force:
            self.log.info(f'Generate: "{file_path}"')
            template = self._get_template(template_name=template_name)
            with open(file_path, 'w') as file:
                file.write(template.render(**kwargs))

    def _create_package(self, dir_name: str) -> None:
        self._create_dir(dir_name=dir_name)
        init_file_path = f'{dir_name}/__init__.py'
        if not os.path.exists(init_file_path):
            self.log.info(f'Create: "{init_file_path}"')
            Path(init_file_path).touch()

    def _create_dir(self, dir_name: str) -> None:
        if not os.path.exists(dir_name):
            self.log.info(f'Create directory: "{dir_name}"')
            os.mkdir(dir_name)

    @classmethod
    def generation_options(cls) -> List[str]:
        return [
            key for key, value in cls.__dict__.items() if isinstance(value, FunctionType) and not key.startswith('_')
        ]


class MainGenerator(Generator):
    __PATH_TEMPLATES = os.path.dirname(os.path.realpath(__file__)) + '/templates'
    __TEMPLATE_INTERFACES = 'interfaces.py.j2'
    __TEMPLATE_SCENARIO = 'scenario.py.j2'
    __TEMPLATE_CONTEXTS = 'contexts.py.j2'
    __TEMPLATE_HELPERS = 'helpers.py.j2'
    __TEMPLATE_HELPER_METHOD = 'helper_method.j2'
    __TEMPLATE_VEDRO_CFG = 'vedro.cfg.py.j2'
    __TEMPLATE_CONFIG = 'config.py.j2'

    __DIRECTORY_INTERFACES = 'interfaces'
    __DIRECTORY_SCENARIOS = 'scenarios'
    __DIRECTORY_CONTEXTS = 'contexts'
    __DIRECTORY_HELPERS = 'helpers'

    __FILE_INTERFACES = 'api.py'
    __FILE_CONTEXTS = 'api.py'
    __FILE_HELPERS = 'helpers.py'
    __FILE_VEDRO_CFG = 'vedro.cfg.py'
    __FILE_CONFIG = 'config.py'

    def __init__(self, requests_dir: str, force: bool, log: logging.Logger):
        super().__init__(force=force, log=log)
        self.__requests_dir = requests_dir
        self.__templates = Environment(loader=FileSystemLoader(self.__PATH_TEMPLATES))

    def all(self) -> None:
        self.vedro_cfg()
        self.config()
        self.interfaces()
        self.contexts()
        self.helpers()
        self.scenarios()

    def vedro_cfg(self) -> None:
        self._generate_by_template(
            file_path=self.__FILE_VEDRO_CFG,
            template_name=self.__TEMPLATE_VEDRO_CFG
        )

    def config(self) -> None:
        self._generate_by_template(
            file_path=self.__FILE_CONFIG,
            template_name=self.__TEMPLATE_CONFIG
        )

    def interfaces(self) -> None:
        self._create_package(dir_name=self.__DIRECTORY_INTERFACES)
        self._generate_by_template(
            file_path=f'{self.__DIRECTORY_INTERFACES}/{self.__FILE_INTERFACES}',
            template_name=self.__TEMPLATE_INTERFACES
        )

    def contexts(self) -> None:
        self._create_package(dir_name=self.__DIRECTORY_CONTEXTS)
        self._generate_by_template(
            file_path=f'{self.__DIRECTORY_CONTEXTS}/{self.__FILE_CONTEXTS}',
            template_name=self.__TEMPLATE_CONTEXTS
        )

    def helpers(self) -> None:
        self._create_package(dir_name=self.__DIRECTORY_HELPERS)
        self._generate_by_template(
            file_path=f'{self.__DIRECTORY_HELPERS}/{self.__FILE_HELPERS}',
            template_name=self.__TEMPLATE_HELPERS
        )
        self.helpers_methods()

    def helpers_methods(self) -> None:
        file_path = f'{self.__DIRECTORY_HELPERS}/{self.__FILE_HELPERS}'

        with open(file_path, 'r') as file:
            content_helpers = file.read()

        with open(file_path, 'a') as f:
            for route in self._get_unique_routes():
                helper_method_name = self._get_helper_method_name(route)
                if helper_method_name not in content_helpers:
                    self.log.info(f'Generate helper: "{helper_method_name}" for route {route}')
                    template = self._get_template(self.__TEMPLATE_HELPER_METHOD)
                    f.write(template.render(helper_method_name=helper_method_name))

    def scenarios(self) -> None:
        self._create_dir(self.__DIRECTORY_SCENARIOS)
        for file_requests in self._get_file_with_requests():
            self._scenario(file_requests=file_requests, route=self._get_route(file_requests))

    def _scenario(self, file_requests: str, route: str) -> None:
        file_path = f'{self.__DIRECTORY_SCENARIOS}/{self._get_scenario_name(file_requests=file_requests)}.py'
        self._generate_by_template(
            file_path=file_path,
            template_name=self.__TEMPLATE_SCENARIO,
            requests_dir=self.__requests_dir,
            api_route=route,
            file_requests=file_requests,
            helper_method_name=self._get_helper_method_name(route)
        )

    @staticmethod
    def _get_helper_method_name(api_route: str) -> str:
        return 'prepare' + api_route.replace('/', '_').replace('.', '').replace('-', '_')

    @staticmethod
    def _get_scenario_name(file_requests: str) -> str:
        return file_requests.split('.')[0]

    def _get_file_with_requests(self) -> List[str]:
        if not os.path.exists(self.__requests_dir):
            raise DirectoryWithRequestsNotFound(f"The directory with requests: {self.__requests_dir} was not found")
        return [
            file for file in os.listdir(self.__requests_dir)
            if os.path.isfile(os.path.join(self.__requests_dir, file))
        ]

    def _get_route(self, file_path: str) -> str:
        requests = parse_requests(f'{self.__requests_dir}/{file_path}')
        return requests[0].path

    def _get_unique_routes(self) -> List[str]:
        routes = [self._get_route(file_requests) for file_requests in self._get_file_with_requests()]
        return sorted(set(routes))

    def _get_template(self, template_name: str) -> Template:
        return self.__templates.get_template(name=template_name)


def generate(args: Any) -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    log = logging.getLogger("Generator")

    try:
        getattr(MainGenerator(requests_dir=args.requests_dir, force=args.force, log=log), args.option)()
        log.info("\nThe necessary files have been generated!\n"
                 "To run the tests, you need to specify two api url to which request will be sent."
                 "You need to set environment variables in any convenient way, for example:\n"
                 "export GOLDEN_API_URL=https://golden.app && export TESTING_API_URL=https://test.app && vedro run")
    except DirectoryWithRequestsNotFound as e:
        log.critical(f"{e}. By default, the 'requests' directory was expected. "
                     "Use --requests-dir to specify another")
