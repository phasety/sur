from sur.cubicparam import RKPR, PR
from numpy.testing import assert_allclose
from numpy import array


def test_rkpr_from_isobutane_constants():
    constants = array([407.8,  36.4,  0.183521,  0.302512])
    c, p = RKPR.from_constants(*constants)
    assert_allclose(c, constants, rtol=1e-4)
    assert_allclose(p, array([13.8062, 0.077960, 1.510750, 2.1156]), rtol=1e-4)


def test_rkpr_from_npentante_constants():
    constants = array([469.7,  33.7,  0.251506, 0.365584])
    c, p = RKPR.from_constants(*constants)
    assert_allclose(c, constants, rtol=1e-4)
    assert_allclose(p, array([20.2654, 0.093318, 1.998363, 2.27780]), rtol=1e-4)


def test_rkpr_from_co2_constants():
    constants = array([304.21, 73.83, 0.223621, 0.109792])
    c, p = RKPR.from_constants(*constants)
    assert_allclose(c, constants, rtol=1e-4)
    assert_allclose(p, array([3.8302, 0.028171, 1.738849, 2.23068]), rtol=1e-4)


def test_pr_from_isobutane_constants():
    constants = array([407.8,  36.4,  0.183521])
    c, p = PR.from_constants(*constants)
    assert_allclose(c, array([407.8, 36.4, 0.18352, 0.286343]), rtol=1e-4)
    assert_allclose(p, array([14.4412, 0.072467, 0.648585]), rtol=1e-4)


def test_pr_from_npentante_constants():
    constants = array([469.7,  33.7,  0.251506])
    c, p = PR.from_constants(*constants)
    assert_allclose(c, array([469.7, 33.7, 0.25151, 0.356230]), rtol=1e-4)
    assert_allclose(p, array([20.6929, 0.090154, 0.745454]), rtol=1e-4)


def test_pr_from_co2_constants():
    constants = array([304.21, 73.83, 0.22362])
    c, p = PR.from_constants(*constants)
    assert_allclose(c, array([304.21, 73.83, 0.22362, 0.105313]), rtol=1e-4)
    assert_allclose(p, array([3.9621, 0.026652, 0.706023]), rtol=1e-4)



