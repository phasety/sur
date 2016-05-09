#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import glob
import subprocess
import setuptools

try:
    from numpy.distutils.core import Extension, setup
except ImportError:
    print("""Numpy is not installed. Try:

    pip install numpy==1.8
""")
    sys.exit(-1)


descr = """\
Envelope Sur.

A basic envelope and flash calculator and plotter for
multicompound mixtures.

Phasety 2013 - 2016
"""
VERSION = '1.0'   # base version


DISTNAME = 'sur'
DESCRIPTION = 'Envelope-sur package'
LONG_DESCRIPTION = descr
MAINTAINER = u'Martín Gaitán',
MAINTAINER_EMAIL = 'gaitan@gmail.com',
URL = 'http://sur.phasety.com'
LICENSE = 'Freeware'
DOWNLOAD_URL = URL
PACKAGE_NAME = 'sur'



EXTRA_INFO = dict(
    install_requires=['django>=1.7,<1.8', 'one==0.2.1', 'django-picklefield==0.3.0',
                      'numpy>=1.8', 'matplotlib>=1.3', 'quantities'],
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Scientific/Engineering']
)


def find_data_files(source, target, patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())




def get_version():
    """Obtain the version number
    If HEAD is tag, return it.
    """
    try:
        return os.environ.get('APPVEYOR_REPO_TAG_NAME', subprocess.check_output(
                    ['git', 'describe', '--exact-match', '--tags','HEAD']
                  ).strip().decode('ascii'))
    except:
        try:
            git_version = os.environ.get('APPVEYOR_REPO_COMMIT')
            if not git_version:
              git_version = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
              git_version = git_version.strip().decode('ascii')[:7]
            return '{}.post{}'.format(VERSION, git_version)
        except:
            return VERSION


# Call the setup function
if __name__ == "__main__":
    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          data_files=find_data_files('data', 'data', '*.db'),
          url=URL,
          packages=['sur'],
          zip_safe=False,
          download_url=DOWNLOAD_URL,
          long_description=LONG_DESCRIPTION,
          include_package_data=True,
          # test_suite="nose.collector",
          version=get_version(),
          ext_modules=[Extension('sur._cubic', sources=['sur/CubicParam.f90'])],
          **EXTRA_INFO)
