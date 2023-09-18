from click import clear
from click import command
from click import secho

from click import version_option


from versionoverlord.Common import __version__


@command()
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
def versionOverlord():
    clear()
    secho('Commands are:')
    secho('\tquerySlugs')
    secho('\tcreateSpecification:')
    secho('\tupdateDependencies')
    