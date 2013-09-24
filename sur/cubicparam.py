# -*- coding: utf-8 -*-

import numpy as np
import _cubic

__all__ = ['SRK', 'PR', 'RKPR']


class CubicModel(object):

    @classmethod
    def from_constants(cls, tc, pc, acentric_factor, pvdat=()):
        """
        Given the constants of a pure compound, returns
        a tuple of arrays with the same constants adjusted
        and the arrays of correspond model's parameters.

        If a point pvdat = (P, T) is given, it's used as a constraint
        to calculate the vapor pressure

        Returns
        -------

        ::

             (constants, model_parameters)

        Where::

            constants = array([Tc, Pc, acentric_factor, Vc])
            models_parameters =  array([ac, b, rm])

        """
        constants = np.array([tc, pc, acentric_factor])
        if pvdat:
            if len(pvdat) != 2:
                raise ValueError('pvdat should be a tuple (P, T)')
            p_pvdat, t_pvdat = pvdat
            inputs, params = _cubic.modelsparam(0, cls.MODEL_ID, constants,
                                               p_pvdat, t_pvdat)
        else:
            inputs, params = _cubic.modelsparam(0, cls.MODEL_ID, constants)
        params = params[:3]
        return inputs, params

    @classmethod
    def from_parameters(cls, ac, b, rm):
        """
        Given the model's parameters, returns
        a tuple of arrays with the pure compound constants adjusted
        and the the ajusted model's array of parameters.


        Returns
        -------

               (constants, model_parameters)

        Where

            constants = array([Tc, Pc, acentric_factor, Vc])
            models_parameters =  array([ac, b, rm])

        """
        parameters = np.array([ac, b, rm])
        inputs, params = _cubic.modelsparam(1, cls.MODEL_ID, parameters)
        params = params[:3]
        return inputs, params


class SRK(CubicModel):
    """
    Soave modification of Redlich–Kwong EOS
    """

    MODEL_ID = 2
    MODEL_NAME = 'SRK'


class PR(CubicModel):
    """
    Peng–Robinson equation of state
    """
    MODEL_ID = 1
    MODEL_NAME = 'PR'


class RKPR(object):
    """
    Peng–Robinson equation of state
    """

    MODEL_ID = 3
    MODEL_NAME = 'RKPR'

    @classmethod
    def from_constants(cls, tc, pc, acentric_factor, vc=None, del1=None,
                       rhoLsat_t=(), pvdat=()):
        """
        Given the constants of a pure compound, returns
        a tuple of arrays with the same constants adjusted
        and the arrays of correspond model's parameters.

        Constants requires tc, pc, and acentric_factor as mandatory
        and vc or del1 or rhoLsat_t=(rhoLsat, T).

        If a point pvdat = (P, T) is given, it's used as a constraint
        to calculate the vapor pressure

        Returns
        -------

        ::

             (constants, model_parameters)

        Where::

            constants = array([tc, pc, acentric_factor, vc])
            models_parameters =  array([ac, b, del1, rk])

        """
        if len(filter(bool, [vc, del1, rhoLsat_t])) != 1:
            raise ValueError('Give one of vc or del1 or rhoLsat_t=(rhoLsat, T)'
                             ' as the extra parameter')
        elif vc:
            mode = 0
            constants = np.array([tc, pc, acentric_factor, vc])
        elif del1:
            mode = 2
            constants = np.array([tc, pc, acentric_factor, del1])
        else:
            if len(rhoLsat_t) != 2:
                raise ValueError('RhoLsat should be a tuple (rhoLsat, T)')
            rhoLsat, T = rhoLsat_t
            mode = 3
            constants = np.array([tc, pc, acentric_factor, rhoLsat, T])

        if pvdat:
            if len(pvdat) != 2:
                raise ValueError('pvdat should be a tuple (P, T)')
            p_pvdat, t_pvdat = pvdat
            inputs, params = _cubic.modelsparam(mode, cls.MODEL_ID, constants,
                                               p_pvdat, t_pvdat)
        else:
            inputs, params = _cubic.modelsparam(mode, cls.MODEL_ID, constants)
        return inputs, params

    @classmethod
    def from_parameters(cls, ac, b, del1, rk):
        """
        Given the model's parameters, returns
        a tuple of arrays with the pure compound constants adjusted
        and the the ajusted model's array of parameters.


        Returns
        -------

               (constants, model_parameters)

        Where

            constants = array([Tc, Pc, acentric_factor, Vc])
            models_parameters =  array([ac, b, del1, rk])

        """
        parameters = np.array([ac, b, del1, rk])
        inputs, params = _cubic.modelsparam(1, cls.MODEL_ID, parameters)
        return inputs, params
