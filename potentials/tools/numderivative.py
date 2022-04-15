# coding: utf-8
# Standard Python libraries
from typing import Tuple

# https://numpy.org/
import numpy as np
import numpy.typing as npt

def numderivative(x: npt.ArrayLike,
                  y: npt.ArrayLike,
                  n: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes the numerical derivative for a tabulated function.
    
    Parameters
    ----------
    x : array-like 
        Coordinates where the function is tabulated.  Needs to be equally
        spaced for the derivatives to be correct.
    y : array-like
        Function evaluations at the x coordinates.
    n : int, optional
        The number of times the derivative of y is computed.
    
    Returns
    -------
    newx : np.NDArray
        Updated coordinates with N-n values. The coordinates are shifted with each
        derivative to correspond to the halfway point between previous coordinates.
    newy : np.NDArray
        N-n values for the nth derivative of y.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    if n == 0:
        # Return data as given
        return x, y
    
    elif n > 0:
        # Compute the numerical derivative
        deltax = x[1] - x[0]
        newx = x[:-1] + deltax / 2
        newy = (y[1:] - y[:-1]) / deltax
        
        # Iterate until n=0
        return numderivative(newx, newy, n=n-1)
    
    else:
        raise ValueError('n must be >=0')