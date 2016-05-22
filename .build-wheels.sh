#!/bin/bash
set -e -x

# Install a system package required by our library
yum install -y gcc-gfortran numpy

# Compile wheels
/opt/python/python2.7/bin/pip wheel /io/ -w wheelhouse/

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    auditwheel repair $whl -w /io/wheelhouse/
done

# Install packages and test
# for PYBIN in /opt/python/*/bin/; do
#     ${PYBIN}/pip install python-manylinux-demo --no-index -f /io/wheelhouse
#     (cd $HOME; ${PYBIN}/nosetests pymanylinuxdemo)
# done
