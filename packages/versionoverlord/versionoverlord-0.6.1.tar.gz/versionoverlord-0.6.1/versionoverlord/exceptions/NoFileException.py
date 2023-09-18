from pathlib import Path


class NoFileException(Exception):

    def __init__(self, missingFilePath: Path):

        self._missingFilePath: Path = missingFilePath
