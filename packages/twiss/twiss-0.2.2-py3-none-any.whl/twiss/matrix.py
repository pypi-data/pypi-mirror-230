"""
Matrix
------

Matrix utils

"""

import torch

from torch import Tensor

def symplectic_block(*,
                     dtype:torch.dtype=torch.float64,
                     device:torch.device=torch.device('cpu')) -> Tensor:
    """
    Generate 2D symplectic block [[0, 1], [-1, 0]] matrix

    Parameters
    ----------
    dtype: torch.dtype, default=torch.float64
        output type
    device: torch.device, torch.device=torch.device('cpu')
        output device

    Returns
    -------
    Tensor

    Examples
    --------
    >>> symplectic_block()
    tensor([[ 0.,  1.],
            [-1.,  0.]], dtype=torch.float64)

    """
    return torch.tensor([[0, 1], [-1, 0]], dtype=dtype, device=device)


def symplectic_identity(d:int, *,
                        dtype:torch.dtype=torch.float64,
                        device:torch.device=torch.device('cpu')) -> Tensor:
    """
    Generate symplectic identity matrix for a given (configuration space) dimension

    Parameters
    ----------
    d: int, positive
        configuration space dimension
    dtype: torch.dtype, default=torch.float64
        data type
    device: torch.device, torch.device=torch.device('cpu')
        data device

    Returns
    -------
    Tensor
    
    Note
    ----
    Symplectic block is [[0, 1], [-1, 0]], i.e. canonical variables are grouped by pairs

    Examples
    --------
    >>> symplectic_identity(1)
    tensor([[ 0.,  1.],
            [-1.,  0.]], dtype=torch.float64)

    >>> symplectic_identity(2)
    tensor([[ 0.,  1.,  0.,  0.],
            [-1.,  0.,  0.,  0.],
            [ 0.,  0.,  0.,  1.],
            [ 0.,  0., -1.,  0.]], dtype=torch.float64)

    """
    block = symplectic_block(dtype=dtype, device=device)
    return torch.block_diag(*[block for _ in range(d)])


def symplectify(m:Tensor) -> Tensor:
    """
    Perform symplectification of a given input matrix

    Parameters
    ----------
    m: Tensor, even-dimension
        input matrix to symplectify

    Returns
    -------
    Tensor

    Examples
    --------
    >>> import torch
    >>> symplectify(torch.tensor([[1.0, 0.1], [0.0, 0.99]], dtype=torch.float64))
    tensor([[1.0050, 0.1005],
            [0.0000, 0.9950]], dtype=torch.float64)

    """
    d = len(m) // 2
    i = torch.eye(2*d, dtype=m.dtype, device=m.device)
    s = symplectic_identity(d, dtype=m.dtype, device=m.device)
    v = s @ (i - m) @ (i + m).inverse()
    w = 0.5*(v + v.T)
    return (s + w).inverse() @ (s - w)


def symplectic_inverse(m:Tensor) -> Tensor:
    """
    Compute inverse of a given input symplectic matrix

    Parameters
    ----------
    m: Tensor, even-dimension, symplectic
        input matrix

    Returns
    -------
    Tensor

    Examples
    --------
    >>> import torch
    >>> symplectic_inverse(torch.tensor([[1.0, 0.1], [0.0, 1.0]], dtype=torch.float64))
    tensor([[ 1.0000, -0.1000],
            [ 0.0000,  1.0000]], dtype=torch.float64)

    """
    d = len(m) // 2
    s = symplectic_identity(d, dtype=m.dtype, device=m.device)
    return -s @ m.T @ s


def is_symplectic(m:Tensor, *,
                  epsilon:float=1.0E-12) -> bool:
    """
    Test symplectic condition for a given input matrix elementwise

    Parameters
    ----------
    matrix: Tensor
        input matrix
    epsilon: float
        tolerance epsilon
    
    Returns
    -------
    bool
    
    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> is_symplectic(rotation_block(torch.tensor(pi, dtype=torch.float64)))
    True
    
    """
    d = len(m) // 2
    s = symplectic_identity(d, dtype=m.dtype, device=m.device)
    return all(epsilon > (m.T @ s @ m - s).abs().flatten())


def rotation_block(angle:Tensor) -> Tensor:
    """
    Generate 2D rotation block [[cos(angle), sin(angle)], [-sin(angle), cos(angle)]] matrix

    Parameters
    ----------
    angle: Tensor
        rotation angle

    Returns
    -------
    Tensor

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> rotation_block(torch.tensor(pi, dtype=torch.float64))
    tensor([[-1.0000e+00,  1.2246e-16],
            [-1.2246e-16, -1.0000e+00]], dtype=torch.float64)

    """
    c, s = angle.cos(), angle.sin()
    return torch.stack([*map(torch.stack, [[c, +s], [-s, c]])])


def rotation(*angles:Tensor) -> Tensor:
    """
    Generate rotation matrix using given angles.

    Parameters
    ----------
    angles: Tensor
        rotation angles

    Returns
    -------
    Tensor

    Note
    ----
    Block rotation is [[cos(angle), sin(angle)], [-sin(angle), cos(angle)]]

    Examples
    --------
    >>> from math import pi
    >>> import torch
    >>> rotation(*torch.tensor([pi, -pi], dtype=torch.float64))
    tensor([[-1.0000e+00,  1.2246e-16,  0.0000e+00,  0.0000e+00],
            [-1.2246e-16, -1.0000e+00,  0.0000e+00,  0.0000e+00],
            [ 0.0000e+00,  0.0000e+00, -1.0000e+00, -1.2246e-16],
            [ 0.0000e+00,  0.0000e+00,  1.2246e-16, -1.0000e+00]],
           dtype=torch.float64)

    """
    return torch.block_diag(*torch.func.vmap(rotation_block)(torch.stack(angles)))


def projection(d:int,
               p:int, *,
               dtype=torch.float64,
               device=torch.device('cpu')) -> Tensor:
    """
    Plane projection matrix

    Parameters
    ----------
    d: int
        total number of planes
    p: int
        plane id (1, 2, ..., n)
    dtype: torch.dtype, default=torch.float64
        data type
    device: torch.device, torch.device=torch.device('cpu')
        data device

    Returns
    -------
    Tensor

    Examples
    --------
    >>> projection(2, 1)
    tensor([[1., 0., 0., 0.],
            [0., 1., 0., 0.],
            [0., 0., 0., 0.],
            [0., 0., 0., 0.]], dtype=torch.float64)
    >>> projection(2, 2)
    tensor([[0., 0., 0., 0.],
            [0., 0., 0., 0.],
            [0., 0., 1., 0.],
            [0., 0., 0., 1.]], dtype=torch.float64)

    """
    m = torch.tensor([[1, 0], [0, 1]], dtype=dtype, device=device)
    return torch.block_diag(*[m*(i == (p - 1)) for i in range(d)])
