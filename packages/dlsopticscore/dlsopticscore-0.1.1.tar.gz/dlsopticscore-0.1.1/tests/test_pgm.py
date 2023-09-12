from pytest import approx
from optics.components import PGM


def test_pgm_offset():
    p = PGM()
    assert p.compute_shifted_energy(0.1, 0.1) == approx(256.6981)

