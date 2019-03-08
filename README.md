# brunns-builder

Test object builders.

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Build Status](https://travis-ci.org/brunns/brunns-builder.svg?branch=master&logo=travis)](https://travis-ci.org/brunns/brunns-builder)
[![PyPi Version](https://img.shields.io/pypi/v/brunns-builder.svg?logo=pypi)](https://pypi.org/project/brunns-builder/#history)
[![Python Versions](https://img.shields.io/pypi/pyversions/brunns-builder.svg?logo=python)](https://pypi.org/project/brunns-builder/)
[![Licence](https://img.shields.io/github/license/brunns/brunns-builder.svg)](https://github.com/brunns/brunns-builder/blob/master/LICENSE)
[![GitHub all releases](https://img.shields.io/github/downloads/brunns/brunns-builder/total.svg?logo=github)](https://github.com/brunns/brunns-builder/releases/)
[![GitHub forks](https://img.shields.io/github/forks/brunns/brunns-builder.svg?label=Fork&logo=github)](https://github.com/brunns/brunns-builder/network/members)
[![GitHub stars](https://img.shields.io/github/stars/brunns/brunns-builder.svg?label=Star&logo=github)](https://github.com/brunns/brunns-builder/stargazers/)
[![GitHub watchers](https://img.shields.io/github/watchers/brunns/brunns-builder.svg?label=Watch&logo=github)](https://github.com/brunns/brunns-builder/watchers/)
[![GitHub contributors](https://img.shields.io/github/contributors/brunns/brunns-builder.svg?logo=github)](https://github.com/brunns/brunns-builder/graphs/contributors/)
[![GitHub issues](https://img.shields.io/github/issues/brunns/brunns-builder.svg?logo=github)](https://github.com/brunns/brunns-builder/issues/)
[![GitHub issues-closed](https://img.shields.io/github/issues-closed/brunns/brunns-builder.svg?logo=github)](https://github.com/brunns/brunns-builder/issues?q=is%3Aissue+is%3Aclosed)
[![GitHub pull-requests](https://img.shields.io/github/issues-pr/brunns/brunns-builder.svg?logo=github)](https://github.com/brunns/brunns-builder/pulls)
[![GitHub pull-requests closed](https://img.shields.io/github/issues-pr-closed/brunns/brunns-builder.svg?logo=github)](https://github.com/brunns/brunns-builder/pulls?utf8=%E2%9C%93&q=is%3Apr+is%3Aclosed)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6f43e871d3514176bebc650849ac7d4a)](https://www.codacy.com/app/brunns/brunns-builder)
[![Codacy Coverage](https://api.codacy.com/project/badge/coverage/6f43e871d3514176bebc650849ac7d4a)](https://www.codacy.com/app/brunns/brunns-builder)
[![Lines of Code](https://tokei.rs/b1/github/brunns/brunns-builder)](https://github.com/brunns/brunns-builder)

## Setup

Install with pip:

    pip install brunns-builder

(As usual, use of a [venv](https://docs.python.org/3/library/venv.html) or [virtualenv](https://virtualenv.pypa.io) is recommended.)

## Usage

TODO

## Developing

Requires [tox](https://tox.readthedocs.io). Run `make precommit` tells you if you're OK to commit. For more options, run:

    make help

## Releasing

Requires [hub](https://hub.github.com/), [setuptools](https://setuptools.readthedocs.io), [wheel](https://pypi.org/project/wheel/) and [twine](https://twine.readthedocs.io). To release `n.n.n`:

    version="n.n.n"
    make precommit && git commit -am"Release $version" && git push # If not already all pushed, which it should be.
    hub release create $version -m"Release $version"
    python setup.py sdist bdist_wheel
    twine upload dist/*$version*
    
Quick version:

    version="n.n.n"
    git commit -am"Release $version" && git push && hub release create $version -m"Release $version" && python setup.py sdist bdist_wheel && twine upload dist/*$version*
