
import pathlib
from setuptools import setup

from buildlackey import __version__ as version
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README  = (HERE / "README.md").read_text()
LICENSE = (HERE / 'LICENSE').read_text()

setup(
    name="buildlackey",
    version=version,
    author='Humberto A. Sanchez II',
    author_email='humberto.a.sanchez.ii@gmail.com',
    maintainer='Humberto A. Sanchez II',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='Project Maintenance Scripts',
    long_description=README,
    long_description_content_type="text/markdown",
    license=LICENSE,
    url="https://github.com/buildlackey",
    packages=[
        'buildlackey',
        'buildlackey.commands',
        'buildlackey.exceptions',
        'buildlackey.resources',
    ],
    package_data={
        'buildlackey.resources': ['loggingConfiguration.json', 'version.txt'],
    },

    install_requires=[
        'codeallybasic==0.5.2',
        'click~=8.1.7',
    ],
    entry_points={
        "console_scripts": [
            "runtests=buildlackey.Commands:runtests",
            "cleanup=buildlackey.Commands:cleanup",
            "runmypy=buildlackey.Commands:runmypy",
            "package=buildlackey.Commands:package",
            "prodpush=buildlackey.Commands:prodpush",
        ]
    },
)
