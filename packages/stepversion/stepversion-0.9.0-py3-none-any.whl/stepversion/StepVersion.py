
from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from importlib.abc import Traversable

from importlib.resources import files

from click import ClickException
from click import clear
from click import command
from click import option
from click import secho
from click import version_option

from click import echo as clickEcho

from codeallybasic.Environment import Environment
from codeallybasic.SemanticVersion import SemanticVersion

from stepversion import __version__

DEFAULT_FILE_NAME: str = '_version.py'
VERSION_CODE:      str = '__version__: str = '


class StepVersion(Environment):
    def __init__(self, *, major: int, minor: int, patch: int, packageName: str):

        super().__init__(printCallback=self._printCallback)
        self.logger: Logger = getLogger(__name__)

        self._major:       int = major
        self._minor:       int = minor
        self._patch:       int = patch
        self._packageName: str = packageName

    def update(self):
        semanticVersion: SemanticVersion = self._readVersionFile()
        secho(f'Current Version: {semanticVersion}')
        semanticVersion = self._updateVersion(semanticVersion)

        secho(f'New Version: {semanticVersion}')
        self._writeVersionFile(semanticVersion)

    def _readVersionFile(self) -> SemanticVersion:

        packageName: str = self._computePackageName()
        fqFileName:  str = self._getFullyQualifiedVersionFileName(package=packageName, fileName=DEFAULT_FILE_NAME)

        with open(fqFileName, 'r') as versionFile:
            versionLine: str = versionFile.read()

        justVersion:     str             = versionLine.split('=')[1].strip(osLineSep).strip("'").lstrip(" ").lstrip("'")
        semanticVersion: SemanticVersion = SemanticVersion(justVersion)

        return semanticVersion

    def _updateVersion(self, semanticVersion: SemanticVersion) -> SemanticVersion:
        if self._major is not None:
            semanticVersion.major = semanticVersion.major + self._major
        if self._minor is not None:
            semanticVersion.minor = semanticVersion.minor + self._minor
        if self._patch is not None:
            semanticVersion.patch = semanticVersion.patch + self._patch

        return semanticVersion

    def _writeVersionFile(self, semanticVersion: SemanticVersion):

        packageName: str = self._computePackageName()
        fqFileName:  str = self._getFullyQualifiedVersionFileName(package=packageName, fileName=DEFAULT_FILE_NAME)

        with open(fqFileName, 'w') as versionFile:
            versionFile.write(f"{VERSION_CODE}'{semanticVersion}'")
            versionFile.write(osLineSep)

    def _printCallback(self, message: str):
        secho(f'{message}', color=True, reverse=True)

    def _getFullyQualifiedVersionFileName(self, package: str, fileName: str) -> str:
        """
        Use this method to get other unit test resources
        Args:
            package:    The fully qualified package name (dot notation)
            fileName:   The resources file name

        Returns:  A fully qualified path name
        """

        traversable: Traversable = files(package) / fileName

        return str(traversable)

    def _computePackageName(self) -> str:

        if self._packageName is None:
            packageName: str = self._projectDirectory
        else:
            packageName = self._packageName

        return packageName

@command()
@version_option(version=f'{__version__}', message='%(version)s')
@option('-m', '--major',        type=int, is_flag=False, flag_value=1, help='Bump major version (default 1)')
@option('-i', '--minor',        type=int, is_flag=False, flag_value=1, help='Bump minor version (default 1)')
@option('-p', '--patch',        type=int, is_flag=False, flag_value=1, help='Bump patch version (default 1)')
@option('-a', '--package-name', type=str, help='Use this option when the package name does not match the project name')
def commandHandler(major: int, minor: int, patch: int, package_name: str):
    """

    Args:
        major:
        minor:
        patch:
        package_name

    Returns:

    """

    if major is None and minor is None and patch is None:
        raise ClickException('You must provide one option on what to patch.')
    clear()
    clickEcho(f'{major=} {minor=} {patch=}')
    stepVersion: StepVersion = StepVersion(major=major, minor=minor, patch=patch, packageName=package_name)
    secho('')
    stepVersion.update()


if __name__ == "__main__":

    commandHandler(['-p', '1', '-a', 'stepversion'])
