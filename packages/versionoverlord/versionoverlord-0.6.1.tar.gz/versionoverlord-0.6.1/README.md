[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/versionoverlord/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/versionoverlord/tree/master)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)



## Rationale

These utilities are meant to solve a problem with related repositories and their dependency relationships

Projects may have hierarchical dependencies.  See the following [Pyut](https://github.com/hasii2011/PyUt) dependency diagram. 



```mermaid
---
title: Pyut Dependency Graph
---
flowchart
	direction LR
	
  pyut(Pyut 7.7.0) --> oglio(oglio 0.5.80)
  pyut(Pyut 7.7.0) --> pyutplugins(pyutplugins 0.8.40)
  
  pyutplugins(pyutplugins 0.8.40) -.-> oglio(oglio 0.5.80)
  pyutplugins(pyutplugins 0.8.40) & oglio(oglio 0.5.80) --> untanglepyut.0.6.40

   pyut(Pyut 7.7.0) & oglio(oglio 0.5.80) & untanglepyut.0.6.40 --> ogl.0.70.20
   
   pyut(Pyut 7.7.0) &  pyutplugins(pyutplugins 0.8.40) &  oglio(oglio 0.5.80) &  untanglepyut.0.6.40 &  ogl.0.70.20 -...-> pyutmodel.1.4.2
   pyut(Pyut 7.7.0) & pyutplugins(pyutplugins 0.8.40) & ogl.0.70.20 ----> hasiicommon.0.2.0

    style pyut fill:#ee4,stroke:#333,stroke-width:
    %% linkStyle 1 stroke:#ff3,stroke-width:4px,color:red;
```

The above diagram illustrates how low level dependencies ripple up the dependency tree.  

## Dependency Locations

Additionally, projects may specify dependencies in different places.  Examples of the dependency locations are

* setup.py
* requirements.txt
* .circleci/config.yml
* .travis.yml



## Python Console Scripts

VersionOverlord means to handle this problem by providing a set of Python command line scripts to automate updating the first three of the above dependency specification locations

* querySlugs -- queries repositories for their latest release version
* createSpec -- creates a dependency specification for a project 
* updateDeps -- updates the supported dependency locations using the generated specification



## Required Environment Variables

The above commands depend on the following environment variables.

```bash
GITHUB_ACCESS_TOKEN - A personal GitHub access token necessary to read repository release information
PROJECTS_BASE             -  The local directory where the python projects are based
PROJECT                          -  The name of the project;  It should be a directory name
```

See the [GitHub Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) for instructions on how to create a usable access token.  These scripts assume  that a developer keeps all checked out repositories in a single directory.  An example, of a PROJECTS_BASE is:

```bash
export PROJECTS_BASE="${HOME}/PycharmProjects" 
```

This should be set in your shell startup script.  For example `.bash_profile`.

The PROJECT environment variable should be set on a project by project basis.  I recommend you use [direnv](https://direnv.net) to manage these.  An example of a .envrc follows:

```bash
export PROJECT=pyutmodel
source pyenv-3.10.6/bin/activate
```

## Slugs

The command line options for querySlug and createSpec are GitHub slugs.  For example, for the following repositories

https://github.com/hasii2011/pyutmodel

https://github.com/hasii2011/hasiicommon

The slugs are `hasii2011/pyutmode` and `hasii2011/hasiicommon,` respectively.



## Usage

From the above dependency diagram assume the following:

Both the `pyutmodel` and `hasiicommon` repositories have been updated.  We need to update the `ogl` dependencies to match the latest of both.  Assume both `GITHUB_ACCESS_TOKEN` and `PROJECTS_BASE` are correctly set and `PROJECT` is set to `'ogl'`.  Use the following CLI invocation to create the specification file.

```
createSpec -s hasii2011/pyutmodel -s hasii2011/hasiicommon
```

The command creates the file `versionSpecification.csv` with the following contents.

```
PackageName,OldVersion,NewVersion
pyutmodel,1.4.0,1.4.1
hasiicommon,0.0.7,0.1.0                   
```

Again assuming the previously mentioned environment variables are set the following CLI invocation;

```
updateDeps
```

correctly updates the following

* setup.py
* requirements.txt
* .circleci/config.yml

## Installation

```
pip install versionoverlord
```



## 


___

Written by <a href="mailto:email@humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  (C) 2023


## Note
For all kind of problems, requests, enhancements, bug reports, etc.,
please drop me an e-mail.


![Humberto's Modified Logo](https://raw.githubusercontent.com/wiki/hasii2011/gittodoistclone/images/SillyGitHub.png)

I am concerned about GitHub's Copilot project



I urge you to read about the
[Give up GitHub](https://GiveUpGitHub.org) campaign from
[the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there I do not like that
a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  But, I continue
to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done
without my permission.  I do not consent to GitHub's use of this project's
code in Copilot.

A repository owner may opt out of Copilot by changing Settings --> GitHub Copilot.

I have done so.

