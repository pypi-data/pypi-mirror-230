"""
Transport
---------

Transport matrix utils

"""

from torch import Tensor

from twiss.matrix import rotation
from twiss.normal import wolski_to_normal
from twiss.normal import lb_normal
from twiss.normal import cs_normal

def transport(n1:Tensor,
              n2:Tensor,
              *mu12:Tensor) -> Tensor:
    """
    Generate transport matrix using normalization matrices and phase advances between locations

    Parameters
    ----------
    n1: Tensor, even-dimension, symplectic
        normalization matrix at the 1st location
    n2: Tensor, even-dimension, symplectic
        normalization matrix at the 2nd location
    *mu12: Tensor
        phase advances between locations

    Returns
    -------
    Tensor

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> from twiss.wolski import advance
    >>> t = torch.tensor([[1.0, 0.1], [0.0, 1.0]], dtype=torch.float64)
    >>> m = rotation(2*pi*torch.tensor(0.12, dtype=torch.float64))
    >>> _, n1, w1 = twiss(m @ t)
    >>> mu12, n2 = advance(n1, t)
    >>> transport(n1, n2, *mu12)
    tensor([[1.0000, 0.1000],
            [0.0000, 1.0000]], dtype=torch.float64)

    """
    return n2 @ rotation(*mu12) @ n1.inverse()


def wolski_transport(pars1:Tensor,
                     pars2:Tensor,
                     *mu12:Tensor) -> Tensor:
    """
    Generate transport matrix using Wolski matrices and phase advances between locations

    Parameters
    ----------
    pars1 : Tensor
        Wolski matrices at the 1st location
    pars2 : Tensor
        Wolski matrices at the 2nd location
    *mu12: Tensor
        phase advances between locations

    Returns
    -------
    Tensor

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> from twiss.wolski import propagate
    >>> from twiss.wolski import advance
    >>> t = torch.tensor([[1.0, 0.1], [0.0, 1.0]], dtype=torch.float64)
    >>> m = rotation(2*pi*torch.tensor(0.12, dtype=torch.float64))
    >>> _, n1, w1 = twiss(m @ t)
    >>> mu12, n2 = advance(n1, t)
    >>> w2 = propagate(w1, t)
    >>> torch.allclose(t, wolski_transport(w1, w2, *mu12))
    True

    """
    n1 = wolski_to_normal(pars1)
    n2 = wolski_to_normal(pars2)
    return transport(n1, n2, *mu12)


def lb_transport(pars1:Tensor,
                 pars2:Tensor,
                 *mu12:Tensor) -> Tensor:
    """
    Generate transport matrix using LB twiss data between given locations

    Parameters
    ----------
    pars1: Tensor
        twiss parameters at the 1st location
    pars2: Tensor
        twiss parameters at the 2nd location
    *mu12: Tensor
        phase advances between locations

    Returns
    -------
    Tensor

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> from twiss.wolski import advance
    >>> from twiss.normal import normal_to_wolski
    >>> from twiss.convert import wolski_to_lb
    >>> t = torch.tensor([[1.0, 0.1], [0.0, 1.0]], dtype=torch.float64)
    >>> t = torch.block_diag(t, t)
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.31], dtype=torch.float64))
    >>> _, n1, w1 = twiss(m @ t)
    >>> mu12, n2 = advance(n1, t)
    >>> w2 = normal_to_wolski(n2)
    >>> lb_transport(*torch.func.vmap(wolski_to_lb)(torch.stack([w1, w2])), *mu12)
    tensor([[1.0000e+00, 1.0000e-01, 0.0000e+00, 0.0000e+00],
            [1.3878e-17, 1.0000e+00, 0.0000e+00, 0.0000e+00],
            [0.0000e+00, 0.0000e+00, 1.0000e+00, 1.0000e-01],
            [0.0000e+00, 0.0000e+00, 1.3878e-16, 1.0000e+00]], dtype=torch.float64)

    """
    n1 = lb_normal(pars1)
    n2 = lb_normal(pars2)
    return transport(n1, n2, *mu12)


def cs_transport(pars1:Tensor,
                 pars2:Tensor,
                 *mu12:Tensor) -> Tensor:
    """
    Generate transport matrix using CS twiss data between given locations

    Parameters
    ----------
    pars1: Tensor
        twiss parameters at the 1st location
    pars2: Tensor
        twiss parameters at the 2nd location
    *mu12: Tensor
        phase advances between locations

    Returns
    -------
    Tensor

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> from twiss.wolski import twiss
    >>> from twiss.wolski import advance
    >>> from twiss.normal import normal_to_wolski
    >>> from twiss.convert import wolski_to_cs
    >>> t = torch.tensor([[1.0, 0.1], [0.0, 1.0]], dtype=torch.float64)
    >>> t = torch.block_diag(t, t)
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.31], dtype=torch.float64))
    >>> _, n1, w1 = twiss(m @ t)
    >>> mu12, n2 = advance(n1, t)
    >>> w2 = normal_to_wolski(n2)
    >>> cs_transport(*torch.func.vmap(wolski_to_cs)(torch.stack([w1, w2])), *mu12)
    tensor([[1.0000e+00, 1.0000e-01, 0.0000e+00, 0.0000e+00],
            [2.7756e-17, 1.0000e+00, 0.0000e+00, 0.0000e+00],
            [0.0000e+00, 0.0000e+00, 1.0000e+00, 1.0000e-01],
            [0.0000e+00, 0.0000e+00, 1.5959e-16, 1.0000e+00]], dtype=torch.float64)

    """
    n1 = cs_normal(pars1)
    n2 = cs_normal(pars2)
    return transport(n1, n2, *mu12)


def momenta(matrix:Tensor,
            qx1:Tensor,
            qx2:Tensor,
            qy1:Tensor,
            qy2:Tensor) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    """
    Compute momenta at positions 1 & 2 for given transport matrix and coordinates at 1 & 2

    Parameters
    ----------
    matrix: torch.Tensor, even-dimension, symplectic
        transport matrix between
    qx1, qx2, qy1, qy2: Tensor
        x & y coordinates at 1 & 2

    Returns
    -------
    tuple[Tensor, Tensor, Tensor, Tensor]
        px1, px2, py1, py2

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> from twiss.matrix import rotation
    >>> m = rotation(*2*pi*torch.tensor([0.12, 0.31], dtype=torch.float64))
    >>> x1 = torch.tensor([1.0, 0.0, 1.0, 0.0], dtype=torch.float64)
    >>> x2 = m @ x1
    >>> qx1, px1, qy1, py1 = x1
    >>> qx2, px2, qy2, py2 = x2
    >>> Px1, Px2, Py1, Py2 = momenta(m, qx1, qx2, qy1, qy2)
    >>> all(torch.allclose(x, y) for x, y in zip((px1, px2, py1, py2), (Px1, Px2, Py1, Py2)))
    True

    """
    (m11, m12, m13, m14), _, (m31, m32, m33, m34), _  = matrix

    px1  = qx1*(m11*m34 - m14*m31)/(m14*m32 - m12*m34)
    px1 += qx2*m34/(m12*m34 - m14*m32)
    px1 += qy1*(m13*m34 - m14*m33)/(m14*m32 - m12*m34)
    px1 += qy2*m14/(m14*m32 - m12*m34)

    py1  = qx1*(m11*m32 - m12*m31)/(m12*m34 - m14*m32)
    py1 += qx2*m32/(m14*m32 - m12*m34)
    py1 += qy1*(m12*m33 - m13*m32)/(m14*m32 - m12*m34)
    py1 += qy2*m12/(m12*m34 - m14*m32)

    (m11, m12, m13, m14), _, (m31, m32, m33, m34), _  = matrix.inverse()

    px2  = qx2*(m11*m34 - m14*m31)/(m14*m32 - m12*m34)
    px2 += qx1*m34/(m12*m34 - m14*m32)
    px2 += qy2*(m13*m34 - m14*m33)/(m14*m32 - m12*m34)
    px2 += qy1*m14/(m14*m32 - m12*m34)

    py2  = qx2*(m11*m32 - m12*m31)/(m12*m34 - m14*m32)
    py2 += qx1*m32/(m14*m32 - m12*m34)
    py2 += qy2*(m12*m33 - m13*m32)/(m14*m32 - m12*m34)
    py2 += qy1*m12/(m12*m34 - m14*m32)

    return  px1, px2, py1, py2
