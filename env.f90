module envelope

contains

subroutine rkpr(comp, tc, pc, ohm, ac, b, del, k, K0, Tstar, Lij, n, Tenv, Penv, Denv, n_out, Tcri, Pcri, Dcri, n_cri)
    implicit none

    ! pure compound constants
    real, dimension(n), intent(in) :: comp
    real, dimension(n), intent(in) :: tc
    real, dimension(n), intent(in) :: pc
    real, dimension(n), intent(in) :: ohm

    ! rkpr parameters
    real, dimension(n), intent(in) :: ac
    real, dimension(n), intent(in) :: b
    real, dimension(n), intent(in) :: del
    real, dimension(n), intent(in) :: k

    ! interaction parameters matrices
    real, dimension(n,n), intent(in) :: K0
    real, dimension(n,n), intent(in) :: Tstar
    real, dimension(n,n), intent(in) :: Lij

    ! number of compounds in the system
    integer, intent(in) :: n

    ! T, P and Density of the calculated envelope
    real, dimension(5000), intent(out) :: Tenv
    real, dimension(5000), intent(out) :: Penv
    real, dimension(5000), intent(out) :: Denv

    ! number of valid elements in To, Po and Do arrays
    integer, intent(out) :: n_out

    ! T, P and Density of critical points
    real, dimension(10), intent(out) :: Tcri
    real, dimension(10), intent(out) :: Pcri
    real, dimension(10), intent(out) :: Dcri

    ! number of valid elements in Tcri, Pcri and Dcri arrays
    integer, intent(out) :: n_cri

    ! auxiliar/internal variables
    integer :: i, j

    !-----------------------------------------------------------
    ! Algorithm starts here :)

    do i=1,n
        Tenv(i) = 2.0 * tc(i)
        Penv(i) = 2.0 * pc(i)
        Denv(i) = 2.0 * ohm(i)
    end do

    n_out = n

    do i=1,3
        Tcri(i) = Tenv(i)
        Pcri(i) = Penv(i)
        Dcri(i) = Denv(i)
    end do

    n_cri = 3


    ! Algorithm ends here
    !-----------------------------------------------------------

end subroutine rkpr
end module envelope