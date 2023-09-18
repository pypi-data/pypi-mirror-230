
import pathlib
from setuptools import setup

from versionoverlord import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
LICENSE = (HERE / 'LICENSE').read_text()

DATA_FILES = [
    ('versionoverlord/resources', ['versionoverlord/resources/loggingConfiguration.json']),
]

setup(
    name="versionoverlord",
    version=__version__,
    author='Humberto A. Sanchez II',
    author_email='humberto.a.sanchez.ii@gmail.com',
    maintainer='Humberto A. Sanchez II',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='Dependency Manager',
    long_description=README,
    long_description_content_type="text/markdown",
    license=LICENSE,
    url="https://github.com/versionoverlord",
    data_files=DATA_FILES,
    packages=[
        'versionoverlord',
        'versionoverlord.circleci',
        'versionoverlord.commands',
        'versionoverlord.exceptions',
        'versionoverlord.requirements',
        'versionoverlord.resources',
        'versionoverlord.setup'
    ],
    include_package_data=True,
    install_requires=[
        'PyGithub==1.58.1',
        'click~=8.1.7',
        'codeallybasic==0.5.2',
    ],
    entry_points={
        "console_scripts": [
            "querySlugs=versionoverlord.commands.QuerySlugs:querySlugs",
            "createSpecification=versionoverlord.commands.CreateSpecification:createSpecification",
            "updateDependencies=versionoverlord.commands.UpdateDependencies:updateDependencies",
            "versionOverlord=versionoverlord.commands.VersionOverlord:versionOverlord",
        ]
    },
)
