from __future__ import print_function, division, absolute_import
from .EAMPotential import EAMPotential
from .tools import get_atomicnumber
import numpy as np

class MoldyFS(EAMPotential, object):
    """Class for EAM potentials based on Moldy ATVF format"""
    
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            if len(kwargs) > 0:
                raise TypeError('Cannot give both params and file')
            self.load(args[0])
        elif len(args) == 0:
            self.set_params(**kwargs)
        else:
            raise TypeError('__init__() can take at most one non-keyword argument')
    
    def __hspline(self, r, A, R):
        """Cubic spline with heavyside used by Moldy potentials"""
        
        def spline(r, A, R):
            """Cubic spline"""
            return A * (R - r)**3
        
        # return with heavyside (piecewise) applied
        return np.piecewise(r, [r < R, r >= R], [spline, 0], A, R)
        
    def __d_hspline(self, r, A, R):
        """Derivative of hspline function"""
        
        def d_spline(r, A, R):
            """Derivative of cubic spline"""
            return -3 * A * (R - r)**2 
           
        # return with heavyside (piecewise) applied
        return np.piecewise(r, [r < R, r >= R], [d_spline, 0], A, R)
    
    def pairbiersack(self, r):
        """Biersack-Ziegler close-range pair interaction"""
        
        # Screening function
        return self.rpairbiersack(r) / r

    def d_pairbiersack(self, r):
        """Derivative of Biersack-Ziegler close-range pair interaction"""
        z1 = self.__params['z1']
        z2 = self.__params['z2']
        
        electron  = 1.602176487e-19
        angstrom  = 1.0e-10
        zed = z1 * z2 * 8.98755178e9 * electron / angstrom
        
        # Screening length
        a = (0.8854 * 0.529) / (z1 ** 0.23 + z2 ** 0.23) 
        x = r / a

        return (-zed / r * ((1.0 / r + 3.2 / a) * 0.1818 * np.exp(-3.2 * x)
                          + (1.0 / r + 0.9423 / a) * 0.5099 * np.exp(-0.9423 * x)
                          + (1.0 / r + 0.4029 / a) * 0.2802 * np.exp(-0.4029 * x)
                          + (1.0 / r + 0.2016 / a) * 0.02817 * np.exp(-0.2016 * x)))

    def rpairbiersack(self, r):
        """r times Biersack-Ziegler close-range pair interaction"""
        z1 = self.__params['z1']
        z2 = self.__params['z2']
        
        electron  = 1.602176487e-19
        angstrom  = 1.0e-10
        zed = z1 * z2 * 8.98755178e9 * electron / angstrom
        
        # Screening length
        a = (0.8854 * 0.529) / (z1 ** 0.23 + z2 ** 0.23) 
        x = r / a
        
        # Screening function
        return zed  * (0.1818 * np.exp(-3.2 * x) 
                     + 0.5099 * np.exp(-0.9423 * x) 
                     + 0.2802 * np.exp(-0.4029 * x) 
                     + 0.02817 * np.exp(-0.2016 * x)) 
    
    def pairspline(self, r):
        """Spline component of pair interaction"""
        # Scale r values by lattice parameter
        rs = r / self.__params['alat']
        
        # Sum spline components
        v = np.zeros_like(rs)
        for a_pair, r_pair in zip(self.__params['a_pair'], self.__params['r_pair']):
            v += self.__hspline(rs, a_pair, r_pair)
        
        return v

    def d_pairspline(self, r):
        """Derivative of spline component of pair interaction"""
        # Scale r values by lattice parameter
        rs = r / self.__params['alat']
        
        # Sum spline components
        v = np.zeros_like(rs)
        for a_pair, r_pair in zip(self.__params['a_pair'], self.__params['r_pair']):
            v += self.__d_hspline(rs, a_pair, r_pair)
            
        return v / self.__params['alat']

    def rpairspline(self, r):
        """r times spline component of pair interaction"""
        return r * self.pairspline(r)
    
    def pairjoin(self, r):
        """Linking component between Biersack and spline pair function components"""
        
        def expjoin(x, x1, y1, dy1, x2, y2, dy2):
            """
            Joining function of the form exp(b0 + b1 * x + b2 * x**2 + b3 * x**3)
            fitted such that endpoints x1, x2 have known values y1, y2 and known
            derivatives dy1, dy2, respectively.
            
            Parameters
            ----------
            x - value(s) to evaluate function.
            x1 - endpoint1
            y1 - f(x1)
            dy1 - df(x1)/dx 
            x2 - endpoint2
            y2 - f(x2)
            dy2 - df(x2)/dx
            """
            
            # Renormalize by t
            t = (x - x1) / (x2 - x1)
            
            # Compute polynomial constants
            b0 = np.log(y1)
            b1 = dy1 / y1 * (x2 - x1)
            b2 = -3 * b0 - 2 * b1 + 3 * np.log(y2) - dy2 / y2 * (x2 - x1)
            b3 = np.log(y2) - b2 - b1 - b0
            
            return np.exp(b0 + b1 * t + b2 * t**2 + b3 * t**3)  
            
        # Get parameters
        r1 = self.__params['biercut1']
        r2 = self.__params['biercut2']
        
        # Compute endpoints
        y1 = self.pairbiersack(r1)
        y2 = self.pairspline(r2)
        dy1 = self.d_pairbiersack(r1)
        dy2 = self.d_pairspline(r2)
        
        return expjoin(r, r1, y1, dy1, r2, y2, dy2)

    def rpairjoin(self, r):
        """r times linking component between Biersack and spline pair function components"""
        return r * self.pairjoin(r)
    
    def pair(self, r, symbol=None):
        """Complete pair function"""
        
        # Get Biersack-Ziegler cutoff distances
        r1 = self.__params['biercut1']
        r2 = self.__params['biercut2']
        
        return np.piecewise(r, 
                            [r <= r1, (r > r1) & (r < r2), r >= r2], 
                            [self.pairbiersack, self.pairjoin, self.pairspline])
        
    def rpair(self, r, symbol=None):
        """r times complete pair function"""
        
        # Get Biersack-Ziegler cutoff distances
        r1 = self.__params['biercut1']
        r2 = self.__params['biercut2']
        
        return np.piecewise(r, 
                            [r <= r1, (r > r1) & (r < r2), r >= r2], 
                            [self.rpairbiersack, self.rpairjoin, self.rpairspline])
        
    def embedding(self, rho, symbol=None):
        """The embedding energy function: F(rhobar)"""
        return -rho ** 0.5
        
    def electrondensity(self, r, symbol=None):
        """The electron density function: rho(r)"""
        
        # Scale r values by lattice parameter
        rs = r / self.__params['alat']
        
        # Sum spline components
        v = np.zeros_like(rs)
        for a_pair, r_pair in zip(self.__params['a_den'], self.__params['r_den']):
            v += self.__hspline(rs, a_pair, r_pair)
        
        # Set negative values to zero
        v[v < 0] = 0.0
        
        return v
        
    def load(self, fname):
        """Load parameter file"""
        params = {}
        with open(fname) as f:
            lines = f.readlines()
            
        symbols = lines[0].split()
        if len(symbols) == 1:
            params['z1'] = params['z2'] = get_atomicnumber(symbols[0])
            params['a_pair'] = lines[1].split()
            params['r_pair'] = lines[2].split()
            params['a_den'] = lines[3].split()
            params['r_den'] = lines[4].split()
            params['alat'] = lines[5].split()[0]
            try:
                terms = lines[6].split()
                assert len(terms) == 2
                params['biercut1'] = terms[0]
                params['biercut2'] = terms[1]
            except:
                pass
        else:
            raise ValueError('Cross potentials not handled yet')
        self.set_params(**params)
    
    def set_params(self, **kwargs):
        """Sets default parameter values if not given"""
        
        self.__params = {}
        
        self.__params['alat'] = float(kwargs.pop('alat'))
        self.__params['z1'] = int(kwargs.pop('z1'))
        self.__params['z2'] = int(kwargs.pop('z2'))
        self.__params['biercut1'] = float(kwargs.pop('biercut1', 0.0))
        self.__params['biercut2'] = float(kwargs.pop('biercut2', 0.0))
        
        assert len(kwargs['a_pair']) == len(kwargs['r_pair'])
        self.__params['a_pair'] = []
        self.__params['r_pair'] = []
        for a_pair, r_pair in zip(kwargs.pop('a_pair'), kwargs.pop('r_pair')):
            self.__params['a_pair'].append(float(a_pair))
            self.__params['r_pair'].append(float(r_pair))

        assert len(kwargs['a_den']) == len(kwargs['r_den'])
        self.__params['a_den'] = []
        self.__params['r_den'] = []
        for a_den, r_den in zip(kwargs.pop('a_den'), kwargs.pop('r_den')):
            self.__params['a_den'].append(float(a_den))
            self.__params['r_den'].append(float(r_den))
        
        if len(kwargs) > 0:
            raise KeyError('Invalid parameters found')