<!--
    =====================================
    generator=datazen
    version=3.1.2
    hash=dc1cf0b80c7df04bc799c2981b83e78f
    =====================================
-->

# userfs ([1.1.3](https://pypi.org/project/userfs/))

[![python](https://img.shields.io/pypi/pyversions/userfs.svg)](https://pypi.org/project/userfs/)
![Build Status](https://github.com/vkottler/userfs/workflows/Python%20Package/badge.svg)
[![codecov](https://codecov.io/gh/vkottler/userfs/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/vkottler/userfs)
![PyPI - Status](https://img.shields.io/pypi/status/userfs)
![Dependents (via libraries.io)](https://img.shields.io/librariesio/dependents/pypi/userfs)

*A system-bootstrapping automation and introspection tool.*

## Documentation

### Generated

* By [sphinx-apidoc](https://vkottler.github.io/python/sphinx/userfs)
(What's [`sphinx-apidoc`](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html)?)
* By [pydoc](https://vkottler.github.io/python/pydoc/userfs.html)
(What's [`pydoc`](https://docs.python.org/3/library/pydoc.html)?)

## Python Version Support

This package is tested with the following Python minor versions:

* [`python3.10`](https://docs.python.org/3.10/)
* [`python3.11`](https://docs.python.org/3.11/)

## Platform Support

This package is tested on the following platforms:

* `ubuntu-latest`
* `macos-latest`
* `windows-latest`

# Introduction

# Command-line Options

```
$ ./venv3.11/bin/ufs -h

usage: ufs [-h] [--version] [-v] [-q] [--curses] [--no-uvloop] [-C DIR]
           {build,custom,fetch,noop} ...

A system-bootstrapping automation and introspection tool.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose         set to increase logging verbosity
  -q, --quiet           set to reduce output
  --curses              whether or not to use curses.wrapper when starting
  --no-uvloop           whether or not to disable uvloop as event loop driver
  -C DIR, --dir DIR     execute from a specific directory

commands:
  {build,custom,fetch,noop}
                        set of available commands
    build               attempt to build a software project from its sources
    custom              perform a custom interaction, sourced from external
                        hooks
    fetch               attempt to obtain some software from the internet
    noop                command stub (does nothing)

```

## Sub-command Options

### `build`

```
$ ./venv3.11/bin/ufs build -h

usage: ufs build [-h] [-c CONFIG] [-a] [-n] [-p PATTERN] [-d] [projects ...]

positional arguments:
  projects              specific projects to build, arguments in the form
                        'key=value' will be provided as interaction options

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        an optional path to the configuration directory
  -a, --all             interact with all configured projects
  -n, --no-interact     don't run package-implemented interactions
  -p PATTERN, --pattern PATTERN
                        a pattern to use to select project specifications
                        filtered by name
  -d, --deploy          whether or not to also attempt to deploy or install
                        the built project assets

```

### `custom`

```
$ ./venv3.11/bin/ufs custom -h

usage: ufs custom [-h] [-c CONFIG] [-a] [-n] [-p PATTERN] [projects ...]

positional arguments:
  projects              specific projects to build, arguments in the form
                        'key=value' will be provided as interaction options

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        an optional path to the configuration directory
  -a, --all             interact with all configured projects
  -n, --no-interact     don't run package-implemented interactions
  -p PATTERN, --pattern PATTERN
                        a pattern to use to select project specifications
                        filtered by name

```

### `fetch`

```
$ ./venv3.11/bin/ufs fetch -h

usage: ufs fetch [-h] [-c CONFIG] [-a] [-n] [-p PATTERN] [-u] [projects ...]

positional arguments:
  projects              specific projects to build, arguments in the form
                        'key=value' will be provided as interaction options

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        an optional path to the configuration directory
  -a, --all             interact with all configured projects
  -n, --no-interact     don't run package-implemented interactions
  -p PATTERN, --pattern PATTERN
                        a pattern to use to select project specifications
                        filtered by name
  -u, --update          whether or not to also attempt to update project
                        sources

```

# Internal Dependency Graph

A coarse view of the internal structure and scale of
`userfs`'s source.
Generated using [pydeps](https://github.com/thebjorn/pydeps) (via
`mk python-deps`).

![userfs's Dependency Graph](im/pydeps.svg)
