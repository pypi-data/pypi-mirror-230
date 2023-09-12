from optics.components import Undulator
from math import pi, sqrt
from pytest import approx

def test_top_row_phase():
    u = Undulator()
    u.period = 64
    u.top_row_position = u.period
    assert u.top_row_phase == 2*pi
    u.top_row_position = u.period/2
    assert u.top_row_phase == pi

def test_bx():
    u = Undulator()
    u.period = 64
    u.bx0 = sqrt(2)/2
    u.by0 = sqrt(2)/2
    u.top_row_position = 4
    print(u.bx0)
    print(u.by0)
    print(u.bx(0))
