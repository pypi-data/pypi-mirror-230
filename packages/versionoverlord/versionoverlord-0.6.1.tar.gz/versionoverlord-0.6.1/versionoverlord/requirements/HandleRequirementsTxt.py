
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from os import sep as osSep

from pathlib import Path

from tempfile import mkstemp

from re import match as regExMatch
from re import Match

from versionoverlord.Common import REQUIREMENTS_TXT

from versionoverlord.Common import PackageName
from versionoverlord.Common import Packages
from versionoverlord.Common import UpdateDependencyCallback
from versionoverlord.Common import UpdatePackage

from versionoverlord.exceptions.NoRequirementsTxtsException import NoRequirementsTxtException

from versionoverlord.BaseHandler import BaseHandler


class HandleRequirementsTxt(BaseHandler):

    def __init__(self, packages: Packages):

        self.logger: Logger = getLogger(__name__)

        super().__init__(packages)

    def update(self):

        requirementsTxtPath: Path = Path(f'{self._projectsBase}{osSep}{self._projectDirectory}{osSep}{REQUIREMENTS_TXT}')

        if requirementsTxtPath.exists() is False:
            raise NoRequirementsTxtException(fullPath=requirementsTxtPath)

        self.logger.info(f'Working on: `{requirementsTxtPath}`')

        osHandle, tempFile = mkstemp(text=True)

        searchItems: List[str] = self._buildSearchItems()
        self._fixDependencies(searchFile=requirementsTxtPath, tempFile=tempFile, searchItems=searchItems,
                              callback=UpdateDependencyCallback(self._updateRequirementsLine))

        # Replace with updated contents
        tempFilePath: Path = Path(tempFile)
        tempFilePath.rename(requirementsTxtPath)

    def _updateRequirementsLine(self, contentLine: str) -> str:
        """
        Update lines like 'ogl==0.70.20'
        Args:
            contentLine:

        Returns:  The updates requirement line
        """
        regex: str          = ".+?(?===)"        # match everything to the left of the '==' sign
        match: Match | None = regExMatch(regex, contentLine)
        if match is None:
            regex = ".+?(?=~=)"         # match everything to the left of the '~=' sign
            match = regExMatch(regex, contentLine)

        assert match, 'We should only come here on valid packages'

        pkgNameStr: str = match.group(0)
        updatePackage: UpdatePackage = self._packageDict[PackageName(pkgNameStr)]

        self.logger.debug(f'{pkgNameStr}')
        newRequirement: str = contentLine.replace(str(updatePackage.oldVersion), str(updatePackage.newVersion))

        return newRequirement

    def _buildSearchItems(self) -> List[str]:
        searchItems: List[str] = []

        for pkg in self._packages:
            updatePackage: UpdatePackage = cast(UpdatePackage, pkg)

            equalSearchItem:  str = f'{updatePackage.packageName}=={str(updatePackage.oldVersion)}'
            almostSearchItem: str = f'{updatePackage.packageName}~={updatePackage.oldVersion.__str__()}'
            searchItems.append(equalSearchItem)
            searchItems.append(almostSearchItem)

        return searchItems
