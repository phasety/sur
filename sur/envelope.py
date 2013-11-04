import _env
import numpy as np
from sur import eos


def flash(t, p, model, z, tc, pc, ohm, ac, b, m=None, k=None,
          delta1=None, kij=None, k0=None, tstar=None, lij=None):
    """
    Low level wrapper for the Fortran implementation
    of flash calculation based on EOS

    Required arguments:

      t = Temperature for the flash
      p = Pressure for the flash

      model: one of eos's Cubic classes
      z : input rank-1 array('f') with size n
      tc : input rank-1 array('f')
      pc : input rank-1 array('f')
      ohm : input rank-1 array('f')

      ac : input rank-1 array('f')
      b : input rank-1 array('f')
      k (RKPR) or m (SRK or PR): input rank-1 array('f')
      delta1 (RKPR): input rank-1 array('f')

      kij or (k0 and tstar): input rank-2 array('f')

    Returns:

      A tuple (x, y, rho_x, rho_y, beta) where

        x and y are composition arrays for liquid and vapour respectively
        rho_x and rho_y are the density for liquid and vapour
        beta is the total fraction of vapour


    """
    n = z.size

    if kij is not None and any((k0, tstar)):
        raise ValueError('Only kij or (k0 and tstar) could be given')
    elif kij is None and (k0 is None or tstar is None):
        raise ValueError('At least kij or (k0 and tstar) could be given')

    if model == eos.RKPR and (k is None or delta1 is None or m is not None):
        raise ValueError('RKPR requires just k and delta1 arrays')
    elif model != eos.RKPR and (m is None or k is not None):
        raise ValueError('%s require just m array (not k)' % model.MODEL_NAME)

    kij_or_k0 = kij if kij is not None else k0
    lij = lij if lij is not None else np.zeros((n, n))
    tstar = tstar if tstar is not None else np.zeros((n, n))
    k_or_m = k if k is not None else m

    delta1 = delta1 if delta1 is not None else np.zeros((n,))
    return _env.sur.flash(model.MODEL_ID, z, tc, pc, ohm, ac, b, k_or_m,
                          delta1, kij_or_k0, tstar, lij, t, p)


def envelope(model, z, tc, pc, ohm, ac, b, m=None, k=None,
             delta1=None, kij=None, k0=None, tstar=None, lij=None):
    """
    Low level wrapper for the Fortran implementation
    of envelope calculations based on EOS.

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
    elif kij is None and (k0 is None or tstar is None):
        raise ValueError('At least kij or (k0 and tstar) could be given')

    if model == eos.RKPR and (k is None or delta1 is None or m is not None):
        raise ValueError('RKPR requires just k and delta1 arrays')
    elif model != eos.RKPR and (m is None or k is not None):
        raise ValueError('%s require just m array (not k)' % model.MODEL_NAME)

    kij_or_k0 = kij if kij is not None else k0
    lij = lij if lij is not None else np.zeros((n, n))
    tstar = tstar if tstar is not None else np.zeros((n, n))
    k_or_m = k if k is not None else m

    delta1 = delta1 if delta1 is not None else np.zeros((n,))
    fortran_out = _env.sur.envelope(model.MODEL_ID, z, tc, pc, ohm, ac, b, k_or_m,
                                    delta1, kij_or_k0, tstar, lij)
    n_points, tv, pv, dv, n_cri, tcri, pcri, dcri = fortran_out
    return ((tv[:n_points], pv[:n_points], dv[:n_points]),
            (tcri[:n_cri], pcri[:n_cri], dcri[:n_cri]))
