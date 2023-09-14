"""
Math
----

Math utils

"""

from typing import Any

def mod(x:Any, y:Any, z:Any=0) -> Any:
    """
    Return the remainder on division of `x` by `y` with offset `z`

    Parameters
    ----------
    x: Any
        numerator
    y: Any
        denomenator
    z: Any, default=0
        offset

    Returns
    -------
    Any

    Note
    ----
    ``int`` is returned only if all input arguments have ``int`` type

    Examples
    --------
    >>> mod(5, 2, -1)
    -1
    >>> mod(5, 2, +1)
    1

    >>> from math import pi
    >>> mod(1.5*pi, 2.0*pi, -pi)
    -1.5707963267948966
    >>> mod(1.5*pi, 2.0*pi, +pi)
    4.71238898038469

    """
    return x - ((x - z) - (x - z) % y)
