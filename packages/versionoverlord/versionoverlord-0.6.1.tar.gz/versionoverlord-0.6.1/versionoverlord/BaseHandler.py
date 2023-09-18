
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from abc import ABC
from abc import abstractmethod

from pathlib import Path

from tempfile import gettempdir

from versionoverlord.Common import PackageLookupType
from versionoverlord.Common import Packages
from versionoverlord.Common import UpdateDependencyCallback
from versionoverlord.Common import UpdatePackage

from versionoverlord.EnvironmentBase import EnvironmentBase


class BaseHandler(ABC, EnvironmentBase):
    def __init__(self, packages: Packages):

        self._packages:  Packages = packages
        self.baseLogger: Logger   = getLogger(__name__)

        super().__init__()

        self._packageDict: PackageLookupType = self._buildPackageLookup()

    @abstractmethod
    def update(self):
        """
        Updates a project's file.
        """
        pass

    def _fixDependencies(self, searchFile: Path, tempFile: str, searchItems: List[str], callback: UpdateDependencyCallback):
        """

        Args:
            searchFile:     The file we will iterate through
            tempFile:       The temporary file to write the changed file
            searchItems:    A list of strings to find
            callback:       The method to call when we find a match;
        """
        self.baseLogger.debug(f'{searchItems=}')
        self.baseLogger.debug(f'{tempFile=}')
        with open(searchFile, 'r') as inputFd:
            with open(tempFile, 'w') as tempFileFd:
                self.baseLogger.debug(f'tempDir: {gettempdir()}')
                while True:
                    contentLine: str = inputFd.readline()
                    if not contentLine:
                        break

                    # Check to see if we need to modify this line
                    for searchText in searchItems:
                        if searchText in contentLine:
                            contentLine = callback(contentLine)
                            self.baseLogger.debug(f'{contentLine=}')
                    tempFileFd.write(contentLine)

    def _buildPackageLookup(self) -> PackageLookupType:

        lookupDict: PackageLookupType = PackageLookupType({})

        for pkg in self._packages:
            updatePackage: UpdatePackage = cast(UpdatePackage, pkg)
            lookupDict[updatePackage.packageName] = updatePackage

        return lookupDict
