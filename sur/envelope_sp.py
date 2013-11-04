"""
this is a hack due we couldn't compile the fortran code using gfrotran.
"""
import sys
import os.path
import tempfile
import cStringIO

try:
    import subprocess32 as subprocess
    TIME_OUT = True
except ImportError:
    import subprocess
    TIME_OUT = False

import numpy as np
from django.template.loader import render_to_string
from eos import get_eos
from . import data


def exec_fortran(bin, path, as_out_txt=None):
    """Execute a fortran program
    if as_out_txt is read that file and return its content
    """

    args = []
    if sys.platform != 'win32':
        # On any non-Windows system, we run binaries through wine
        args.append('wine')
    args.append(data(bin + '.exe'))

    if TIME_OUT:
        p = subprocess.Popen(args, cwd=path, stdout=subprocess.PIPE)
        output = p.communicate(timeout=20)[0]
    else:
        p = subprocess.Popen(args, cwd=path, stdout=subprocess.PIPE)
        output = p.communicate()[0]
    if as_out_txt:
        txt = os.path.join(path, as_out_txt)
        with open(txt, 'r') as fh:
            output = fh.read()

    return output


def write_input(mixture, eos, t=None, p=None, as_data=False, interactions=None):
    """
    if t and p are given, return the path of the folder with
    a written flashIN.txt
    """
    compounds = []
    for i, c in enumerate(mixture.compounds):
        if i > 0:
            for k, matrix in interactions.items():
                setattr(c, '%s_' % k, "   ".join(map(str, matrix[:i, i])))
        update = eos == 'RKPR'
        c.params = "   ".join(map(str, c._get_eos_params(eos, update_vc=update)))
        compounds.append(c)
    nTdep = 1 if 'k0' in matrix else 0
    eos = get_eos(eos)
    data = render_to_string('input.html', locals())
    if as_data:
        return data

    input_file = 'flashIN.txt' if t and p else 'envelIN.txt'
    path = tempfile.mkdtemp()
    print path
    with open(os.path.join(path, input_file), 'w') as fh:
        fh.write(data)

    return path


def envelope(env):
    path = write_input(env.mixture, env.eos, interactions=env.interactions)
    output = exec_fortran('EnvelopeSur', path, as_out_txt="envelOUT.txt")
    # to debug
    env.input_txt = open(os.path.join(path, 'envelIN.txt')).read()
    env.output_txt = output

    output = output.split('\n')

    mark = "    T(K)        P(bar)        D(mol/L)"
    for start, line in enumerate(output):
        if line.startswith(mark):
            break

    env_block = []
    for end, line in enumerate(output[start + 1:]):
        if not line.strip():
            break
        env_block.append(line)

    env_block = np.loadtxt(cStringIO.StringIO("\n".join(env_block)),
                           unpack=True, ndmin=2)

    for start_cri, line in enumerate(output[start + end:]):
        if line.startswith(mark):
            break

    cri_block = output[start + end + start_cri + 1:]
    cri_block = np.loadtxt(cStringIO.StringIO("\n".join(cri_block)),
                           unpack=True, ndmin=2)
    if not cri_block.any():
        cri_block = [None, None, None, None]
    return env_block, cri_block


def flash(fi):
    if fi.rel_envelope:
        interactions = fi.rel_envelope.interactions
    else:
        from .models import get_interactions
        interactions = get_interactions(fi.input_mixture, fi.mode, fi.eos)
    path = write_input(fi.input_mixture, fi.eos, fi.t, fi.p,
                       interactions=interactions)
    output = exec_fortran('FlashSur', path)
    output = [l.strip() for l in output.split('\n') if l.strip()]

    x, y, rho_x, rho_y, beta = output
    rho_x, rho_y, beta = map(float, (rho_x, rho_y, beta))
    x = np.fromstring(x, sep=" ")
    y = np.fromstring(y, sep=" ")
    return x / x.sum(), y / y.sum(), rho_x, rho_y, beta
