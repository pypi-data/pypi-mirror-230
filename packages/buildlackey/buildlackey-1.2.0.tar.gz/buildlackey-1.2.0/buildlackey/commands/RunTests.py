
from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from pathlib import Path

from click import ClickException
from click import secho

from buildlackey.Environment import Environment
from buildlackey.PythonWarnings import PythonWarnings

STATUS_NO_SUCH_PATH: int = 23

DEFAULT_MODULE_NAME: str = 'tests.TestAll'
PYTHON_CLI:          str = 'python3'


class RunTests(Environment):
    
    def __init__(self, inputFile: str, warning: str):
        super().__init__()

        self.logger: Logger = getLogger(__name__)

        self._inputFile: str = inputFile
        if warning is None:
            self._warning: PythonWarnings = PythonWarnings.IGNORE
        else:
            try:
                self._warning = PythonWarnings(warning)
            except ValueError:
                raise ClickException(f'Invalid warning type: {warning}')

    def execute(self):

        if self.validProjectsBase is True and self.validProjectDirectory() is True:
            self._changeToProjectRoot()

        if self._inputFile is None:
            defaultCmd: str = f'{PYTHON_CLI} -W{self._warning.value} -m tests.TestAll'
            secho(f'{defaultCmd}')
            status: int = self._runCommand(command=f'python3 -W{self._warning.value} -m {DEFAULT_MODULE_NAME}')
            secho(f'{status=}')
        else:
            path: Path = Path(self._inputFile)
            if path.exists() is True:
                with path.open(mode='r') as fd:
                    moduleName: str = fd.readline()

                    while moduleName != '':
                        if moduleName != osLineSep and not moduleName.startswith('#'):
                            # noinspection SpellCheckingInspection
                            cmd: str = f'{PYTHON_CLI} -W{self._warning.value} -m {moduleName}'
                            secho(f'{cmd}')
                            status = self._runCommand(command=cmd)
                            if status != 0:
                                exit(status)
                        moduleName = fd.readline()
            else:
                secho(f'No such file: {self._inputFile}')
                exit(STATUS_NO_SUCH_PATH)
