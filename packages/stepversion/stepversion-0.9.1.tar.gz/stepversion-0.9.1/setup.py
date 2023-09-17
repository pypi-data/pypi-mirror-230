import pathlib
from setuptools import setup

from stepversion import __version__ as versionNumber

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
LICENSE = (HERE / 'LICENSE').read_text()

setup(
    name="stepversion",
    version=versionNumber,
    author='Humberto A. Sanchez II',
    author_email='humberto.a.sanchez.ii@gmail.com',
    maintainer='Humberto A. Sanchez II',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='Bump package versions',
    long_description=README,
    long_description_content_type="text/markdown",
    license=LICENSE,
    url="https://github.com/hasii2011/stepversion",
    packages=[
        'stepversion'
    ],
    install_requires=['click==8.1.7'],
    entry_points={
        "console_scripts": [
            "stepversion=stepversion.StepVersion:commandHandler",
        ],
    },
)
