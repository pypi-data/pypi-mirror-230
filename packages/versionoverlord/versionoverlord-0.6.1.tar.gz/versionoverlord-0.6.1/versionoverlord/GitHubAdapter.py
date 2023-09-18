
from typing import cast

from logging import Logger
from logging import getLogger

from collections import Counter

from os import environ as osEnvironment

from github import Github
from github import UnknownObjectException

from github.GitRelease import GitRelease
from github.PaginatedList import PaginatedList
from github.Repository import Repository

from codeallybasic.SemanticVersion import SemanticVersion

from versionoverlord.exceptions.NoGitHubAccessTokenException import NoGitHubAccessTokenException
from versionoverlord.exceptions.UnknownGitHubRepositoryException import UnknownGitHubRepositoryException


class GitHubAdapter:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        try:
            gitHubToken: str = osEnvironment['GITHUB_ACCESS_TOKEN']
        except KeyError:
            raise NoGitHubAccessTokenException

        self._github: Github = Github(gitHubToken)

    def getLatestVersionNumber(self, repositorySlug: str) -> SemanticVersion:

        try:
            repo: Repository = self._github.get_repo(repositorySlug)
            self.logger.debug(f'{repo.full_name=}')
        except UnknownObjectException:
            raise UnknownGitHubRepositoryException(repositorySlug=repositorySlug)

        releases: PaginatedList = repo.get_releases()

        latestReleaseVersion: SemanticVersion = SemanticVersion('0.0.0')
        for release in releases:
            gitRelease: GitRelease = cast(GitRelease, release)

            if gitRelease.draft is True:
                self.logger.warning(f'{repo.full_name} Ignore pre-release {gitRelease.tag_name}')
                continue
            releaseNumber: str = gitRelease.tag_name
            numPeriods: int = self._countPeriods(releaseNumber)
            if numPeriods < 2:
                releaseNumber = f'{releaseNumber}.0'

            releaseVersion: SemanticVersion = SemanticVersion(releaseNumber)
            self.logger.debug(f'{releaseVersion=}')
            if latestReleaseVersion < releaseVersion:
                latestReleaseVersion = releaseVersion

        return latestReleaseVersion

    def _countPeriods(self, releaseNumber: str) -> int:

        cnt = Counter(list(releaseNumber))
        return cnt['.']
