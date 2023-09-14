import pytest

from math import pi
from twiss.util import mod

@pytest.mark.parametrize(
    ('x', 'y', 'z', 'out'),
    [
        (5, 2, -1, -1),
        (5, 2, 1, 1),
        (1.5*pi, 2.0*pi, -pi, -1.5707963267948966),
        (1.5*pi, 2.0*pi, +pi, 4.71238898038469)
    ]
)
def test_mod(x, y, z, out):
    assert(mod(x, y, z) == out)