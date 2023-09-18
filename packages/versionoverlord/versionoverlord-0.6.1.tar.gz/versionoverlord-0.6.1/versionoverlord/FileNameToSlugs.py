
from typing import cast
from typing import List

from logging import Logger
from logging import getLogger

from pathlib import Path

from os import linesep as osLineSep

from versionoverlord.Common import Slugs


class FileNameToSlugs:
    def __init__(self, path: Path):
        self.logger: Logger = getLogger(__name__)

        self._fqFileName: Path = path

    def getSlugs(self) -> Slugs:

        slugString: str        = self._fqFileName.read_text()
        slugList:   List[str] = slugString.split(sep=osLineSep)

        cleanList: List[str] = list(filter(None, slugList))
        return cast(Slugs, tuple(cleanList))
