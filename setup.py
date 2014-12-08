#!/usr/bin/env python
# -*- coding: utf-8 -*-
descr = """\
Envelope Sur.

A basic envelope and flash calculator and plotter for
multicompound mixtures.

Phasety 2013 - 2015
"""

DISTNAME = 'sur'
DESCRIPTION = 'Envelope-sur package'
LONG_DESCRIPTION = descr
MAINTAINER  = u'Martín Gaitán',
MAINTAINER_EMAIL = 'gaitan@gmail.com',
URL = 'http://sur.phasety.com'
LICENSE = 'Freeware'
DOWNLOAD_URL = URL
PACKAGE_NAME = 'sur'
EXTRA_INFO  = dict(
    install_requires=['django', 'django-picklefield', 'numpy', 'matplotlib', 'quantities'],
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Scientific/Engineering']
)

import os
import sys
import glob
import subprocess

import setuptools
from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration


def find_data_files(source,target,patterns):
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



def configuration(parent_package='', top_path=None, package_name=DISTNAME):
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    config = Configuration(None, parent_package, top_path)

    # Avoid non-useful msg: "Ignoring attempt to set 'name' (from ... "
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_subpackage(PACKAGE_NAME)
    return config

def get_version():
    """Obtain the version number"""
    import imp
    try:
        mod = imp.load_source('version', os.path.join(PACKAGE_NAME, 'version.py'))
        return mod.__version__
    except:
        return 'dev'

# Documentation building command
try:
    from sphinx.setup_command import BuildDoc as SphinxBuildDoc
    class BuildDoc(SphinxBuildDoc):
        """Run in-place build before Sphinx doc build"""
        def run(self):
            ret = subprocess.call([sys.executable, sys.argv[0], 'build_ext', '-i'])
            if ret != 0:
                raise RuntimeError("Building doc failed!")
            SphinxBuildDoc.run(self)
    cmdclass = {'build_sphinx': BuildDoc}
except ImportError:
    cmdclass = {}

# Call the setup function
if __name__ == "__main__":
    setup(configuration=configuration,
          name=DISTNAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          data_files=find_data_files('data', 'data', '*.db'),
          url=URL,
          download_url=DOWNLOAD_URL,
          long_description=LONG_DESCRIPTION,
          include_package_data=True,
          test_suite="nose.collector",
          cmdclass=cmdclass,
          version=get_version(),
          **EXTRA_INFO)
