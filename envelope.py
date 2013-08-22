import _env
import numpy as np


def rkpr(comp, tc, pc, ohm, ac, b, delta, k, k0=None, tstar=None, lij=None):

    """
    Low level wrapper for the Fortran implementation of the RK-PR for multicompounds systems.

    Return envelope and critical point data arrays::

        ((tenv, penv, denv), (tcri, pcri, dcri))

    Required arguments:

      comp : input rank-1 array('f')
      tc : input rank-1 array('f')
      pc : input rank-1 array('f')
      ohm : input rank-1 array('f')

      ac : input rank-1 array('f')
      b : input rank-1 array('f')
      delta : input rank-1 array('f')
      k : input rank-1 array('f')

    Optional arguments:

      k0 : input rank-2 array('f') with bounds (n,n)
      tstar : input rank-2 array('f') with bounds (n,n)
      lij : input rank-2 array('f') with bounds (n,n)

    Return object:

      A tuple (envelope_data, critical_points_data) where envelope_data is a tuple

        (tenv, penv, denv) rank-1 arrays of the same size

      and critical_points_data

        (tcri, pcri, dcri) rank-1 arrays of the same size

    """
    n = comp.size
    if k0 is None:
       k0 = np.zeros((n,n))

    if tstar is None:
       tstar = np.zeros((n,n))

    if lij is None:
       lij = np.zeros((n,n))

    fortran_out = _env.envelope.rkpr(comp, tc, pc, ohm, ac, b, delta, k, k0, tstar, lij)
    tenv, penv, denv, n_out, tcri, pcri, dcri, n_cri = fortran_out

    return ((tenv[:n_out], penv[:n_out], denv[:n_out]),
            (tcri[:n_cri], pcri[:n_cri], dcri[:n_cri]))
