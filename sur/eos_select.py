import numpy as np

RGAS = 0.08314472

# Critical constants must be given in K and bar
# b will be in L/mol and ac in bar*(L/mol)**2

# PARAMETER (A0=0.0017,B0=1.9681,C0=-2.7238)
A0 = 0.0017
B0 = 1.9681
C0 = -2.7238

# PARAMETER (A1=-2.4407,B1=7.4513,C1=12.504)
A1 = -2.4407
B1 = 7.4513
C1 = 12.504

D = np.array([0.428363,18.496215,0.338426,0.660,789.723105,2.512392])
NC = 2
NIN = 1
nout = 9

nmodel = 3
ICALC = 0

Tc = 334.0
Pc = 13.3
Vceos = 0.34


# 1  3  0                             ICALC,NMODEL,IVAP
# 2422.44    3.90091    1.80323 8.60102        ac,b,del1,rk

# Me sale este output:
# 1377.9116    2.4027       NaN 15.22254
# 2422.4400  3.900910  1.803230   8.60102
#----------------------------------------------------------------
def getdel1(Zcin, del1ini, del1):

	del1 = del1ini
	d1 = (1 + del1 ** 2) / (1 + del1)
	y = 1 + (2 * (1 + del1)) ** (1.0 / 3) + (4 / (1 + del1)) ** (1.0 / 3)
	Zc = y / (3 * y + d1 - 1.0)
	dold = del1

	if Zc > Zcin: #(Zc.gt.Zcin)then
	    del1 = 1.01 * del1
	else:
		del1 = 0.99 * del1

	err = abs(Zc - Zcin)

	while err >= 1e-6:
		d1 = (1 + del1 ** 2) / (1 + del1)
		y = 1 + (2 * (1 + del1)) ** (1.0 / 3) + (4 / (1 + del1)) ** (1.0 / 3)
		Zold = Zc
		Zc = y / (3 * y + d1 -1.0)
		aux = del1
		del1 = del1 - (Zc - Zcin) * (del1 - dold) / (Zc - Zold)
		dold = aux
		err = abs(Zc - Zcin)
	return del1, err


def intermedio_cal(del1):
	d1 = (1 + del1 ** 2) / (1 + del1)
	y = 1 + (2 * (1 + del1)) ** (1.0 / 3) + (4 / (1 + del1)) ** (1.0 / 3)
	OMa = (3 * y * y + 3 * y * d1 + d1 ** 2 + d1 - 1.0) / (3 * y + d1 - 1.0) ** 2
	OMb = 1 / (3 * y + d1 - 1.0)
	Zc = y / (3 * y + d1 - 1.0)
	return Zc, OMa, OMb


"""
ICALC = [0, 1, 2, 3]
NMODEL = [1, 2, 3]
Sin contar IVAP, puesto que se define actualmente siempre IVAP = 0,
se tienen 12 casos de posibles especificaciones
"""

#prueba = "SRK_0" # ICALC, NMODEL, IVAP = 0, 1, 0 
#prueba = "SRK_1" # ICALC,NMODEL,IVAP = 1, 1, 0


#prueba = "PR_0" # ICALC, NMODEL, IVAP = 0, 2, 0 
#prueba = "PR_1" # ICALC,NMODEL,IVAP = 1, 2, 0


#prueba = "RKPR_0" # ICALC, NMODEL, IVAP = 0, 3, 0 
prueba = "RKPR_1" # ICALC,NMODEL,IVAP = 1, 3, 0
#prueba = "RKPR_2" # ICALC,NMODEL,IVAP = 2, 3, 0
#prueba = "RKPR_3" # ICALC,NMODEL,IVAP = 3, 3, 0


if prueba == "RKPR_0":    
    #305.32  48.72  0.09949  0.1724175  1.185	Tc, Pc, omega, Vceos(L/mol)  C2       
    ICALC, NMODEL, IVAP = 0, 3, 0    
    componente = "Etano_RKPR_0"    
    Tc, Pc, omega, Vceos = 305.32, 48.72, 0.09949, 0.1724175 #  1.185
    print("componente = {0} \nTc = {1} \nPc = {2} \nomega = {3} \nVceos = {4}".format(componente, Tc, Pc, omega, Vceos))
    
    RT = RGAS * Tc
    Zc = Pc * Vceos / RT
    print("Zc = {0}".format(Zc))    
    del1ini = D[0] + D[1] * (D[2] - Zc)**D[3] + D[4] * (D[2] - Zc)**D[5]
    print("del1ini = {0}".format(del1ini))

    dinputs = np.array([Tc, Pc, omega, Vceos])
    
elif prueba == "RKPR_1":
    # 1  3  0                         	ICALC,NMODEL,IVAP
    # 2422.44    3.90091	1.80323 8.60102		ac,b,del1,rk
    # Me sale este output:
    # 1377.9116    2.4027       NaN 15.22254
    # 2422.4400  3.900910  1.803230   8.60102
    ICALC,NMODEL,IVAP = 1, 3, 0
    componente = "Prueba_1_RKPR_1"
    ac,b,del1,rk = 2422.44, 3.90091, 1.80323, 8.60102
    print("componente = {0} \nac = {1} \nb = {2} \ndel1 = {3} \nrk = {4}".format(componente, ac,b,del1,rk))

    dinputs = np.array([ac,b,del1,rk])
elif prueba == "RKPR_2":
    #2  3  0                         	ICALC,NMODEL,IVAP 
    #			          Tc	Pc(bar)		W	Zc	dc(mol/L)
    #CYCLOPROPANE		397.91	54.94956075	0.1269	0.27	6.142506143
    # del1 SPECIFICATION together with Tc,Pc,OM
    ICALC,NMODEL,IVAP = 2, 3, 0
    componente = "CYCLOPROPANE_RKPR_2"
    Tc, Pc, W, Zc, dc = 397.91, 54.94956075, 0.1269, 0.27, 6.142506143
    print("componente = {0} \nTc = {1} \nPc = {2} \nW = {3} \nZc = {4} \ndc = {5}".format(componente, Tc, Pc, W, Zc, dc))
    
elif prueba == "RKPR_3":
    # ! RhoLsat SPECIFICATION together with Tc,Pc,OM
    # READ(NIN,*)T, RhoLsat
    # Trho = T/Tc 
    del1 = 2.0    #!  initial value
    RHOld = 0.0
elif prueba == "PR_0":
    # 0  2  0                         	ICALC,NMODEL,IVAP
    
    ICALC, NMODEL, IVAP = 0, 2, 0 
    
    #                Tc,     Pc,   omega
    # Saturates  	930 	11.98	0.9 	1.35
    # Arom+Resins	1074	10.85	1.5 	1.35
    # Asphaltenes	1274	6.84	1.75	1.35
    componente = "Asphaltenes"
    Tc, Pc, OM = 1274.0, 6.84, 1.75
    print("componente = {0} \nTc = {1} \nPc = {2} \nOM = {3}".format(componente, Tc, Pc, OM))
    dinputs = np.array([Tc, Pc, OM])
    del1 = 1
elif prueba == "PR_1":
    pass
    

if NMODEL == 1:
	NMODEL = "SRK"
elif NMODEL == 2:
	NMODEL == "PR"
elif NMODEL == 3:
	NMODEL = "RKPR"

if ICALC == 0:
	ICALC = "constants_eps"
elif ICALC == 1:
	ICALC = "parameters_eps"
elif ICALC == 2:
	ICALC = "rk_param"
elif ICALC == 3:
	ICALC = "density"




if NMODEL == "SRK" or NMODEL == "PR":
	# CONSTANTS SPECIFICATION READ(Tc,Pc,OM)
	if ICALC == "constants_eps":
		Tc = dinputs[0]
		Pc = dinputs[1]
		OM = dinputs[2]
		RT = RGAS * Tc
		print("CONSTANTS SPECIFICATION","\t","READ(Tc,Pc,OM)")
		print("componente = {0} \nTc = {1} \nPc = {2} \nOM = {3}".
        	format(componente, Tc, Pc, OM))

		ac = OMa * RT **2 / Pc
		b = OMb * RT / Pc

		if NMODEL == "SRK":
			rm = 0.48 + 1.574 * OM - 0.175 * OM**2  # ! m from SRK
			ecuacion_cubica = "SRK"
			del1 = 1.0
			print("SRK EOS","\t","del1 = {0}".format(del1))
		elif NMODEL == "PR":
			rm = 0.37464 + 1.54226 * OM - 0.26992 * OM**2 # ! m from PR
			ecuacion_cubica = "PR"
			del1 = 1.0 + np.sqrt(2.0)
			print("PR EOS","\t","del1 = {0}".format(del1))

		Zc, OMa, OMb = intermedio_cal(del1)

		Vceos = Zc * RGAS * Tc / Pc
		print("\necuacion_cubica = {0} \nrm = {1} \nZc = {2} \nVceos = {3}".format(ecuacion_cubica, rm, Zc, Vceos))

	if ICALC == "parameters_eps":
		Tc = OMb * ac/ (OMa * RGAS * b)
		Pc = OMb * RGAS * Tc/b
		Vceos = Zc * RGAS * Tc/Pc

		if NMODEL == "SRK":
			print("PARAMETERS SPECIFICATION","\t","READ(ac,b,rM)")
			print("componente = {0} \nac = {1} \nb = {2} \ndel1 = {3} \nrk = {4}".format(componente, ac,b,del1,rk))
			del1 = 1.0
			print("SRK EOS","\t","del1 = {0}".format(del1))
			al =-0.175
			be = 1.574
			ga = 0.48 - rm #		! m from SRK
		elif NMODEL == "PR":
			del1 = 1.0 + np.sqrt(2.0)
			print("PR EOS","\t","del1 = {0}".format(del1))
			al =-0.26992
			be = 1.54226
			ga = 0.37464 - rm #	! m from PR

		OM = 0.5 * (-be + np.sqrt(be**2 - 4*al*ga)) / al
		print("al = {0} \nbe= {1} \nga = {2}".format(al, be, ga))
		print("(be**2-4*al*ga) = {0}".format(be**2-4*al*ga))

		#write(nout,*)'Parameters were specified and constants calculated'
		print("Parameters were specified and constants calculated")
		print("\nTc = {0} \nPc = {1} \nOM = {2} \nVceos = {3}".format(Tc, Pc, OM, Vceos))

		mensaje_2 = """\nMartín Dice:
		Me sale este output:
		# 1377.9116    2.4027       NaN 15.22254
		# 2422.4400  3.900910  1.803230   8.60102"""

		print(mensaje_2)

elif NMODEL == "RKPR": #	RKPR EOS
    if ICALC == "constants_eps": # CONSTANTS SPECIFICATION (Tc,Pc,OM,Vceos)
    	Tc = dinputs[0]
    	Pc = dinputs[1]
    	OM = dinputs[2]
    	Vceos = dinputs[3]
    	RT = RGAS * Tc
    	Zc = Pc * Vceos / RT
    	print("Zc = {0}".format(Zc))
    	del1ini = D[0] + D[1] * (D[2] - Zc)**D[3] + D[4] * (D[2] - Zc)**D[5]
    	print("del1ini = {0}".format(del1ini))

    	Zcin = Zc
    	del1ini
    	del1 = del1ini*1.2
    	calcular_delta_1 = getdel1(Zcin, del1ini, del1)
    	print("\ndelta_1 = {0} \nErr = abs(Zc - Zcin) = {1}".format(calcular_delta_1[0], calcular_delta_1[1]))        
        
    elif ICALC == "parameters_eps": #PARAMETERS SPECIFICATION (ac,b,del1,rk)
        print("componente = {0} \nac = {1} \nb = {2} \ndel1 = {3} \nrk = {4}".
        	format(componente, ac,b,del1,rk))

        ac = dinputs[0]
        b = dinputs[1]
        del1 = dinputs[2]
        rk = dinputs[3]

        Zc, OMa, OMb = intermedio_cal(del1)

        Tc = OMb * ac/ (OMa * RGAS * b)
        Pc = OMb * RGAS * Tc/b
        Vceos = Zc * RGAS * Tc/Pc

        al = A1 * Zc + A0
        be = B1 * Zc + B0
        ga = C1 * Zc + C0 - rk

        OM = 0.5 * (-be + np.sqrt(be**2 - 4*al*ga)) / al
        print("al = {0} \nbe= {1} \nga = {2}".format(al, be, ga))
        print("(be**2-4*al*ga) = {0}".format(be**2-4*al*ga))

        #write(nout,*)'Parameters were specified and constants calculated'

        print("Parameters were specified and constants calculated")
        print("\nTc = {0} \nPc = {1} \nOM = {2} \nVceos = {3}".format(Tc, Pc, OM, Vceos))
    
    elif ICALC == "rk_param": # RKPR EOS (Tc,Pc,OM) 
        RT = RGAS * Tc
        # THEN	! del1 SPECIFICATION together with Tc,Pc,OM
        # READ(NIN,*)del1  ! this line must be active when it is not a list
        s = 0
    elif ICALC == "density": # RhoLsat SPECIFICATION together with Tc,Pc,OM
        # (T, RhoLsat)
        Trho = T / Tc
        del1 = 2.0    #!  initial value
        RHOld = 0.0
    print("RKPR EOS","\t","ICALC = {0}".format(ICALC))



