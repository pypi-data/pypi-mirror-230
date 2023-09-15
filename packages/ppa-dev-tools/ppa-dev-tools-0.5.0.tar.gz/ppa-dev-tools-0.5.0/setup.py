#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ppa - Tools for creating, installing, modifying, and testing PPAs.
#
# Copyright (c) 2012,2019-2022 - Bryce W. Harrington

from setuptools import setup, find_packages

import sys
import re

if sys.version_info < (3,0):
    sys.exit('Please run setup.py with python3')

def get_version(package):
    """Directly retrieve version, avoiding an import.

    Since setup.py runs before the package is set up, we can't expect
    that simply doing an import ._version will work reliably in all
    cases.  Instead, manually import the version from the file here,
    and then the module can be imported elsewhere in the project easily.
    """
    version_file = "%s/%s" %(package, '_version.py')
    version_string = open(version_file, "rt").read()
    re_version = r"^__version__ = ['\"]([^'\"]*)['\"]"
    m = re.search(re_version, version_string, re.M)
    if not m:
        raise RuntimeError("Unable to find version string for %s in %s." %(
            package, version_file))
    return m.group(1)

def get_description():
    return open('README.md', 'rt').read()

setup(
    name             = 'ppa-dev-tools',
    version          = get_version('ppa'),
    url              = 'https://launchpad.net/ppa-dev-tools',
    author           = 'Bryce W. Harrington',
    author_email     = 'bryce@canonical.com',
    description      = 'Utility for interacting with PPAs on Launchpad',
    long_description = get_description(),
    classifiers      = [
        # See https://pypi.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Software Distribution',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3',
        ],
    platforms        = ['any'],
    python_requires  = '>=3',
    setup_requires   = [
        'pytest-runner'
        ],
    tests_require    = [
        'pytest'
        ],
    install_requires = [],  # See INSTALL.md
    scripts          = ['scripts/ppa'],
    packages         = find_packages(),
    package_data     = { },
    data_files       = [ ],
)
