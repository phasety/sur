import _env
import numpy as np
from . import eos

def envelope(model, z, tc, pc, ohm, ac, b, m=None, k=None,
             delta1=None, kij=None, k0=None, tstar=None, lij=None):
    """
    Low level wrapper for the Fortran implementation
    of the RK-PR for multicompounds systems.

    Return envelope and critical point data arrays::

        ((tenv, penv, denv), (tcri, pcri, dcri))

    Required arguments:


      model: one of eos's Cubic classes
      z : input rank-1 array('f')
      tc : input rank-1 array('f')
      pc : input rank-1 array('f')
      ohm : input rank-1 array('f')

      ac : input rank-1 array('f')
      b : input rank-1 array('f')
      k (RKPR) or m (SRK or PR): input rank-1 array('f')
      delta1 (RKPR): input rank-1 array('f')

      kij or (k0 and tstar): input rank-2 array('f')

    Return object:

      A tuple (envelope_data, critical_points_data) where envelope_data is a tuple

        (tenv, penv, denv) rank-1 arrays of the same size

      and critical_points_data

        (tcri, pcri, dcri) rank-1 arrays of the same size

    """
    n = z.size

    if kij is not None and any((k0, tstar)):
        raise ValueError('Only kij or (k0 and tstar) could be given')
    elif kij is None and not all((k0, tstar)):
        raise ValueError('Only kij or (k0 and tstar) could be given')

    if model == eos.RKPR and (not all((k, delta1)) or m is not None):
        raise ValueError('RKPR requires just k and delta1 arrays')
    elif model != eos.RKPR and (m is None or k is not None):
        raise ValueError('%s require just m array (not k)' % model.MODEL_NAME)


    kij_or_k0 = kij or k0
    lij = lij or np.zeros((n,n))
    tstar = tstar or np.zeros((n,n))
    k_or_m = k or m

    delta1 = delta1 or np.zeros((n,))

    fortran_out = _env.sur.envelope(model.MODEL_ID, z, tc, pc, ohm, ac, b, k_or_m,
                                    delta1, kij_or_k0, tstar, kij)
    return ((tenv[:n_out], penv[:n_out], denv[:n_out]),
            (tcri[:n_cri], pcri[:n_cri], dcri[:n_cri]))
