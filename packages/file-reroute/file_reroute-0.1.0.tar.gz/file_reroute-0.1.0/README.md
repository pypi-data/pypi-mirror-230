# 📦 file-reroute
[![test](https://github.com/RonaldsonBellande/file-reroute/actions/workflows/library_test.yml/badge.svg)](https://github.com/RonaldsonBellande/file-reroute/actions/workflows/library_test.yml)
[![publish](https://github.com/RonaldsonBellande/file-reroute/actions/workflows/library_publish.yml/badge.svg)](https://github.com/RonaldsonBellande/file-reroute/actions/workflows/library_publish.yml)
[![PyPI version](https://badge.fury.io/py/file_reroute.svg)](https://badge.fury.io/py/file_reroute)

### 🦾 motivation
- easy to use package to solve an easy problem

### ✔️ confirmed versions
- `Works of all platforms(Windows, Linux, Mac OS), all version of python (python2 and python3), all versions of IDE, all different kind of IDE's

### 3 ways to install ⬇️ install locally
- clone this repo
- `$ pip install file-retoute`
- `$ pip show -f file_reroute`

### :octocat: install from GitHub.com
- `pip install git+https://github.com/RonaldsonBellande/file-reroute`

### Usage 
```
from file_reroute.reroute import reroute
reroute(["directory1", "directory2"])
```
- directory= "directory you want to reroute to"
- can be more then one directory as if one does not exist it will do the other directory and tell you that it does not exist


```
Name: file_reroute
Version: 0.0.1
Summary: A package for easier interaction with Terminal and IDE
Home-page: github.com/RonaldsonBellande/file-reroute
Author: RonaldsonBellande
Author-email: ronaldsonbellande@gmail.com
License: GNU General Public License v3.0
Requires: None
Required-by:
```
### 👩‍🔧 testing
- `$ pip install .[dev]`
- `$ python -m pytest --cov`

### ❓ src-layout vs. flat-layout
- see https://setuptools.pypa.io/en/stable/userguide/package_discovery.html

### 📦 publish to PyPI
- use [pypa/build](https://github.com/pypa/build), a simple PEP 517 frontend and [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
- https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
