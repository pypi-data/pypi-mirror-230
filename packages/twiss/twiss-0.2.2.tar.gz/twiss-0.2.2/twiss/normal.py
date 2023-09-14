"""
Normal
------

Normalization matrix utils

"""

import torch
from torch import Tensor

from twiss.wolski import twiss

def normal_to_wolski(n:Tensor) -> Tensor:
    """
    Compute Wolski twiss matrices for a given normalization matrix

    Parameters
    ----------
    n: torch.Tensor, even-dimension, symplectic
        normalization matrix

    Returns
    -------
    Tensor

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import  rotation
    >>> m = rotation(2*pi*torch.tensor(0.88, dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> torch.allclose(normal_to_wolski(n), w)
    True

    """
    d = len(n) // 2
    p = torch.tensor([[1, 0], [0, 1]], dtype=n.dtype, device=n.device)
    p = torch.stack([torch.block_diag(*[p*(i == j) for i in range(d)]) for j in range(d)])
    return n @ p @ n.T


def wolski_to_normal(w:Tensor, *,
                     epsilon:float=1.0E-12) -> Tensor:
    """
    Compute normalization matrix for given Wolski twiss matrices

    Parameters
    ----------
    w: Tensor
        Wolski twiss matrices
    epsilon: float, optional, default=1.0E-12
        tolerance epsilon

    Returns
    -------
    Tensor

    Note
    ----
    Normalization matrix is computed using fake one-turn matrix with fixed tunes

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import  rotation
    >>> m = rotation(2*pi*torch.tensor(0.88, dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> torch.allclose(wolski_to_normal(w), n)
    True

    """
    d, *_ = w.shape

    b = torch.tensor([[0, 1], [-1, 0]], dtype=w.dtype, device=w.device)
    b = torch.block_diag(*[b for _ in range(d)])

    t = 2.0**0.5*torch.linspace(1, d, d, dtype=w.dtype, device=w.device)

    m = torch.zeros_like(b)
    for i in range(d):
        s = w[i] @ b
        m += s*t[i].sin() - (s @ s) * t[i].cos()

    _, n, _ = twiss(m, epsilon=epsilon)

    return n


def parametric(pars:Tensor) -> Tensor:
    """
    Generate 'parametric' 4x4 normalization matrix for given free elements

    Parameters
    ----------
    pars: Tensor
        free matrix elements
        n11, n33, n21, n43, n13, n31, n14, n41

    Returns
    -------
    Tensor
        normalization matrix N
        M = N R N^-1

    Note
    ----
    Elements denoted with x are computed for given free elements using symplectic condition
    For n11 > 0 & n33 > 0, all matrix elements are not singular in uncoupled limit

        n11   0 n13 n14
        n21   x   x   x
        n31   x n33   0
        n41   x n43   x

    Examples
    --------
    >>> import torch
    >>> from twiss.matrix import is_symplectic
    >>> pars = torch.tensor([1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    >>> is_symplectic(parametric(pars))
    True

    """
    n11, n33, n21, n43, n13, n31, n14, n41 = pars

    n12 = torch.zeros_like(n11)
    n22 = n33*(n11 + n14*(n33*n41 - n31*n43))/(n11*(n11*n33 - n13*n31))
    n23 = (n13*n21 + n33*n41 - n31*n43)/n11
    n24 = (n14*n21*n33 -n31 + n14*n31/n11*(n31*n43 - n13*n21 - n33*n41))/(n11*n33 - n13*n31)
    n32 = n14*n33/n11
    n34 = torch.zeros_like(n11)
    n42 = (n13*(-1.0 - (n14*n33*n41)/n11) + n14*n33*n43)/(n11*n33 - n13*n31)
    n44 = (n11 + n14*(n33*n41 - n31*n43))/(n11*n33 - n13*n31)

    n = torch.stack(
        [
            torch.stack([n11, n12, n13, n14]),
            torch.stack([n21, n22, n23, n24]),
            torch.stack([n31, n32, n33, n34]),
            torch.stack([n41, n42, n43, n44])
        ])

    return n


def lb_normal(pars:Tensor) -> Tensor:
    """
    Generate Lebedev-Bogacz normalization matrix

    Parameters
    ----------
    pars: Tensor
        Lebedev-Bogacz twiss parameters
        a1x, b1x, a2x, b2x, a1y, b1y, a2y, b2y, u, v1, v2

    Returns
    -------
    Tensor
        normalization matrix N, M = N R N^-1

    Note
    ----
    [a1x, b1x, a2x, b2x, a1y, b1y, a2y, b2y, u, v1, v2] are LB twiss parameters
    [a1x, b1x, a2y, b2y] are 'in-plane' twiss parameters

    Examples
    --------
    >>> import torch
    >>> from twiss.matrix import is_symplectic
    >>> pars = torch.tensor([0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0], dtype=torch.float64)
    >>> is_symplectic(lb_normal(pars))
    True

    """
    a1x, b1x, a2x, b2x, a1y, b1y, a2y, b2y, u, v1, v2 = pars

    o = torch.tensor(0.0, dtype=pars.dtype, device=pars.device)

    cv1, sv1 = v1.cos(), v1.sin()
    cv2, sv2 = v2.cos(), v2.sin()

    n1 = torch.stack([
        b1x.sqrt(),
        o,
        b2x.sqrt()*cv2,
        -b2x.sqrt()*sv2])

    n2 = torch.stack([
        -a1x/b1x.sqrt(),
        (1 - u)/b1x.sqrt(),
        (-a2x*cv2 + u*sv2)/b2x.sqrt(),
        (a2x*sv2 + u*cv2)/b2x.sqrt()])

    n3 = torch.stack([
        b1y.sqrt()*cv1,
        -b1y.sqrt()*sv1,
        b2y.sqrt(),
        o])

    n4 = torch.stack([
        (-a1y*cv1 + u*sv1)/b1y.sqrt(),
        (a1y*sv1 + u*cv1)/b1y.sqrt(),
        -a2y/b2y.sqrt(),
        (1 - u)/b2y.sqrt()])

    return torch.stack([n1, n2, n3, n4]).nan_to_num(posinf=0.0, neginf=0.0)


def cs_normal(pars:Tensor) -> Tensor:
    """
    Generate Courant-Snyder normalization matrix

    Parameters
    ----------
    pars: Tensor
        Courant-Snyder twiss parameters
        ax, bx, ay, by

    Returns
    -------
    Tensor
        normalization matrix N, M = N R N^-1

    Note
    -----
    [ax, bx, ay, by] are CS twiss parameters

    Examples
    --------
    >>> import torch
    >>> from twiss.matrix import is_symplectic
    >>> pars = torch.tensor([0, 1, 0, 1], dtype=torch.float64)
    >>> is_symplectic(cs_normal(pars))
    True

    """
    ax, bx, ay, by = pars

    o = torch.tensor(0.0, dtype=pars.dtype, device=pars.device)

    return torch.stack([
        torch.stack([bx.sqrt(), o, o, o]),
        torch.stack([-ax/bx.sqrt(), 1/bx.sqrt(), o, o]),
        torch.stack([o, o, by.sqrt(), o]),
        torch.stack([o, o, -ay/by.sqrt(), 1/by.sqrt()]),
    ]).nan_to_num(posinf=0.0, neginf=0.0)
