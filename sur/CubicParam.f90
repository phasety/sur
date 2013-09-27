
subroutine ModelsParam(icalc, nmodel, dinputs, ni, pvdat, t_pvdat, constants, params)
    implicit DOUBLE PRECISION (A-H,O-Z)
    PARAMETER (RGAS=0.08314472d0)
!    Critical constants must be given in K and bar
!    b will be in L/mol and ac in bar*(L/mol)**2
    PARAMETER (A0=0.0017,B0=1.9681,C0=-2.7238)
    PARAMETER (A1=-2.4407,B1=7.4513,C1=12.504)
    dimension D(6)
    dimension dinputs(ni), constants(4), params(4)
    !f2py intent(in) :: inputs
    !f2py intent(out) :: constants, params
    !f2py intent(hide) :: ni
    !f2py optional :: pvdat, t_pvdat


    COMMON /Tcdc/ Tc,dc
    COMMON /ABd1/ a,b,del1


    D=[0.428363,18.496215,0.338426,0.660,789.723105,2.512392]
    NC=2
    NIN = 1
    IF(NMODEL == 4)GO TO 104
    IF(nmodel <= 2)THEN
        IF(ICALC == 0)THEN        ! CONSTANTS SPECIFICATION
            Tc = dinputs(1)
            Pc = dinputs(2)
            OM = dinputs(3)
            RT=RGAS*Tc
        ELSE                    ! PARAMETERS SPECIFICATION
            ac = dinputs(1)
            b = dinputs(2)
            rM = dinputs(3)
        END IF
        IF(nmodel == 1)THEN
        !        SRK EOS
            del1=1.0D0
        ELSE
        !        PR EOS
            del1=1.0D0+sqrt(2.0)
        END IF
    ELSE
    !    RKPR EOS
        IF(ICALC == 0)THEN        ! CONSTANTS SPECIFICATION
            Tc = dinputs(1)
            Pc = dinputs(2)
            OM = dinputs(3)
            Vceos = dinputs(4)
            RT=RGAS*Tc
            Zc=Pc*Vceos/RT
            del1ini=D(1)+D(2)*(D(3)-Zc)**D(4)+D(5)*(D(3)-Zc)**D(6)
            call getdel1 (Zc,del1ini,del1)
        ELSE IF(ICALC == 1)THEN    ! PARAMETERS SPECIFICATION
            ac = dinputs(1)
            b = dinputs(2)
            del1 = dinputs(3)
            rk = dinputs(4)
        ELSE
            Tc = dinputs(1)
            Pc = dinputs(2)
            OM = dinputs(3)
            RT=RGAS*Tc
            IF(ICALC == 2)THEN    ! del1 SPECIFICATION together with Tc,Pc,OM
                del1 = dinputs(4)
            ELSE   ! RhoLsat SPECIFICATION together with Tc,Pc,OM
                T = dinputs(4)
                RhoLsat = dinputs(5)
                Trho=T/Tc
                del1=2.0    !  initial value
                RHOld = 0.d0
            END IF
        END IF
    END IF
    11    d1=(1+del1**2)/(1+del1)
    y=1+(2*(1+del1))**(1.0d0/3)+(4/(1+del1))**(1.0d0/3)
    OMa=(3*y*y+3*y*d1+d1**2+d1-1.0d0)/(3*y+d1-1.0d0)**2
    OMb=1/(3*y+d1-1.0d0)
    Zc=y/(3*y+d1-1.0d0)
    IF(ICALC == 1) then ! PARAMETERS SPECIFICATION
        Tc=OMb*ac/(OMa*RGAS*b)
        Pc=OMb*RGAS*Tc/b
        Vceos=Zc*RGAS*Tc/Pc
        IF(nmodel == 3)THEN
            al=A1*Zc+A0
            be=B1*Zc+B0
            ga=C1*Zc+C0-rk
        ELSE IF(nmodel == 1)THEN
            al=-0.175
            be=1.574
            ga=0.48-rm        ! m from SRK
        ELSE
            al=-0.26992
            be=1.54226
            ga=0.37464-rm    ! m from PR
        END IF
        OM=0.5*(-be+sqrt(be**2-4*al*ga))/al
    !        write(nout,*)'Parameters were specified and constants calculated'
    ELSE  ! CONSTANTS SPECIFICATION (ICALC = 0,2,3)
        ac=OMa*RT**2/Pc
        b=OMb*RT/Pc
        if(icalc == 2)Vceos=Zc*RGAS*Tc/Pc
        IF(nmodel == 3)THEN
            dc=Pc/Zc/RT
            rk=(A1*Zc+A0)*OM**2+(B1*Zc+B0)*OM+(C1*Zc+C0) ! initial guess for k parameter
            Tr=0.7D0    ! Change here to use another Pv than the one at Tr 0.7
            a=ac*(3/(2+Tr))**rk

            if (pvdat == 0) then
                Pvdat=Pc*10**(-(1.0D0+OM))
            else
                Tr=t_pvdat/Tc
            end if
            CALL VaporPressure(Tr,Pvdat,Pv,RHOL,RHOV,phiL)
            if(Pv>Pvdat)then
                dk = 0.1
            else
                dk = -0.1
            end if
            do while (abs(Pv-Pvdat)/Pvdat>0.005)
                Pold = Pv
                oldk = rk
                rk = rk + dk
                a=ac*(3/(2+Tr))**rk
                CALL VaporPressure(Tr,Pvdat,Pv,RHOL,RHOV,phiL)
                dk = -(Pv-Pvdat)*(rk-oldk)/(Pv-Pold)
            end do
        ELSE
            Zc=y/(3*y+d1-1.0d0)
            Vceos=Zc*RGAS*Tc/Pc
            IF(nmodel == 1)THEN
                rm=0.48+1.574*OM-0.175*OM**2  ! m from SRK
            ELSE
                rm=0.37464+1.54226*OM-0.26992*OM**2  ! m from PR
            END IF
        END IF
        IF(nmodel == 3 .AND. icalc==3)THEN  ! November 2011 for RKPR specifying T, RHOLsat
            if (abs(Trho-0.70)>1.d-2) then  ! get calculated RHOL when Trho is no 0.70
                Pvdat=Pc*10**(-((1./Trho-1d0)*7*(1.0D0+OM)/3))
                a=ac*(3/(2+Trho))**rk
                CALL VaporPressure(Trho,Pvdat,Pv,RHOL,RHOV,phiL)
            end if
            if (RHOld==0.d0) then
                dold1 = del1
                if(abs(RHOL-RHOLSAT)/RHOLSAT>1.d-4)del1=2.1  ! condition for the strange case that del1=2 is solution
            else
                ddel1 = -(RHOL-RhoLsat)*(del1-dold1)/(RHOL-RHOld)
                dold1 = del1
                del1 = del1 + ddel1
            end if
            RHOld = RHOL
            if(abs(RHOL-RHOLSAT)/RHOLSAT>1.d-4) go to 11
            d1=(1+del1**2)/(1+del1)
            y=1+(2*(1+del1))**(1.0d0/3)+(4/(1+del1))**(1.0d0/3)
            OMa=(3*y*y+3*y*d1+d1**2+d1-1.0d0)/(3*y+d1-1.0d0)**2
            OMb=1/(3*y+d1-1.0d0)
            Zc=y/(3*y+d1-1.0d0)
            ac=OMa*RT**2/Pc
            b=OMb*RT/Pc
        END IF
    !        write(nout,*)'Constants were specified and parameters calculated'
    END IF
    Vceos=1.0d0/dc

    !write(nout,1)Tc,Pc,OM,Vceos  ! it used to be "Vceos,OM" (changed 5/7/13 to imitate gpecin standard)

    constants(1) = Tc
    constants(2) = Pc
    constants(3) = OM
    constants(4) = Vceos

    IF(nmodel == 3)THEN
        params(1) = ac
        params(2) = b
        params(3) = del1
        params(4) = rk
    ELSE
        params(1) = ac
        params(2) = b
        params(3) = rm
    END IF
    104    continue
    end
!
    subroutine getdel1 (Zcin,del1ini,del1)
    implicit DOUBLE PRECISION (A-H,O-Z)
    del1=del1ini
    d1=(1+del1**2)/(1+del1)
    y=1+(2*(1+del1))**(1.0d0/3)+(4/(1+del1))**(1.0d0/3)
    Zc=y/(3*y+d1-1.0d0)
    dold=del1
    if(Zc > Zcin)then
        del1=1.01*del1
    else
        del1=0.99*del1
    end if
    2    d1=(1+del1**2)/(1+del1)
    y=1+(2*(1+del1))**(1.0d0/3)+(4/(1+del1))**(1.0d0/3)
    Zold=Zc
    Zc=y/(3*y+d1-1.0d0)
    aux=del1
    del1=del1-(Zc-Zcin)*(del1-dold)/(Zc-Zold)
    dold=aux
    err=abs(Zc-Zcin)
    if(err > 1.0d-6)go to 2
    end
!
!
    SUBROUTINE VaporPressure(Tr,PVini,Pv,RHOL,RHOV,phiL)
    IMPLICIT DOUBLE PRECISION (A-H,O-Z)
    PARAMETER (ERRMAX=1.D-8)
    COMMON /Tcdc/ Tc,dc
    dphi = 0.0D0
    P = PVini
    n=1
    T=Tr*Tc
    30    call VCALC(1,T,P,V)
    RHOL = 1/V
    call VCALC(-1,T,P,V) ! SOLVE for vapor density
    RHOV = 1/V
    if(RHOL < 0.9*dc) then
        P=1.01*P
        go to 30
    else if(RHOV > dc) then
        P=0.99*P
        go to 30
    end if
    call FUG_CALC(T,P,1/RHOL,phi)
    phiL = phi
    call FUG_CALC(T,P,V,phi)
    phiV = phi
    dphiold = dphi
    dphi = phiV - phiL
    IF (ABS(dphi) > ERRMAX) THEN
        Pold = Plast
        Plast = P
        if(dphiold == 0.0D0 .OR. Tr > 0.975) then
            P = P * (phiL/phiV)
        else
            P = Plast - dphi*(Plast-Pold)/(dphi-dphiold)
        end if
    !        n=n+1
        GO TO 30
    END IF
    PV = P
!      WRITE (31,*) ' n=',n
    return
    END
!
    SUBROUTINE VCALC(ITYP,T,P,V)
!
!     ROUTINE FOR CALCULATION OF VOLUME, GIVEN PRESSURE
!
!     INPUT:
!
!     ITYP:        TYPE OF ROOT DESIRED
!     T:           TEMPERATURE
!     P:           PRESSURE
!
!     OUTPUT:
!
!     V:           VOLUME
!
    IMPLICIT DOUBLE PRECISION (A-H,O-Z)
    PARAMETER (RGAS=0.08314472d0)
    LOGICAL :: FIRST_RUN
    COMMON /ABd1/ a,b,d1
    FIRST_RUN = .TRUE.
    VCP = b
    S3R = 1.D0/VCP
    ITER = 0
!
    ZETMIN = 0.D0
    ZETMAX = .99D0
    IF (ITYP > 0) THEN
        ZETA = .5D0
    ELSE
    !..............IDEAL GAS ESTIMATE
        ZETA = MIN (.5D0,VCP*P/(RGAS*T))
    ENDIF
    100 CONTINUE
!    WRITE(*,*)'ZETA',ZETA
    V = VCP/ZETA
    ITER = ITER + 1
    CALL vdWg_Derivs(1,T,V,F,F_V,F_2V,F_N)
    PCALC = RGAS*T*(1/V - F_V)
!    WRITE(*,*)'PCALC',PCALC
    IF (PCALC > P) THEN
        ZETMAX = ZETA
    ELSE
        ZETMIN = ZETA
    ENDIF
!    write(*,*)'VCALC V=',V
    AT  = F - LOG(V) + V*P/(T*RGAS)
    DER = RGAS*T*(F_2V+1.D0)*S3R
    DEL = -(PCALC-P)/DER
    ZETA = ZETA + MAX (MIN(DEL,0.1D0),-.1D0)
    IF (ZETA > ZETMAX .OR. ZETA < ZETMIN) &
    ZETA = .5D0*(ZETMAX+ZETMIN)
    IF (ABS(DEL) > 1D-10) GOTO 100
    IF (ITYP == 0 ) THEN
    !
    ! FIRST RUN WAS VAPOUR; RERUN FOR LIQUID
    !
        IF (FIRST_RUN) THEN
            VVAP = V
            AVAP = AT
            FIRST_RUN = .FALSE.
            ZETA = 0.5D0
            GOTO 100
        ELSE
            IF (AT > AVAP) V = VVAP
        ENDIF
    ENDIF
    return
    END
!
    SUBROUTINE FUG_CALC(T,P,V,phi)
    IMPLICIT DOUBLE PRECISION (A-H,O-Z)
    PARAMETER (RGAS=0.08314472d0)
    RT = RGAS*T
    Z = P*V/RT
    CALL vdWg_Derivs(2,T,V,F,F_V,F_2V,F_N)
    PHI=EXP(F_N)/Z
    return
    END
!
!
    subroutine vdWg_Derivs(NDER,T,V,F,F_V,F_2V,F_N)
!
!     THE SUBROUTINE CALCULATES THE CONTRIBUTION TO THE RESIDUAL,
!     REDUCED HELMHOLZ ENERGY (F) AND
!     ITS FIRST AND SECOND DERIVATIVE WRT V
!
!     INPUT:
!    NDER:         indicates which derivatives are required.
!                 1 is used for density calculation and 2 for fugacity
!        NDER = 1: CALCULATES F, F_V AND F_2V
!         NDER = 2: CALCULATES F AND F_N
!     T:           TEMPERATURE
!     V:           VOLUME (ML/MOL) or (ML) for checking n-derivatives
!
!     OUTPUT:       NDER
!     F:            5    A^RES/RT CONTRIBUTION (DIMENSIONLESS) or (MOLES)
!     F_V:        5    1ST V-DERIVATIVE OF F
!     F_2V:            1ST V-DERIVATIVE OF F_V  (*V**2)
!     F_N:            1ST N-DERIVATIVE OF F
    IMPLICIT DOUBLE PRECISION (A-H,O-Z)
    PARAMETER (RGAS=0.08314472d0)
    COMMON /ABd1/ a,b,d
    C = (1-d)/(1+d)
    aRT = a / (RGAS*T)
    ETA = 0.25 * b / V
    SUMC = c*b+V
    SUMD = d*b+V
    REP = -log(1-4*ETA)
    ATT = aRT*LOG(SUMD/SUMC)/(b*(C-D))
    ATTV = aRT/SUMC/SUMD
    REPV = 1/(1-4*ETA)-1
    REP2V = 1/(1-4*ETA)**2-1
    ATT2V = aRT*V**2*(1/SUMD**2-1/SUMC**2)/(b*(C-D))
    F = REP+ATT
    F_V = (-REPV/V+ATTV)
    IF (NDER == 1) THEN
        F_2V = REP2V-ATT2V
    ELSE
        F_N = REP + ATT - V*F_V
    END IF
    return
    end subroutine vdWg_Derivs