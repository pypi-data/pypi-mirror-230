
from pathlib import Path
from typing import Tuple
from typing import cast

from click import command
from click import option
from click import secho
from click import version_option

from versionoverlord.Common import __version__
from versionoverlord.Common import Slugs
from versionoverlord.Common import setUpLogging
from versionoverlord.FileNameToSlugs import FileNameToSlugs
from versionoverlord.TemplateHandler import TemplateHandler


@command()
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
@option('--slugs',     '-s',  multiple=True, required=False, help='Create package update specification')
@option('--input-file', '-i', required=False,                help='Use input file for slug list')
def createSpecification(slugs: Tuple[str], input_file: str):
    """
    \b
    This command creates .csv specification file
    It uses the following environment variables:
    \b
        GITHUB_ACCESS_TOKEN - A personal GitHub access token necessary to read repository release information
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name
    """

    if len(slugs) != 0:
        templateHandler: TemplateHandler = TemplateHandler(slugs=cast(Slugs, slugs))
        templateHandler.createSpecification()
    elif input_file is not None:
        fqFileName: Path = Path(input_file)
        if fqFileName.exists() is False:
            secho('                          ', fg='red', bg='black', bold=True)
            secho('Input file does not exist ', fg='red', bg='black', bold=True)
            secho('                          ', fg='red', bg='black', bold=True)
        else:
            fileNameToSlugs: FileNameToSlugs = FileNameToSlugs(path=fqFileName)
            inputSlugs:      Slugs           = fileNameToSlugs.getSlugs()

            templateHandler = TemplateHandler(slugs=inputSlugs)
            templateHandler.createSpecification()


if __name__ == "__main__":
    setUpLogging()
    createSpecification(['-i', 'tests/resources/testdata/query.slg'])
