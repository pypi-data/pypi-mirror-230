"""
Invariant
---------

Invariant utils

"""

import torch
from torch import Tensor

from twiss.normal import lb_normal
from twiss.normal import cs_normal

def invariant(normal:Tensor,
              orbit:Tensor) -> Tensor:
    """
    Compute linear invariants for a given normalization matrix and orbit

    Parameters
    ----------
    normal: Tensor, even-dimension, symplectic
        normalization matrix
    orbit: Tensor
        orbit

    Returns
    -------
    Tensor
        [jx, jy] for each turn
    
    Note
    ----
    Orbit is assumed to have the form [..., [qx_i, px_i, qy_i, py_i], ...]

    Examples
    --------
    >>> from math import pi
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.31], dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> x = torch.tensor([[1, 0, 1, 0]], dtype=torch.float64)
    >>> torch.allclose(invariant(n, x), invariant(n, torch.func.vmap(lambda x: m @ x)(x)))
    True

    """
    qx, px, qy, py = torch.inner(normal.inverse(), orbit)

    jx = 1/2*(qx**2 + px**2)
    jy = 1/2*(qy**2 + py**2)

    return torch.stack([jx, jy])


def lb_invariant(twiss:Tensor,
                 orbit:Tensor) -> Tensor:
    """
    Compute linear invariants for a given LB twiss and orbit

    Parameters
    ----------
    twiss: Tensor
        LB twiss
        a1x, b1x, a2x, b2x, a1y, b1y, a2y, b2y, u, v1, v2
    orbit: Tensor
        orbit

    Returns
    -------
    Tensor
        [jx, jy] for each turn

    Note
    ----
    Orbit is assumed to have the form [..., [qx_i, px_i, qy_i, py_i], ...]

    Examples
    --------
    >>> from math import pi
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> from twiss.convert import wolski_to_lb
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.31], dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> lb = wolski_to_lb(w)
    >>> x = torch.tensor([[1, 0, 1, 0]], dtype=torch.float64)
    >>> torch.allclose(lb_invariant(lb, x), lb_invariant(lb, torch.func.vmap(lambda x: m @ x)(x)))
    True

    """
    normal = lb_normal(twiss)
    return invariant(normal, orbit)


def cs_invariant(twiss:Tensor,
                 orbit:Tensor) -> Tensor:
    """
    Compute linear invariants for a given CS twiss and orbit

    Parameters
    ----------
    twiss: Tensor
        CS twiss
        ax, bx, ay, by
    orbit: Tensor
        orbit

    Returns
    -------
    Tensor
        [jx, jy] for each turn

    Note
    ----
    Orbit is assumed to have the form [..., [qx_i, px_i, qy_i, py_i], ...]

    Examples
    --------
    >>> from math import pi
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> from twiss.convert import wolski_to_cs
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.31], dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> cs = wolski_to_cs(w)
    >>> x = torch.tensor([[1, 0, 1, 0]], dtype=torch.float64)
    >>> torch.allclose(cs_invariant(cs, x), cs_invariant(cs, torch.func.vmap(lambda x: m @ x)(x)))
    True

    """
    normal = cs_normal(twiss)
    return invariant(normal, orbit)
