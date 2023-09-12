from optics.beam import Polarization
from pytest import approx

def test_phi_0():
    p = Polarization()
    p.s1 = 1
    p.s2 = 0
    p.s3 = 0
    assert p.phi == 0

def test_phi_45():
    p = Polarization()
    p.s1 = 0
    p.s2 = 1
    p.s3 = 0
    assert p.phi == approx(45)

def test_phi_22p5():
    p = Polarization()
    p.s1 = 0.5
    p.s2 = 0.5
    p.s3 = 0
    assert p.phi == 22.5

def test_s1_s2_45():
    p = Polarization()
    p.phi = 45
    assert p.s1 == approx(0)
    assert p.s2 == 1

def test_s1_s2_0():
    p = Polarization()
    p.phi = 0
    assert p.s1 == 1
    assert p.s2 == 0

def test_chi_pc():
    p = Polarization()
    p.s1 = 0
    p.s2 = 0
    p.s3 = 1
    assert p.chi == approx(45)

def test_chi_nc():
    p = Polarization()
    p.s1 = 0
    p.s2 = 0
    p.s3 = -1
    assert p.chi == approx(-45)

def test_s3_pc():
    p = Polarization()
    p.chi = 45
    assert p.s3 == 1

def test_s3_nc():
    p = Polarization()
    p.chi = -45
    assert p.s3 == -1

def test_polarization_fraction():
    p = Polarization()
    p.s1 = 1
    p.s2 = 0
    p.s3 = 0
    assert p.polarization_fraction == 1

def test_polarization_fraction_less():
    p = Polarization()
    p.s1 = 0.9
    p.s2 = 0
    p.s3 = 0.1
    assert p.polarization_fraction < 1
