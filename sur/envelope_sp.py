"""
this is a hack due we couldn't compile the fortran code using gfrotran.
"""
import sys
import os.path
import tempfile
import subprocess

import numpy as np
from django.template.loader import render_to_string
from eos import get_eos
from . import data


def exec_fortran(bin, path):
    """Execute a fortran program"""

    args = []
    if sys.platform != 'win32':
        # On any non-Windows system, we run binaries through wine
        args.append('wine')
    args.append(data(bin + '.exe'))

    return subprocess.check_output(args, cwd=path)


def write_input(mixture, eos, t=None, p=None):
    """
    if t and p are given, return the path of the folgter with
    a written flashIN.txt
    """
    compounds = []
    for i, c in enumerate(mixture.compounds):
        if i > 0:
            c.k12 = "   ".join(map(str, mixture.kij(eos)[:i, i]))
            c.l12 = "   ".join(map(str, mixture.lij(eos)[:i, i]))
        c.params = "   ".join(map(str, c._get_eos_params(eos, update_vc=True)))
        compounds.append(c)
    eos = get_eos(eos)
    data = render_to_string('input.html', locals())

    input_file = 'flashIN.txt' if t and p else 'envelopeIN.txt'
    path = tempfile.mkdtemp()
    with open(os.path.join(path, input_file), 'w') as fh:
        fh.write(data)
    return path


def envelope(envelope_instance):
    pass


def flash(fi):
    path = write_input(fi.input_mixture, fi.eos, fi.t, fi.p)
    output = exec_fortran('flash', path)
    print output
    output = [l.strip() for l in output.split('\n') if l.strip()]

    x, y, rho_x, rho_y, beta = output
    rho_x, rho_y, beta = map(float, (rho_x, rho_y, beta))
    x = np.fromstring(x, sep=" ")
    y = np.fromstring(y, sep=" ")
    return x / x.sum(), y/ y.sum(), rho_x, rho_y, beta
