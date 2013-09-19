
module envelope_sur

    integer, parameter :: PR=1, SRK=2, RKPR=3
    save

    contains

    subroutine envelope(nmodel, n, z, tc, pc, ohm, ac, b, del, k_o_m, K0, Tstar, Lij, &
                    n_points, Tv, Pv, Dv, n_cri, Tcri, Pcri, Dcri)

        implicit none

        ! number of compounds in the system
        integer, intent(in) :: nmodel, n

        ! pure compound constants
        real*8, dimension(n), intent(in) :: z
        real*8, dimension(n), intent(in) :: tc
        real*8, dimension(n), intent(in) :: pc
        real*8, dimension(n), intent(in) :: ohm

        ! rkpr parameters
        real*8, dimension(n), intent(in) :: ac
        real*8, dimension(n), intent(in) :: b
        real*8, dimension(n), intent(in) :: del
        real*8, dimension(n), intent(in) :: k_o_m

        ! interaction parameters matrices
        real*8, dimension(n,n), intent(in) :: K0
        real*8, dimension(n,n), intent(in) :: Tstar
        real*8, dimension(n,n), intent(in) :: Lij

        ! T, P and Density of the calculated envelope
        real*8, dimension(5000), intent(out) :: Tv
        real*8, dimension(5000), intent(out) :: Pv
        real*8, dimension(5000), intent(out) :: Dv

        ! number of valid elements in To, Po and Do arrays
        integer, intent(out) :: n_points

        ! T, P and Density of critical points
        real*8, dimension(10), intent(out) :: Tcri
        real*8, dimension(10), intent(out) :: Pcri
        real*8, dimension(10), intent(out) :: Dcri

        ! number of valid elements in Tcri, Pcri and Dcri arrays
        integer, intent(out) :: n_cri

        ! auxiliar/internal variables
        integer :: i, j

        !-----------------------------------------------------------
        ! Algorithm starts here :)
        ! this is just dummy code

        if (nmodel == RKPR) then
            print *, 'hello RKPR!'
        else if (nmodel == PR) then
            print *, 'hi PR!'
        else if (nmodel == SRK) then
            print *, 'how u doing SRK!'
        else
            print *, 'unknow MODEL'
            stop 9
        end if


        do i=1,n
            Tv(i) = 2.0 * tc(i)
            Pv(i) = 2.0 * pc(i)
            Dv(i) = 2.0 * ohm(i)
        end do

        n_points = n

        do i=1,3
            Tcri(i) = Tv(i)
            Pcri(i) = Pv(i)
            Dcri(i) = Dv(i)
        end do

        n_cri = 3


        ! Algorithm ends here
        !-----------------------------------------------------------

    end subroutine envelope
end module envelope_sur