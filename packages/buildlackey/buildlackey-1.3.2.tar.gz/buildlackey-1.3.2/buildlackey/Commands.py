
import logging
import logging.config

from importlib.resources import files
from importlib.abc import Traversable

from json import load as jsonLoad

from click import command
from click import option
from click import version_option

from buildlackey import __version__ as version

from buildlackey.commands.Cleanup import Cleanup
from buildlackey.commands.Package import Package
from buildlackey.commands.ProductionPush import ProductionPush
from buildlackey.commands.RunMypy import RunMypy
from buildlackey.commands.RunTests import RunTests


RESOURCES_PACKAGE_NAME:       str = 'buildlackey.resources'
JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"

"""
Put in type ignore because of strange error on that appeared on 8.1.4

buildlackey/Commands.py:80: error: Argument 1 has incompatible type "Callable[[], Any]"; expected <nothing>  [arg-type]
    @command
"""


def setUpLogging():
    """
    """
    traversable: Traversable = files(RESOURCES_PACKAGE_NAME) / JSON_LOGGING_CONFIG_FILENAME

    loggingConfigFilename: str = str(traversable)

    with open(loggingConfigFilename, 'r') as loggingConfigurationFile:
        configurationDictionary = jsonLoad(loggingConfigurationFile)

    logging.config.dictConfig(configurationDictionary)
    logging.logProcesses = False
    logging.logThreads = False


@command
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
@option('--input-file', '-i', required=False,   help='Use input file to list the unit tests to execute')
@option('--warning',    '-w', required=False,   help='Use this option to control Python warnings')
def runtests(input_file: str, warning: str):
    """
    \b
    Runs the unit tests for the project specified by the environment variables listed below;
    \b
    Use the -i/--input-file option to list a set of module names to execute as your
    unit tests

    Legal values for -w/--warning are:

    \b
        default
        error
        always
        module
        once
        ignore
    \b
    Environment Variables

        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name

    \b
    \b
    However, if one or the other is not defined the command assumes it is executing in a CI
    environment and thus the current working directory is the project base directory.

    By default, buildlackey runs the module named tests.TestAll
    """
    setUpLogging()
    runTests: RunTests = RunTests(inputFile=input_file, warning=warning)

    runTests.execute()


@command
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
@option('--package-name', '-p', required=False, help='Use this option when the package name does not match the project name')
def cleanup(package_name: str):
    """
    \b
    Clean the build artifacts for the project specified by the following environment variables
    \b
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name

    PROJECT is overridden if the developer specifies a package name
    """
    setUpLogging()
    clean: Cleanup = Cleanup(packageName=package_name)

    clean.execute()


@command
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
@option('--package-name', '-p', required=False, help='Use this option when the package name does not match the project name')
def runmypy(package_name: str):
    """
    \b
    Runs the mypy checks for the project specified by the following environment variables
    \b
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name

    PROJECT is overridden if the developer specifies a package name
    """
    runMyPy: RunMypy = RunMypy(packageName=package_name)
    runMyPy.execute()


@command
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
@option('--input-file', '-i', required=False,   help='Use input file to specify a set of commands to execute')
def package(input_file: str):
    """
    \b
    Creates the deployable for the project specified by the environment variables listed below
    \b
    Use the -i/--input-file option to specify a set of custom commands to execute to build
    your deployable

    Environment Variables
    \b
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name

    """
    setUpLogging()
    pkg: Package = Package(inputFile=input_file)

    pkg.execute()


@command
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
def prodpush():
    """
    \b
    Pushes the deployable to pypi.  The project is specified by the following environment variables
    \b
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name
    """
    productionPush: ProductionPush = ProductionPush()
    productionPush.execute()


if __name__ == "__main__":
    runtests([])
    # noinspection SpellCheckingInspection
    # runmypy(['-p', 'codeallyadvanced'])
    # runtests(['-i', 'tests/unittest.txt'])
    # cleanup(['--help'])
    # deploy(['--help'])
