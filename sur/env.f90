
module sur

    integer, parameter :: PR=1, SRK=2, RKPR=3
    save

    contains



    subroutine envelope(nmodel, n, z, tc, pc, ohm, ac, b, k_or_m, delta1, Kij_or_K0, &
                        Tstar, Lij, n_points, Tv, Pv, Dv, n_cri, Tcri, Pcri, Dcri)

        implicit none

        ! eos id and  number of compounds in the system
        integer, intent(in) :: nmodel, n

        ! composition of the system
        real*8, dimension(n), intent(in) :: z

        ! pure compound constants
        real*8, dimension(n), intent(in) :: tc
        real*8, dimension(n), intent(in) :: pc
        real*8, dimension(n), intent(in) :: ohm

        ! eos parameters
        real*8, dimension(n), intent(in) :: ac
        real*8, dimension(n), intent(in) :: b
        real*8, dimension(n), intent(in) :: delta1  !only required for RKPR
        real*8, dimension(n), intent(in) :: k_or_m

        ! interaction parameters matrices
        real*8, dimension(n,n), intent(in) :: Kij_or_K0
        real*8, dimension(n,n), intent(in) :: Tstar
        real*8, dimension(n,n), intent(in) :: Lij

        ! T, P and Density of the calculated envelope
        real*8, dimension(5000), intent(out) :: Tv
        real*8, dimension(5000), intent(out) :: Pv
        real*8, dimension(5000), intent(out) :: Dv

        ! number of valid elements in To, Po and Do arrays
        integer, intent(out) :: n_points

        ! T, P and Density of critical points
        real*8, dimension(4), intent(out) :: Tcri
        real*8, dimension(4), intent(out) :: Pcri
        real*8, dimension(4), intent(out) :: Dcri

        ! number of valid elements in Tcri, Pcri and Dcri arrays
        integer, intent(out) :: n_cri

        ! auxiliar/internal variables
        integer :: i, j

        !-----------------------------------------------------------
        ! Algorithm starts here :)
        ! this is just a mockup code


        real*8 :: t
        real*8 :: p
        real*8 :: d

        open(unit=1, file='ISO.DAT')

        do i=1, 2260, 1
           READ(1,*) t, p, d
             Tv(i) = t
             Pv(i) = p
             Dv(i) = d
        END DO

        n_points = i
        n_cri = 1
        Tcri(1) = 260.22
        Pcri(1) = 81.697
        Dcri(1) = 10.543
        close(unit=1)

        ! Algorithm ends here
        !-----------------------------------------------------------

    end subroutine envelope


    subroutine flash(nmodel, n, z, tc, pc, ohm, ac, b, k_or_m, delta1, &
                     Kij_or_K0, Tstar, Lij, t, p, x, y, rho_x, rho_y, beta)

        implicit none

        ! eos id and  number of compounds in the system
        integer, intent(in) :: nmodel, n

        ! composition of the system
        real*8, dimension(n), intent(in) :: z

        ! pure compound constants
        real*8, dimension(n), intent(in) :: tc
        real*8, dimension(n), intent(in) :: pc
        real*8, dimension(n), intent(in) :: ohm

        ! eos parameters
        real*8, dimension(n), intent(in) :: ac
        real*8, dimension(n), intent(in) :: b
        real*8, dimension(n), intent(in) :: delta1  !only required for RKPR
        real*8, dimension(n), intent(in) :: k_or_m

        ! interaction parameters matrices
        real*8, dimension(n,n), intent(in) :: Kij_or_K0
        real*8, dimension(n,n), intent(in) :: Tstar
        real*8, dimension(n,n), intent(in) :: Lij

        ! Temperature and Pressure for the flash
        real*8, intent(in) :: t            ! density of liquid
        real*8, intent(in) :: p            ! density of vapour

        !
        real*8, dimension(n), intent(out) :: x  ! composition of liquid
        real*8, dimension(n), intent(out) :: y  ! composition of vapour
        real*8, intent(out) :: rho_x            ! density of liquid
        real*8, intent(out) :: rho_y            ! density of vapour
        real*8, intent(out) :: beta             ! total fraction of vapour


        !-----------------------------------------------------------
        ! Put the magic since here

        continue


        ! until here
        !-----------------------------------------------------------


    end subroutine flash

end module sur