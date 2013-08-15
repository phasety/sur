module envelope

contains

subroutine rkpr(comp, tc, pc, ohm, ac, b, del, k, Kij0, Kij1, Lij, n, To, Po, Do)
    implicit none

    real, dimension(n), intent(in) :: comp
    real, dimension(n), intent(in) :: tc
    real, dimension(n), intent(in) :: pc
    real, dimension(n), intent(in) :: ohm
    real, dimension(n), intent(in) :: ac
    real, dimension(n), intent(in) :: b
    real, dimension(n), intent(in) :: del
    real, dimension(n), intent(in) :: k
    real, dimension(n,n), intent(in) :: Kij0
    real, dimension(n,n), intent(in) :: Kij1
    real, dimension(n,n), intent(in) :: Lij

    integer, intent(in) :: n

    real, dimension(n), intent(out) :: To
    real, dimension(n), intent(out) :: Po
    real, dimension(n), intent(out) :: Do


    integer :: i

    do i=1,n
        To(i) = 2.0 * tc(i)
        Po(i) = 2.0 * pc(i)
        Do(i) = 2.0 * ohm(i)
    end do

end subroutine rkpr

end module envelope