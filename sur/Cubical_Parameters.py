import numpy as np
from scipy.optimize import fsolve
"""
This module calculate parameters necessary to use the equations of state:
SRK, PR and RKPR

"""

# acá encontré esto que lo tenía aparte, como un ejemplo de ese tipo de corrida con un RHOLSat
# 3  3    0                         ICALC,NMODEL
# 304.21  73.83  0.2236      Tc, Pc, omega
# 270.0  21.4626                 T(K), RhoLsat (L/mol)

# Critical constants must be given in K and bar
# b will be in L/mol and ac in bar*(L/mol)**2


RGAS = 0.08314472
# Definir el significado fisicoquímico

A0, B0, C0 = 0.0017, 1.9681, -2.7238

# Definir el significado fisicoquímico
A1, B1, C1 = -2.4407, 7.4513, 12.504
# Definir el significado fisicoquímico

D = np.array([0.428363, 18.496215, 0.338426, 0.660, 789.723105, 2.512392])

# METHANE (1)
Tc, Pc, ohm, vc, zrat = 190.564, 45.99, 0.01155, 0.115165, 1.00000173664
ac, b, d, rk = 2.3277, 0.029962, 0.932475, 1.49541
#   Tr = 0.7 # Change here to use another Pv than the one at Tr 0.7
Tr = 0.7

delta_1 = d
delta_1 = 2.0


print ("delta_1 = {0}".format(delta_1))

#dc = 1 / vc
OM = ohm


d1 = (1 + delta_1 ** 2) / (1 + delta_1)
y = 1 + (2 * (1 + delta_1)) ** (1.0 / 3) + (4 / (1 + delta_1)) ** (1.0 / 3)
OMa = (3 * y * y + 3 * y * d1 + d1 ** 2 + d1 - 1.0) / (3 * y + d1 - 1.0) ** 2
OMb = 1 / (3 * y + d1 - 1.0)
Zc = y / (3 * y + d1 - 1.0)

#dc = Pc / Zc / (RGAS * Tc)
#Vceos = 1.0 / dc

RT = RGAS * Tc*Tr

ac = OMa * RT**2 / Pc
b = OMb * RT / Pc

print("Zc = {0}".format(Zc))
print("ac = {0}".format(ac))
print("b = {0}".format(b))



# initial guess for k parameter
rk = (A1 * Zc + A0) * OM**2 + (B1 * Zc + B0) * OM + (C1 * Zc + C0)
rk = rk * 1.2
Pvdat = Pc * 10 ** -(1.0 + OM)
print("Pvdat = {0}".format(Pvdat))


class Parameter_eos(object):
    """Parameter_eos contains the methods to adjust the parameters delta 1 rk for the energy parameter to a function of temperature and setting the parameter to represent a point of density - temperature curve """

    def __init__(self, *arg):
        #self.T = arg[0]
        #self.V = arg[1]
        #self.P = arg[2]
        #self.rk= arg[0]
        self.d = arg[0]        

    
    def parametro_a_cal(self, ac, rk, delta_1):

        #ac_calculado = self.recalcular_parametros_cal(delta_1)[0]
        self.a = ac * (3 / (2 + Tr)) ** rk
        return self.a


    def vdWg_Derivs_cal(self, NDER, V, b):

        C = (1 - self.d) / (1 + self.d)
        aRT = self.a / (RGAS * self.T)
        ETA = 0.25 * b / V
        SUMC = C * b + V
        SUMD = self.d * b + V
        REP = -np.log(1 - 4 * ETA)
        ATT = aRT * np.log(SUMD / SUMC) / (b * (C - self.d))
        ATTV = aRT / SUMC / SUMD
        REPV = 1 / (1 - 4 * ETA) - 1
        REP2V = 1 / (1 - 4 * ETA) ** 2 - 1
        ATT2V = aRT * V ** 2 * (1 / SUMD ** 2 - 1 / SUMC ** 2) / (b * (C - self.d))
        F = REP + ATT
        F_V = (- REPV / V + ATTV)

        if NDER == 1:
            F_2V = REP2V - ATT2V
            calculo_1 = "F_V"
            calculo_2 = "F_2V"
            return F, F_V, F_2V, calculo_1, calculo_2
        else:
            F_N = REP + ATT - V * F_V
            calculo = "F_N"
            return F_N, calculo


    def VCALC(self, ITYP, T, P, b):
 
        volume_iteration = 0
        VCP = b
        S3R = 1.0 / VCP
        zeta_min, zeta_max = 0.00, 0.99
        P_sur = P
        if ITYP >= 0.0:
            zeta = 0.5
        else:
            # IDEAL GAS ESTIMATE
            zeta = min(0.5, (VCP * P_sur) / (RGAS * self.T))
        while True:
            V = VCP / zeta

            vdWg = self.vdWg_Derivs_cal(1, V, b)
            F = vdWg[0]
            F_V = vdWg[1]
            F_2V = vdWg[2]
            pressure_cal_eos = RGAS * self.T * (1 / V - F_V)
            if pressure_cal_eos > P_sur:
                zeta_max = zeta
            else:
                zeta_min = zeta
            AT = F - np.log(V) + V * P_sur / (self.T * RGAS)
            DER = RGAS * self.T * (F_2V + 1.0) * S3R
            DEL = - (pressure_cal_eos - P_sur) / DER
            zeta = zeta + 1.0 * max(min(DEL, 0.1), -0.1)
            if zeta > zeta_max or zeta < zeta_min:
                zeta = 0.5 * (zeta_max + zeta_min)
            if abs(DEL) < 1e-10 or volume_iteration >= 50:
                break
            volume_iteration += 1
        return V, pressure_cal_eos


    def phi_fagacity_cal(self, T, P, V):
        RT = RGAS * self.T
        P_sur = P
        print("self.vol = {0}".format(V))
        print("self.P = {0}".format(P))
        print("self.P_sur = {0}".format(P_sur))

        Z = P_sur * V / RT
        vdWg = self.vdWg_Derivs_cal(2, V, b)
        F_N = vdWg[0]
        phi_fugacity = np.exp(F_N) / Z
        return phi_fugacity


    def saturation_pressure_cal(self, PV_supuesta, ac_inicial, rk_inicial):
        self.T = Tr * Tc
        P_sur = PV_supuesta
        print(self.T, Tr, P_sur)
        
        self.a = self.parametro_a_cal(ac, rk_inicial, delta_1)
        self.volume_liquid = self.VCALC(1, self.T, P_sur, b)[0]
        print("liquid_volume = {0}".format(self.volume_liquid))

        phi_fugacity_liquid = self.phi_fagacity_cal(self.T, P_sur, self.volume_liquid)
        print("phi_fugacity_liquid = {0}".format(phi_fugacity_liquid))

        self.volume_vapor = self.VCALC(-1, self.T, P_sur, b)[0]
        print("vapor_volume = {0}".format(self.volume_vapor))        
        
        phi_fugacity_vapor = self.phi_fagacity_cal(self.T, P_sur, self.volume_vapor)

        print("phi_fugacity_vapor = {0}".format(phi_fugacity_vapor))
        
        phase_equilibrium = abs(phi_fugacity_vapor - phi_fugacity_liquid)
        print("phase_equilibrium (phi_l - phi_v) = {0}".format(
            phase_equilibrium))
        return phase_equilibrium

    def resolver_fases_cal(self, rk_inicial, ac_inicial):
        PV_experimental = Pvdat
        PV_inicial = PV_experimental * 1.1
        print("PV_experimental  = {0}".format(PV_experimental))
        print("PV_inicial = {0}".format(PV_inicial))
        rk_class = rk_inicial
        ac_class = ac_inicial

        PV_calculada = fsolve(self.saturation_pressure_cal, PV_inicial, args=(ac_class, rk_class), xtol=1e-4)

        print("Presion de saturación = {0} Bar".format(PV_calculada[0]))

        return PV_calculada

    def funcion_saturacion_cal(self, rk_inicial, ac_inicial):

        self.a = self.parametro_a_cal(ac, rk_inicial, delta_1)
        presion_saturada_modelo = self.resolver_fases_cal(rk_inicial, ac_inicial)
        funcion_saturacion = abs(presion_saturada_modelo - Pvdat) / Pvdat
        print("error_presion_relativo = {0}".format(funcion_saturacion))

        return funcion_saturacion

    def resolver_rk_cal(self, rk_inicial, ac_inicial):

        rk_cls = rk_inicial
        ac_cls = ac_inicial
        self.rk_calculado = fsolve(self.funcion_saturacion_cal, rk_cls, args=(ac_cls), xtol=1e-4)
        print ("rk_calculado = {0}".format(self.rk_calculado))

        return self.rk_calculado

    def recalcular_parametros_cal(self, delta_1):
        RT = RGAS * self.T

        d1 = (1 + delta_1 ** 2) / (1 + delta_1)
        y = 1 + (2 * (1 + delta_1)) ** (1.0 / 3) + (4 / (1 + delta_1)) ** (1.0 / 3)
        OMa = (3 * y * y + 3 * y * d1 + d1 ** 2 + d1 - 1.0) / (3 * y + d1 - 1.0) ** 2
        OMb = 1 / (3 * y + d1 - 1.0)
        Zc = y / (3 * y + d1 - 1.0)
        dc = Pc / Zc / (RGAS * Tc)
        Vceos = 1.0 / dc

        ac = OMa * RT**2 / Pc
        b = OMb * RT / Pc

        print("Zc = {0}".format(Zc))
        print("ac = {0}".format(ac))
        print("b = {0}".format(b))

        return ac, b

    def density_cal(self, ac_inicial, rk_inicial, Pvdat):       

        rk_inicial = self.resolver_rk_cal(rk_inicial, ac_inicial)
        print("rk_inicial ______= {0}".format(rk_inicial))

        self.volume_liquid = self.VCALC(1, self.T, Pvdat, b)[0]
        print("volume_liquid = {0}".format(self.volume_liquid))
        self.density_liquid = 1 / self.volume_liquid
        print("density_liquid = {0}".format(self.density_liquid))

        return self.density_liquid

            

calculo_1 = Parameter_eos(delta_1)
calculo_1.resolver_fases_cal(rk, ac)
calculo_1.resolver_rk_cal(rk, ac)
#calculo_1.recalcular_parametros_cal(delta_1)
#calculo_1.density_cal(ac, rk, Pvdat)

#print("Parametro rk_calculado = {0}".format(calculo_1.rk_calculado))
