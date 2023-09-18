from pathlib import Path

from versionoverlord.exceptions.NoFileException import NoFileException


class NoSetupPyFileException(NoFileException):

    def __init__(self, fullPath: Path):

        super().__init__(missingFilePath=fullPath)

    @property
    def fullSetupPyPath(self) -> Path:
        return self._missingFilePath
