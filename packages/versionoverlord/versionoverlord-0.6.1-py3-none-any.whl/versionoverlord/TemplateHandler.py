
from typing import List

from logging import Logger
from logging import getLogger

from pathlib import Path

from os import linesep as osLineSep

from codeallybasic.SemanticVersion import SemanticVersion

from versionoverlord.Common import REQUIREMENTS_TXT
from versionoverlord.Common import SPECIFICATION_FILE
from versionoverlord.Common import Slugs

from versionoverlord.DisplayVersions import SlugVersion
from versionoverlord.DisplayVersions import SlugVersions
from versionoverlord.EnvironmentBase import EnvironmentBase
from versionoverlord.GitHubAdapter import GitHubAdapter


class TemplateHandler(EnvironmentBase):

    def __init__(self, slugs: Slugs):

        super().__init__()

        self.logger: Logger = getLogger(__name__)
        self._slugs: Slugs  = slugs

        requirementsPath:      Path      = Path(self._projectsBase) / self._projectDirectory / REQUIREMENTS_TXT
        self._requirementsTxt: List[str] = requirementsPath.read_text().split(osLineSep)

    def createSpecification(self):
        print(f'Creating a specification')
        versionOverlord: GitHubAdapter = GitHubAdapter()

        slugVersions: SlugVersions = SlugVersions([])
        for slug in self._slugs:
            version: SemanticVersion = versionOverlord.getLatestVersionNumber(slug)
            slugVersion: SlugVersion = SlugVersion(slug=slug, version=str(version))
            slugVersions.append(slugVersion)

        versionUpdateSpecification: Path = Path(SPECIFICATION_FILE)
        with versionUpdateSpecification.open(mode='w') as fd:
            fd.write(f'PackageName,OldVersion,NewVersion{osLineSep}')
            for slugVersion in slugVersions:
                oldVersion: str = self._findRequirementVersion(self._extractPackageName(slugVersion.slug))
                if oldVersion == '':
                    print(f'{slugVersion.slug} Did not find requirement')
                else:
                    pkgName:    str = self._extractPackageName(slug=slugVersion.slug)
                    fd.write(f'{pkgName},{oldVersion},{slugVersion.version}{osLineSep}')

    def _extractPackageName(self, slug: str) -> str:
        splitSlug: List[str] = slug.split(sep='/')

        pkgName: str = splitSlug[1]
        return pkgName

    def _findRequirementVersion(self, packageName: str) -> str:
        """
        Can handle requirements specifications like:
        pkgName==versionNumber
        pkgName~=versionNumber

        Args:
            packageName:   The package name to search for

        Returns:  A version number from the requirement file that matches the package name
                 If the requirement is not listed returns an empty string
        """
        lookupRequirement: str = f'{packageName}=='

        req: List[str] = self._searchRequirements(lookupRequirement)
        if len(req) == 0:
            lookupRequirement = f'{packageName}~='      # did not find '=='  how about '~='
            req = self._searchRequirements(lookupRequirement)
            if len(req) == 0:
                splitRequirement: List[str]  = ['', '']
            else:
                splitRequirement = req[0].split('~=')
        else:
            splitRequirement = req[0].split('==')

        return splitRequirement[1]

    def _searchRequirements(self, reqLine: str) -> List[str]:
        req = [match for match in self._requirementsTxt if reqLine in match]
        return req
