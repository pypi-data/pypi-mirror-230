"""
Convert
-------

Convert between different twiss representations

"""

import torch
from torch import Tensor

from twiss.matrix import projection
from twiss.normal import lb_normal
from twiss.normal import cs_normal

def wolski_to_lb(pars:Tensor) -> Tensor:
    """
    Convert Wolski twiss matrices to Lebedev-Bogacz twiss parameters

    Parameters
    ----------
    pars: Tensor
        Wolski twiss matrices

    Returns
    -------
    Tensor

    Note
    ----
    [a1x, b1x, a2x, b2x, a1y, b1y, a2y, b2y, u, v1, v2] are LB twiss parameters
    [a1x, b1x, a2y, b2y] are 'in-plane' twiss parameters

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.19], dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> torch.allclose(w, lb_to_wolski(wolski_to_lb(w)))
    True

    """
    a1x = -pars[0, 0, 1]
    b1x = +pars[0, 0, 0]
    a2x = -pars[1, 0, 1]
    b2x = +pars[1, 0, 0]

    a1y = -pars[0, 2, 3]
    b1y = +pars[0, 2, 2]
    a2y = -pars[1, 2, 3]
    b2y = +pars[1, 2, 2]

    u = 1/2*(1 + a1x**2 - a1y**2 - b1x*pars[0, 1, 1] + b1y*pars[0, 3, 3])

    cv1 = (1/torch.sqrt(b1x*b1y)*pars[0, 0, 2]).nan_to_num(nan=-1.0)
    sv1 = (1/u*(a1y*cv1 + 1/torch.sqrt(b1x)*(torch.sqrt(b1y)*pars[0, 0, 3]))).nan_to_num(nan=0.0)

    cv2 = (1/torch.sqrt(b2x*b2y)*pars[1, 0, 2]).nan_to_num(nan=+1.0)
    sv2 = (1/u*(a2x*cv2 + 1/torch.sqrt(b2y)*(torch.sqrt(b2x)*pars[1, 1, 2]))).nan_to_num(nan=0.0)

    v1 = torch.arctan2(sv1, cv1)
    v2 = torch.arctan2(sv2, cv2)

    return torch.stack([a1x, b1x, a2x, b2x, a1y, b1y, a2y, b2y, u, v1, v2])


def lb_to_wolski(pars:Tensor) -> Tensor:
    """
    Convert Lebedev-Bogacz twiss parameters to Wolski twiss matrices.

    Parameters
    ----------
    pars: Tensor
        Lebedev-Bogacz twiss parameters
        a1x, b1x, a2x, b2x, a1y, b1y, a2y, b2y, u, v1, v2

    Returns
    -------
    Tensor

    Note
    ----
    [a1x, b1x, a2x, b2x, a1y, b1y, a2y, b2y, u, v1, v2] are LB twiss parameters
    [a1x, b1x, a2y, b2y] are 'in-plane' twiss parameters

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.19], dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> torch.allclose(w, lb_to_wolski(wolski_to_lb(w)))
    True

    """
    n = lb_normal(pars)

    p1 = projection(2, 1, dtype=n.dtype, device=n.device)
    p2 = projection(2, 2, dtype=n.dtype, device=n.device)

    w1 = n @ p1 @ n.T
    w2 = n @ p2 @ n.T

    return torch.stack([w1, w2])


def wolski_to_cs(pars:Tensor) -> Tensor:
    """
    Convert Wolski twiss matrices to Courant-Snyder twiss parameters

    Parameters
    ----------
    pars: Tensor
        Wolski twiss matrices

    Returns
    -------
    Tensor

    Note
    -----
    [ax, bx, ay, by] are CS twiss parameters

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.19], dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> torch.allclose(w, cs_to_wolski(wolski_to_cs(w)))
    True

    """
    ax = -pars[0, 0, 1]
    bx = +pars[0, 0, 0]

    ay = -pars[1, 2, 3]
    by = +pars[1, 2, 2]

    return torch.stack([ax, bx, ay, by])


def cs_to_wolski(pars:Tensor) -> Tensor:
    """
    Convert Courant-Snyder twiss parameters to Wolski twiss matrices

    Parameters
    ----------
    pars: Tensor
        Courant-Snyder twiss parameters
        ax, bx, ay, by
    epsilon: float, optional, default=1.0E-12
        tolerance epsilon

    Returns
    -------
    Tensor

    Note
    -----
    [ax, bx, ay, by] are CS twiss parameters

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.19], dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> torch.allclose(w, cs_to_wolski(wolski_to_cs(w)))
    True

    """
    n = cs_normal(pars)

    p1 = projection(2, 1, dtype=n.dtype, device=n.device)
    p2 = projection(2, 2, dtype=n.dtype, device=n.device)

    w1 = n @ p1 @ n.T
    w2 = n @ p2 @ n.T

    return torch.stack([w1, w2])
