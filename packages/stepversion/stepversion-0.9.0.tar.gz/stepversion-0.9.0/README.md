![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/agpl-license-web-badge-version-2-256x48.png "AGPL")

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/stepversion/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/stepversion/master)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)


# Introduction

A simple python console script to let me bump package version numbers easily and at will.

# Overview

The basic command structure is:

```
Usage: stepversion [OPTIONS]

  Args:     major:     minor:     patch:     package_name

Options:
  --version                Show the version and exit.
  -m, --major INTEGER      Bump major version (default 1)
  -i, --minor INTEGER      Bump minor version (default 1)
  -p, --patch INTEGER      Bump patch version (default 1)
  -a, --package-name TEXT  Use this option when the package name does not
                           match the project name
  --help                   Show this message and exit.

```

# Opinionated Expectations

The project keeps a `_version.py` file in the main package.

The format of the file is:

```python
__version__: str = 'A Semantic Version'
```

See [Semantic Versioning](https://semver.org)

# Installation

```pip install stepversion```


___

Written by <a href="mailto:email@humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  (C) 2023

 


## Note
For all kind of problems, requests, enhancements, bug reports, etc.,
please drop me an e-mail.
___


![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/SillyGitHub.png)

== I am using GitHub under protest ==

This project is currently hosted on GitHub.  

I urge you to read about the
[Give up GitHub](https://GiveUpGitHub.org) campaign from
[the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there I do not like that
a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  But, I continue
to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done
without our permission.  We do not consent to GitHub's use of this project's
code in Copilot.
