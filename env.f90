module test

contains

subroutine foo (a)
    implicit none

    integer, intent(in) :: a
    print*, "Hello from Fortran!"
    print*, "a=",a
end subroutine foo

function bar (a, len_a)
    implicit none

    real, dimension(len_a), intent(in) :: a
    integer, intent(in) :: len_a

    real, dimension(len_a) :: bar


    integer :: i
    real, dimension(len_a) :: b

    do i=1,len_a
        b(i) = 2.0*a(i)
    end do

    bar = b
end function bar

subroutine sub (a, len_a, a_out)
    implicit none

    real, dimension(len_a), intent(in) :: a
    integer, intent(in) :: len_a
    real, dimension(len_a), intent(out) :: a_out

    integer :: i

    do i=1,len_a
        a_out(i) = 2.0*a(i)
    end do

end subroutine sub

end module test