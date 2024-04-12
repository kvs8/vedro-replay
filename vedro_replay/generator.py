import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from types import FunctionType
from typing import Any, List

from jinja2 import Environment, FileSystemLoader, Template


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

    def _create_package(self, dirname: str) -> None:
        self._create_dir(dirname)
        init_file_path = os.path.join(dirname, '__init__.py')
        if not os.path.exists(init_file_path):
            self.log.info(f'Create: "{init_file_path}"')
            Path(init_file_path).touch()

    def _create_dir(self, dirname: str) -> None:
        if dirname and not os.path.exists(dirname):
            self.log.info(f'Create directory: "{dirname}"')
            os.makedirs(dirname)

    @classmethod
    def generation_options(cls) -> List[str]:
        return [
            key for key, value in cls.__dict__.items() if isinstance(value, FunctionType) and not key.startswith('_')
        ]


class MainGenerator(Generator):
    __PATH_TEMPLATES = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
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
        self._create_package(dirname=self.__DIRECTORY_INTERFACES)
        self._generate_by_template(
            file_path=os.path.join(self.__DIRECTORY_INTERFACES, self.__FILE_INTERFACES),
            template_name=self.__TEMPLATE_INTERFACES
        )

    def contexts(self) -> None:
        self._create_package(dirname=self.__DIRECTORY_CONTEXTS)
        self._generate_by_template(
            file_path=os.path.join(self.__DIRECTORY_CONTEXTS, self.__FILE_CONTEXTS),
            template_name=self.__TEMPLATE_CONTEXTS
        )

    def helpers(self) -> None:
        self._create_package(dirname=self.__DIRECTORY_HELPERS)
        self._generate_by_template(
            file_path=os.path.join(self.__DIRECTORY_HELPERS, self.__FILE_HELPERS),
            template_name=self.__TEMPLATE_HELPERS
        )
        self.helpers_methods()

    def helpers_methods(self) -> None:
        file_path = os.path.join(self.__DIRECTORY_HELPERS, self.__FILE_HELPERS)

        with open(file_path, 'r') as file:
            content_helpers = file.read()

        with open(file_path, 'a') as f:
            for file_with_requests in self._get_file_paths_with_requests():
                helper_method_name = self._get_helper_method_name(file_with_requests)
                if helper_method_name not in content_helpers:
                    self.log.info(f'Generate helper: "{helper_method_name}" for file {file_with_requests}')
                    template = self._get_template(self.__TEMPLATE_HELPER_METHOD)
                    f.write(template.render(helper_method_name=helper_method_name))

    def scenarios(self) -> None:
        self._create_dir(self.__DIRECTORY_SCENARIOS)
        for file_path_with_requests in self._get_file_paths_with_requests():
            self._scenario(file_path_with_requests)

    def _scenario(self, file_path_with_requests: str) -> None:
        dirname = os.path.dirname(file_path_with_requests.replace(f'{self.__requests_dir}/', '', 1))
        self._create_dir(os.path.join(self.__DIRECTORY_SCENARIOS, dirname))
        self._generate_by_template(
            file_path=os.path.join(
                self.__DIRECTORY_SCENARIOS, dirname, f'{self._get_scenario_name(file_path_with_requests)}.py'
            ),
            template_name=self.__TEMPLATE_SCENARIO,
            file_path_with_requests=file_path_with_requests,
            helper_method_name=self._get_helper_method_name(file_path_with_requests)
        )

    @classmethod
    def _get_helper_method_name(cls, file_path_with_requests: str) -> str:
        return 'prepare_' + cls._get_scenario_name(file_path_with_requests)

    @staticmethod
    def _get_scenario_name(file_path_with_requests: str) -> str:
        return os.path.basename(file_path_with_requests).split('.')[0].replace('-', '_')

    def _get_file_paths_with_requests(self) -> List[str]:
        if not os.path.exists(self.__requests_dir):
            raise DirectoryWithRequestsNotFound(f"The directory with requests: {self.__requests_dir} was not found")

        file_with_requests = []
        for root, _, files in os.walk(self.__requests_dir):
            for file in files:
                if file.endswith('.txt') or file.endswith('.http'):
                    file_with_requests.append(os.path.join(root, file))
        return file_with_requests

    def _get_template(self, template_name: str) -> Template:
        return self.__templates.get_template(name=template_name)


def generate(args: Any) -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    log = logging.getLogger("Generator")

    try:
        getattr(MainGenerator(requests_dir=args.requests_dir, force=args.force, log=log), args.option)()
        log.info("The necessary files have been generated!\n"
                 "To run the tests, you need to specify two api url to which request will be sent."
                 "You need to set environment variables in any convenient way, for example:\n"
                 "GOLDEN_API_URL=https://golden.app TESTING_API_URL=https://test.app vedro run -v")
    except DirectoryWithRequestsNotFound as e:
        log.critical(f"{e}. By default, the 'requests' directory was expected. "
                     "Use --requests-dir to specify another")
