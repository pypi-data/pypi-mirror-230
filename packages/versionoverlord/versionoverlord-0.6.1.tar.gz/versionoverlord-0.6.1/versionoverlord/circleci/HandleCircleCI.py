
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from os import sep as osSep

from pathlib import Path

from tempfile import mkstemp

from re import match as regExMatch
from re import Match

from versionoverlord.Common import CIRCLE_CI_DIRECTORY
from versionoverlord.Common import CIRCLE_CI_YAML

from versionoverlord.BaseHandler import BaseHandler
from versionoverlord.Common import PackageName
from versionoverlord.Common import Packages
from versionoverlord.Common import UpdateDependencyCallback
from versionoverlord.Common import UpdatePackage
from versionoverlord.exceptions.NotACircleCIProjectException import NotACircleCIProjectException

PIP_COMMAND: str = 'pip install'


class HandleCircleCI(BaseHandler):

    def __init__(self, packages: Packages):
        self.logger: Logger = getLogger(__name__)
        super().__init__(packages)

    def update(self):

        circleCIYAML: Path = Path(f'{self._projectsBase}{osSep}{self._projectDirectory}{osSep}{CIRCLE_CI_DIRECTORY}{osSep}{CIRCLE_CI_YAML}')

        if circleCIYAML.exists() is False:
            raise NotACircleCIProjectException()

        osHandle, tempFile = mkstemp(text=True)

        searchItems: List[str] = self._buildSearchItems()

        self._fixDependencies(searchFile=circleCIYAML, tempFile=tempFile, searchItems=searchItems, callback=UpdateDependencyCallback(self._updateInstallLine))

        # Replace with updated contents
        tempFilePath: Path = Path(tempFile)
        tempFilePath.rename(circleCIYAML)

    def _updateInstallLine(self, contentLine: str) -> str:
        """
        Update lines like 'pip install ogl==0.70.20'

        Args:
            contentLine:

        Returns:  The updated line
        """
        updatePackage: UpdatePackage = self._getUpdatePackage(contentLine=contentLine)

        updatedLine: str = contentLine.replace(str(updatePackage.oldVersion), str(updatePackage.newVersion))

        return updatedLine

    def _buildSearchItems(self) -> List[str]:
        searchItems: List[str] = []

        for pkg in self._packages:
            updatePackage: UpdatePackage = cast(UpdatePackage, pkg)

            equalSearchItem:  str = f'{PIP_COMMAND} {updatePackage.packageName}=={str(updatePackage.oldVersion)}'
            almostSearchItem: str = f'{PIP_COMMAND} {updatePackage.packageName}~={str(updatePackage.oldVersion)}'
            searchItems.append(equalSearchItem)
            searchItems.append(almostSearchItem)

        return searchItems

    def _getUpdatePackage(self, contentLine: str) -> UpdatePackage:

        regex: str   = ".+?(?===)"       # match everything to the left of the '==' sign
        match: Match | None = regExMatch(regex, contentLine)
        if match is None:
            regex = ".+?(?=~=)"         # match everything to the left of the '~=' sign
            match = regExMatch(regex, contentLine)

        assert match, 'We should only come here on valid packages'

        pipInstallStr: str = match.group(0)
        pkgNameStr:    str = self._pkgNameOnly(s=pipInstallStr)

        updatePackage: UpdatePackage = self._packageDict[PackageName(pkgNameStr)]

        return updatePackage

    def _pkgNameOnly(self, s: str):
        return s.partition('install ')[2]
