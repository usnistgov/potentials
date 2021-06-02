from __future__ import print_function, division, absolute_import
from .EAMPotential import EAMPotential
import numpy as np

class ATFS(EAMPotential, object):
    """Generic class for representing an EAM-style potential"""
    
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            if len(kwargs) > 0:
                raise TypeError('Cannot give both params and file')
            self.load(args[0])
        elif len(args) == 0:
            self.set_params(**kwargs)
        else:
            raise TypeError('__init__() can take at most one non-keyword argument')
        
    def pair(self, r, symbol=None):
        """The pair interaction function: phi(r)"""
        
        # Define the component functions
        def pairFS(r, c, c0, c1, c2):
            """Finis-Sinclair component"""
            return (r - c)**2 * (c0 + c1 * r + c2 * r * r)
            
        def pairAT(r, B, a0, alpha):
            """Ackland-Thetford correction"""
            return B * (a0 - r)**3 * np.exp(-alpha * r)
        
        # Extract the parameters
        c = self.__params['c']
        c0 = self.__params['c0']
        c1 = self.__params['c1']
        c2 = self.__params['c2']
        B = self.__params['B']
        a0 = self.__params['a0']
        alpha = self.__params['alpha']
        
        return (np.piecewise(r, [r <= c, r > c], [pairFS, 0], c, c0, c1, c2)
              + np.piecewise(r, [r <= a0, r > a0], [pairAT, 0], B, a0, alpha))
        
    def rpair(self, r, symbol=None):
        """Pair inreraction multiplied by r: r*phi(r)"""
        return r * self.pair(r)
        
    def embedding(self, rho, symbol=None):
        """The embedding energy function: F(rhobar)"""
        return -rho ** 0.5
        
    def electrondensity(self, r, symbol=None):
        """The electron density function: rho(r)"""
        
        # Define the component functions
        def rho(r, A, d, beta):
            return A**2 * (d - r)**2 + beta * (r - d)**3 / d
        
        # Extract the parameters
        A = self.__params['A']
        d = self.__params['d']
        beta = self.__params['beta']
        
        return np.piecewise(r, [r <= d, r > d], [rho, 0], A, d, beta)
        
    def load(self, fname):
        """Load parameter file"""
        params = {}
        with open(fname) as f:
            for line in f:
                line = line.strip()
                terms = line.split()
                if len(terms) > 1 and line[0] != '#':
                    assert len(terms) == 2, 'Invalid parameter file'
                    params[terms[0]] = float(terms[1])
        self.set_params(**params)
    
    def set_params(self, **kwargs):
        """Sets default parameter values if not given"""
        params = ['A', 'B', 'a0', 'c', 'c0', 'c1', 'c2', 'd', 'alpha', 'beta']
        
        self.__params = {}
        for param in params:
            self.__params[param] = kwargs.pop(param, 0.0)
        if len(kwargs) > 0:
            raise KeyError('Invalid parameters found')