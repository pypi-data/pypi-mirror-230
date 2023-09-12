from pytest import approx
from optics.components.grating import Grating


def test_grating_instantiation():
    g = Grating()
    assert g.cff == approx(2)
    assert g.energy == approx(250)
    assert g.line_density == approx(600)


def test_change_energy():
    g = Grating()
    g.energy = 300
    assert g.energy == approx(300)


def test_set_angles():
    g = Grating()
    g.line_density = 400
    g.order = 1
    g.set_angles(89.01819850176891, -86.56179982864404)
    assert g.energy == approx(300)
    assert g.cff == approx(3.5)
