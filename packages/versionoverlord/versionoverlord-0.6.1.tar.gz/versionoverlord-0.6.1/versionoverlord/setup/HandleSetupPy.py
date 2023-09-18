
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from re import sub as regexSubstitute

from os import sep as osSep

from tempfile import mkstemp

from versionoverlord.Common import INSTALL_REQUIRES
from versionoverlord.Common import SETUP_PY
from versionoverlord.Common import Packages
from versionoverlord.Common import UpdateDependencyCallback
from versionoverlord.Common import UpdatePackage

from versionoverlord.exceptions.NoSetupPyFileException import NoSetupPyFileException

from versionoverlord.BaseHandler import BaseHandler


class HandleSetupPy(BaseHandler):
    """
    Handles the setup.py file
    """
    def __init__(self, packages: Packages):
        self.logger: Logger = getLogger(__name__)
        super().__init__(packages)

    def update(self):
        """
        Updates a project's setup.py file.  Updates the "requires"
        """
        setupPyPath: Path = Path(f'{self._projectsBase}{osSep}{self._projectDirectory}{osSep}{SETUP_PY}')

        if setupPyPath.exists() is False:
            raise NoSetupPyFileException(fullPath=setupPyPath)

        self.logger.info(f'Working on: `{setupPyPath}`')

        osHandle, tempFile = mkstemp(text=True)
        self._fixDependencies(searchFile=setupPyPath, tempFile=tempFile, searchItems=[INSTALL_REQUIRES],
                              callback=UpdateDependencyCallback(self._updateRequires))

        # Replace with updated contents
        tempFilePath: Path = Path(tempFile)
        tempFilePath.rename(setupPyPath)

    def _updateRequires(self, contentLine: str) -> str:
        """
        Updates the "requires" string
        Handles "==" and "~=" types

        Args:
            contentLine: The line to update

        Returns:  The updated string
        """
        updatedLine: str = contentLine
        for pkg in self._packages:
            package: UpdatePackage = cast(UpdatePackage, pkg)

            equalPrefix:  str = f'{package.packageName}=='
            almostPrefix: str = f'{package.packageName}~='

            equalPattern:  str = f'{equalPrefix}{str(package.oldVersion)}'
            almostPattern: str = f'{almostPrefix}{str(package.oldVersion)}'
            repl:          str = f'{equalPrefix}{str(package.newVersion)}'

            # run both changes in case the requirement is == or ~=
            updatedLine = regexSubstitute(pattern=equalPattern,  repl=repl, string=updatedLine)
            updatedLine = regexSubstitute(pattern=almostPattern, repl=repl, string=updatedLine)

        assert len(updatedLine) != 0, 'Developer error, bad regex'

        return updatedLine
