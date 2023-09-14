"""
Wolski
-----

Compute coupled Wolski twiss matrices and normalization matrix in standard gauge
Input matrix is assumed stable and can have arbitrary even dimension
Main function can be mapped over a batch of input matrices and is differentiable

"""

from math import pi

import torch
from torch import Tensor

from twiss.util import mod
from twiss.matrix import rotation

def twiss(m:Tensor, *,
          epsilon:float=1.0E-12) -> tuple[Tensor, Tensor, Tensor]:
    """
    Compute coupled Wolski twiss parameters for a given one-turn input matrix

    Returns fractional tunes, normalization matrix (standard gauge) and Wolski twiss matrices

    Input matrix can have arbitrary even dimension
    Input matrix stability is not checked

    Symplectic block is [[0, 1], [-1, 0]]
    Rotation block is [[cos(alpha), sin(alpha)], [-sin(alpha), cos(alpha)]]
    Complex block is 1/sqrt(2)*[[1, 1j], [1, -1j]]

    Parameters
    ----------
    m: Tensor, even-dimension, symplectic
        input one-turn matrix
    epsilon: float, default=1.0E-12
        tolerance epsilon (ordering of planes)

    Returns
    -------
    tuple[Tensor, Tensor, Tensor]
        fractional tunes [..., T_I, ...]
        normalization matrix (standard gauge) N
        twiss matrices W = [..., W_I, ...]

    Note
    ----
    M = N R N^-1 = ... + W_I S sin(2*pi*T_I) - (W_I S)**2 cos(2*pi*T_I) + ...

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import  rotation
    >>> m = rotation(2*pi*torch.tensor(0.88, dtype=torch.float64))
    >>> t, n, w = twiss(m)
    >>> t
    tensor([0.8800], dtype=torch.float64)
    >>> n
    tensor([[1.0000, 0.0000],
            [0.0000, 1.0000]], dtype=torch.float64)
    >>> w
    tensor([[[1.0000, 0.0000],
             [0.0000, 1.0000]]], dtype=torch.float64)

    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> m = rotation(*(2*pi*torch.linspace(0.1, 0.9, 9, dtype=torch.float64)))
    >>> t, n, w = twiss(m)
    >>> t
    tensor([0.1000, 0.2000, 0.3000, 0.4000, 0.5000, 0.6000, 0.7000, 0.8000, 0.9000],
           dtype=torch.float64)

    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> m = torch.func.vmap(rotation)(2*pi*torch.linspace(0.1, 0.9, 9, dtype=torch.float64))
    >>> t, n, w = torch.func.vmap(twiss)(m)
    >>> t
    tensor([[0.1000],
            [0.2000],
            [0.3000],
            [0.4000],
            [0.5000],
            [0.6000],
            [0.7000],
            [0.8000],
            [0.9000]], dtype=torch.float64)

    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import  rotation
    >>> def fn(k):
    ...    m = rotation(2*pi*torch.tensor(0.88, dtype=torch.float64))
    ...    i = torch.ones_like(k)
    ...    o = torch.zeros_like(k)
    ...    m = m @ torch.stack([i, k, o, i]).reshape(m.shape)
    ...    t, *_ = twiss(m)
    ...    return t
    >>> k = torch.tensor(0.0, dtype=torch.float64)
    >>> fn(k)
    tensor([0.8800], dtype=torch.float64)
    >>> torch.func.jacfwd(fn)(k)
    tensor([0.0796], dtype=torch.float64)

    """
    with torch.no_grad():

        dtype = m.dtype
        device = m.device

        rdtype = torch.tensor(1, dtype=dtype).abs().dtype
        cdtype = (1j*torch.tensor(1, dtype=dtype)).dtype

        d = len(m) // 2

        b_p = torch.tensor([[1, 0], [0, 1]], dtype=rdtype, device=device)
        b_s = torch.tensor([[0, 1], [-1, 0]], dtype=rdtype, device=device)
        b_c = 0.5**0.5*torch.tensor([[1, +1j], [1, -1j]], dtype=cdtype, device=device)

        m_p = torch.stack([torch.block_diag(*[b_p*(i == j) for i in range(d)]) for j in range(d)])
        m_s = torch.block_diag(*[b_s for _ in range(d)])
        m_c = torch.block_diag(*[b_c for _ in range(d)])

    l, v = torch.linalg.eig(m)
    l, v = l.reshape(d, -1), v.T.reshape(d, -1, 2*d)

    u = torch.zeros_like(v)
    for i, (v1, v2) in enumerate(v):
        u[i] = v[i]/(-1j*(v1 @ m_s.to(cdtype) @ v2)).abs().sqrt()

    k = torch.zeros_like(l)
    v = torch.zeros_like(u)
    for i in range(d):
        o = torch.clone(l[i].log()).imag.argsort()
        k[i], v[i] = l[i, o], u[i, o]

    t = 1.0 - k.log().abs().mean(-1)/(2.0*pi)

    n = torch.cat([*v]).H
    n = (n @ m_c).real
    w = n @ m_p @ n.T

    o = torch.stack([w[i].diag().argmax() for i in range(d)]).argsort()
    t, v = t[o], v[o]

    n = torch.cat([*v]).H
    n = (n @ m_c).real

    f = (torch.stack(torch.hsplit(n.T @ m_s @ n - m_s, d)).abs().sum((1, -1)) <= epsilon)
    g = f.logical_not()
    for i in range(d):
        t[i] = f[i]*t[i] + g[i]*(1.0 - t[i]).abs()
        v[i] = f[i]*v[i] + g[i]*v[i].conj()

    n = torch.cat([*v]).H
    n = (n @ m_c).real

    s = torch.arange(d, dtype=torch.int64, device=device)
    a = (n[2*s, 2*s + 1] + 1j*n[2*s, 2*s]).angle() - 0.5*pi
    n = n @ rotation(*a)
    w = n @ m_p @ n.T

    return t, n, w


def is_stable(m:Tensor, *,
              epsilon:float=1.0E-12) -> bool:
    """
    Check one-turn matrix stability

    Parameters
    ----------
    m: Tensor, even-dimension
        input one-turn matrix
    epsilon: float, default=1.0E-12
        tolerance epsilon

    Returns
    -------
    bool

    Note
    ----
    Input matrix is stable if eigenvalues are on the unit circle

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> m = rotation(2*pi*torch.tensor(0.1234, dtype=torch.float64))
    >>> is_stable(m)
    True
    >>> is_stable(m + 1.0E-3)
    False

    """
    return all((torch.linalg.eigvals(m).abs() - 1.0).abs() <= epsilon)


def propagate(w:Tensor,
              m:Tensor) -> Tensor:
    """
    Propagate Wolski twiss matrices throught a given transport matrix

    Parameters
    ----------
    w: Tensor, even-dimension
        Wolski twiss matrices
    m: Tensor, even-dimension, symplectic
        transport matrix

    Returns
    -------
    Tensor

    Note
    ----
    W_I = M W_I M.T

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import  rotation
    >>> m = rotation(2*pi*torch.tensor(0.88, dtype=torch.float64))
    >>> *_, w = twiss(m)
    >>> propagate(w, torch.tensor([[1.0, 0.1], [0.0, 1.0]], dtype=torch.float64))
    tensor([[[1.0100, 0.1000],
             [0.1000, 1.0000]]], dtype=torch.float64)

    """
    return m @ w @ m.T


def advance(n:Tensor,
            m:Tensor) -> tuple[Tensor, Tensor]:
    """
    Compute advance and final normalization matrix given input transport and normalization matrices

    Parameters
    ----------
    n: Tensor, even-dimension, symplectic
        normalization matrix
    m: Tensor, even-dimension, symplectic
        transport matrix

    Returns
    -------
    tuple[Tensor, Tensor]
        phase advance
        final normalization matrix

    Note
    ----
    Output phase advance is mod 2 pi

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import  rotation
    >>> m = rotation(2*pi*torch.tensor(0.88, dtype=torch.float64))
    >>> _, n, _ = twiss(m)
    >>> advance(n, torch.tensor([[1.0, 0.1], [0.0, 1.0]], dtype=torch.float64))
    (tensor([0.0997], dtype=torch.float64), tensor([[ 1.0050e+00, -1.3878e-17],
            [ 9.9504e-02,  9.9504e-01]], dtype=torch.float64))

    """
    d = len(n) // 2
    i = torch.arange(d, dtype=torch.int64, device=n.device)
    l = m @ n
    f = mod(torch.arctan2(l[2*i, 2*i + 1], l[2*i, 2*i]), 2.0*pi)
    return f, l @ rotation(*(-f))
