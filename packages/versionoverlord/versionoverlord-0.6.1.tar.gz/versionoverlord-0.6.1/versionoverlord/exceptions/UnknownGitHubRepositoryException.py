class UnknownGitHubRepositoryException(Exception):

    def __init__(self, repositorySlug: str):

        self._repositorySlug: str = repositorySlug

    @property
    def repositorySlug(self) -> str:
        return self._repositorySlug
