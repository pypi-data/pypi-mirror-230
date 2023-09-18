
from pathlib import Path

from versionoverlord.exceptions.NoFileException import NoFileException


class NoRequirementsTxtException(NoFileException):
    def __init__(self, fullPath: Path):

        super().__init__(missingFilePath=fullPath)

    @property
    def fullRequirementsTxtPath(self) -> Path:
        return self._missingFilePath
