
from typing import NewType
from typing import List

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from curses import initscr
from curses import noecho
from curses import cbreak
from curses import endwin
from curses import nocbreak
from curses import echo

from _curses import A_UNDERLINE


PACKAGE_VERSION_GAP: int = 2
TITLE_LINE_GAP:      int = 2


@dataclass
class SlugVersion:
    slug:    str = ''
    version: str = ''


SlugVersions = NewType('SlugVersions', List[SlugVersion])


class DisplayVersions:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._stdScreen = initscr()

    def displaySlugs(self, slugVersions: SlugVersions):

        self._initializeCurses()

        longest:      int = self._getLongest(slugVersions)
        lineNumber:   int = 0
        columnNumber: int = 0
        packageColumnNumber: int = longest + PACKAGE_VERSION_GAP

        self._stdScreen.addstr(lineNumber, columnNumber,        'Slug',    A_UNDERLINE)
        self._stdScreen.addstr(lineNumber, packageColumnNumber, 'Version', A_UNDERLINE)

        lineNumber += TITLE_LINE_GAP
        for slugVersion in slugVersions:

            self._stdScreen.addstr(lineNumber, columnNumber,        f'{slugVersion.slug}:')
            self._stdScreen.addstr(lineNumber, packageColumnNumber, f'{slugVersion.version}')
            lineNumber += 1

        self._stdScreen.addstr(lineNumber + 1, columnNumber, 'Press any key to continue...')
        # noinspection PyUnusedLocal
        s = self._stdScreen.getch()

        self._done()

    def _initializeCurses(self):
        noecho()
        cbreak()
        self._stdScreen.keypad(True)

    def _done(self):
        nocbreak()
        self._stdScreen.keypad(False)
        echo()
        endwin()

    def _getLongest(self, slugVersions: SlugVersions) -> int:
        longest: int = 0
        for slugVersion in slugVersions:
            if len(slugVersion.slug) > longest:
                longest = len(slugVersion.slug)

        return longest
