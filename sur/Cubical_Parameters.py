import numpy as np
from scipy.optimize import fsolve
"""
This module calculate parameters necessary to use the equations of state:
SRK, PR and RKPR
"""

# Ejemplo de ese tipo de corrida con un RHOLSat

# Data for CO2
# 3  3    0                         ICALC,NMODEL
# 304.21  73.83  0.2236      Tc, Pc, omega
# 270.0  21.4626                 T(K), RhoLsat (L/mol)

# Critical constants must be given in K and bar
# b will be in L/mol and ac in bar*(L/mol)**2

# METHANE (1)
# Tc, Pc, omega, vc, zrat = 190.564, 45.99, 0.01155, 0.115165, 1.00000173664
# ac, b, delta_1, rk = 2.3277, 0.029962, 0.932475, 1.49541
# Tr = 0.7 # Change here to use another Pv than the one at Tr 0.7

RGAS = 0.08314472
# Definir el significado fisicoquímico

A0, B0, C0 = 0.0017, 1.9681, -2.7238
# Definir el significado fisicoquímico

A1, B1, C1 = -2.4407, 7.4513, 12.504
# Definir el significado fisicoquímico

D = np.array([0.428363, 18.496215, 0.338426, 0.660, 789.723105, 2.512392])

ICALC = 3

# Carbon Dioxide
Tc, Pc, omega = 304.21,  73.83,  0.2236  # Tc, Pc, omega
T_especific, RHOLSat_esp = 270.0,   21.4626 # T(K), RhoLsat (L/mol)

# delta_1 = d
delta_1 = 0.5

print("delta_1 = {0}".format(delta_1))

class Eos_initialisation(object):
    """docstring for Eos_initialisation"""
    def __init__(self, arg):
        super(Eos_initialisation, self).__init__()
        self.arg = arg


def initial_data(omega, delta_1):

    d1 = (1 + delta_1 ** 2) / (1 + delta_1)
    y = 1 + (2 * (1 + delta_1)) ** (1.0 / 3) + (4 / (1 + delta_1)) ** (1.0 / 3)
    OMa = (3 * y * y + 3 * y * d1 + d1 ** 2 + d1 - 1.0) \
    / (3 * y + d1 - 1.0) ** 2    
    OMb = 1 / (3 * y + d1 - 1.0)
    Zc = y / (3 * y + d1 - 1.0)

    # initial guess for k parameter
    rk = (A1 * Zc + A0) * omega**2 + (B1 * Zc + B0) * omega + (C1 * Zc + C0)
    rk = rk * 3.2

    if ICALC == 1 or ICALC == 2:
        Tr = 0.7
        Pvdat = Pc * 10 ** -(1.0 + omega)
    else:
        Tr_calculada = T_especific/Tc
        Tr = Tr_calculada
        Pvdat = Pc * 10 ** -((1.0 / Tr - 1.0) * 7 * (1.0 + omega) / 3)
    
    return rk, Pvdat, Tr

rk, Pvdat, Tr = initial_data(omega, delta_1)

RT = RGAS * Tc * Tr

print("Pvdat = {0}".format(Pvdat))
print("rk_in = {0}".format(rk))
print("Tr = {0}".format(Tr))


class Parameter_eos(object):
    """
    Parameter_eos contains the methods to adjust the parameters
    delta 1 rk for the energy parameter to a function of temperature and
    setting the parameter to represent a point of density - temperature curve
    """

    def energetic_parameter_cal(self, rk, delta_1_initial):

        self.ac = self.parameter_ab_cal(delta_1_initial)[0]
        self.a = self.ac * (3 / (2 + Tr)) ** rk

        return self.a

    def gvdW_Derivatives_cal(self, NDER, Volume, a, b, delta_1_initial):
        """
        gvdW_Derivatives_cal: calculate the derivatives from Generalized van
        der Waals equation of state
        """
        self.d = delta_1_initial

        c = (1 - self.d) / (1 + self.d)
        aRT = self.a / (RGAS * T_especific)
        relation_covolume = 0.25 * b / Volume
        SUMC = c * b + Volume
        SUMD = self.d * b + Volume
        REP = -np.log(1 - 4 * relation_covolume)
        ATT = aRT * np.log(SUMD / SUMC) / (b * (c - self.d))
        ATTV = aRT / SUMC / SUMD
        REPV = 1 / (1 - 4 * relation_covolume) - 1
        REP2V = 1 / (1 - 4 * relation_covolume) ** 2 - 1
        ATT2V = aRT * Volume ** 2 * (1 / SUMD ** 2 - 1 / SUMC ** 2) \
        / (b * (c - self.d))
        F = REP + ATT
        F_V = (- REPV / Volume + ATTV)

        if NDER == "Derivatives_of_V":
            F_2V = REP2V - ATT2V
            calculo_1 = "F_V"
            calculo_2 = "F_2V"
            return F, F_V, F_2V, calculo_1, calculo_2
        elif NDER == "Derivatives_of_N":
            F_N = REP + ATT - Volume * F_V
            calculo = "F_N"
            return F_N, calculo

    def volume_cal(self, ITYP, T, P, a, b, delta_1_initial):
        volume_iteration = 0
        VCP = b
        S3R = 1.0 / VCP
        zrelation_covolume_min, zrelation_covolume_max = 0.00, 0.99
        P_sur = P
        if ITYP >= 0.0:
            zrelation_covolume = 0.5
        else:
            # IDEAL GAS ESTIMATE
            zrelation_covolume = min(0.5, (VCP * P_sur) / (RGAS * T))
        while True:
            Volume = VCP / zrelation_covolume

            vdWg = self.gvdW_Derivatives_cal("Derivatives_of_V", Volume, a, b, delta_1_initial)
            F = vdWg[0]
            F_V = vdWg[1]
            F_2V = vdWg[2]
            pressure_cal_eos = RGAS * T * (1 / Volume - F_V)
            if pressure_cal_eos > P_sur:
                zrelation_covolume_max = zrelation_covolume
            else:
                zrelation_covolume_min = zrelation_covolume
            AT = F - np.log(Volume) + Volume * P_sur / (T * RGAS)
            DER = RGAS * T * (F_2V + 1.0) * S3R
            DEL = - (pressure_cal_eos - P_sur) / DER
            zrelation_covolume = zrelation_covolume + 1.0 * max(min(DEL, 0.1), -0.1)
            if zrelation_covolume > zrelation_covolume_max or zrelation_covolume < zrelation_covolume_min:
                zrelation_covolume = 0.5 * (zrelation_covolume_max + zrelation_covolume_min)
            if abs(DEL) < 1e-10 or volume_iteration >= 20:
                break
            volume_iteration += 1
        return Volume, pressure_cal_eos

    def phi_fagacity_cal(self, T, P, Volume, delta_1_initial):

        Z = P * Volume / RT
        vdWg = self.gvdW_Derivatives_cal("Derivatives_of_N", Volume, self.a, self.b, delta_1_initial)
        F_N = vdWg[0]
        phi_fugacity = np.exp(F_N) / Z
        return phi_fugacity

    def saturation_pressure_cal(self, PV_supuesta, rk_inicial, delta_1_initial):
        self.Tsat = Tr * Tc
        P_sur = PV_supuesta
        
        self.a = self.energetic_parameter_cal(rk_inicial, delta_1_initial)
        self.b = self.parameter_ab_cal(delta_1_initial)[1]

        self.volume_liquid = self.volume_cal(1, self.Tsat, P_sur, self.a,
        self.b, delta_1_initial)[0]

        phi_fugacity_liquid = self.phi_fagacity_cal(self.Tsat, P_sur,
        self.volume_liquid, delta_1_initial)

        self.volume_vapor = self.volume_cal(-1, self.Tsat, P_sur, self.a,
        self.b, delta_1_initial)[0]
        
        phi_fugacity_vapor = self.phi_fagacity_cal(self.Tsat, P_sur,
        self.volume_vapor, delta_1_initial)
        
        self.phase_equilibrium = abs(phi_fugacity_vapor - phi_fugacity_liquid)
        
        return self.phase_equilibrium

    def phase_equilibrium_cal(self, rk_inicial, delta_1_initial):
        PV_inicial = Pvdat

        rk_class = rk_inicial

        self.PV_calculed = fsolve(self.saturation_pressure_cal, PV_inicial,
        args=(rk_class, delta_1_initial), xtol=1e-4)

        return self.PV_calculed

    def funcion_saturacion_cal(self, rk_inicial, delta_1_initial):

        presion_saturada_modelo = self.phase_equilibrium_cal(rk_inicial, delta_1_initial)
        self.saturation_function = abs(presion_saturada_modelo - Pvdat) / Pvdat
        
        return self.saturation_function

    def resolver_rk_cal(self, rk_inicial, delta_1_initial):
        
        self.rk_calculated = fsolve(self.funcion_saturacion_cal, rk_inicial,
        args = (delta_1_initial), xtol=1e-4)

        return self.rk_calculated

    def parameter_ab_cal(self, delta_1_initial):
        RT = RGAS * T_especific
        d1 = (1 + delta_1_initial ** 2) / (1 + delta_1_initial)
        y = 1 + (2 * (1 + delta_1_initial)) ** (1.0 / 3) \
        + (4.0 / (1 + delta_1_initial)) ** (1.0 / 3.0)
        OMa = (3 * y * y + 3 * y * d1 + d1 ** 2 + d1 - 1.0) \
        / (3 * y + d1 - 1.0) ** 2
        OMb = 1 / (3 * y + d1 - 1.0)
        Zc = y / (3 * y + d1 - 1.0)
        dc = Pc / Zc / (RGAS * Tc)
        Vceos = 1.0 / dc

        self.ac = OMa * RT**2 / Pc
        self.b = OMb * RT / Pc

        return self.ac, self.b

    def density_cal(self, delta_1_initial, rk_inicial, Pvdat):

        self.b = self.parameter_ab_cal(delta_1_initial)[1]
        self.a = self.energetic_parameter_cal(rk_inicial, delta_1_initial)
        self.rk_calculated = self.resolver_rk_cal(rk_inicial, delta_1_initial)

        self.volume_liquid_delta = self.volume_liquid
        self.density_liquid = 1 / self.volume_liquid_delta        

        return self.density_liquid

    def density_function_cal(self, delta_1_initial, rk_inicial, Pvdat, RHOLSat_esp):

        RHOLSat_cal = self.density_cal(delta_1_initial, rk_inicial, Pvdat)
        self.density_function = abs(RHOLSat_cal - RHOLSat_esp)
        self.density_function = self.density_function / RHOLSat_esp        

        return self.density_function

    def resolver_delta_1_cal(self, delta_1_initial, rk_inicial, Pvdat, RHOLSat_esp):
        
        self.delta_1_calculated = fsolve(self.density_function_cal, delta_1_initial, args = (rk_inicial, Pvdat, RHOLSat_esp),
            xtol=1e-3)

        return self.delta_1_calculated


eos_calculation = Parameter_eos()
eos_calculation.phase_equilibrium_cal(rk, delta_1)

print("eos_calculation.resolver_rk_cal = {0}".format(eos_calculation.resolver_rk_cal(rk, delta_1)))


eos_calculation.parameter_ab_cal(delta_1)

eos_calculation.density_cal(delta_1, rk, Pvdat)

eos_calculation.density_function_cal(delta_1, rk, Pvdat, RHOLSat_esp)
print("density_function = {0}".format(eos_calculation.density_function))


eos_calculation.resolver_delta_1_cal(delta_1, rk, Pvdat, RHOLSat_esp)

print("-"*80)

print("Relative Error saturation pressure = {0}".format(eos_calculation.saturation_function))
print("phase_equilibrium (phi_l - phi_v) = {0}".format(eos_calculation.phase_equilibrium))

print("Density_function = {0}".format(eos_calculation.density_function))
print("delta_1_calculated = {0}".format(eos_calculation.delta_1_calculated))
print("rk_calculated = {0}".format(eos_calculation.rk_calculated))

print("volume_liquid_delta = {0}".format(eos_calculation.volume_liquid_delta))
print("density_liquid = {0}".format(eos_calculation.density_liquid))


