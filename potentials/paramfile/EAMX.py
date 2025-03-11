# EAMX model with param checker (v2)
# written fully in python (not translated from mathematica)
# Daw and Chandross: 21 Apr 2023
# see and reference these two seminal papers:
# (1) M. S. Daw & M. E. Chandross, Acta Materialia, v248 a118771 (2023)
#   "Simple parameterization of embedded atom method potentials for FCC metals"
#    https://doi.org/10.1016/j.actamat.2023.118771
# (2) M. S. Daw & M. E. Chandross, Acta Materialia, v248 a118771 (2023)
#   "Simple parameterization of embedded atom method potentials for FCC alloys"
#    https://doi.org/10.1016/j.actamat.2023.118772
from typing import Optional

import numpy as np
import numpy.typing as npt
import math


# Element parameters as defined in the original two papers
element_params = {}
element_params['Cu'] = {'r1nne': 2.56, 'Ece': 3.54, 'Be': 0.86, 'beta': 1.76, 'phi0': 0.29, 'rcut': 4.98, 'rho0':1.000}
element_params['Ag'] = {'r1nne': 2.89, 'Ece': 2.85, 'Be': 0.65, 'beta': 1.63, 'phi0': 0.23, 'rcut': 5.64, 'rho0':0.731}
element_params['Au'] = {'r1nne': 2.89, 'Ece': 3.93, 'Be': 1.04, 'beta': 1.82, 'phi0': 0.16, 'rcut': 5.63, 'rho0':0.896}
element_params['Ni'] = {'r1nne': 2.49, 'Ece': 4.45, 'Be': 1.13, 'beta': 2.13, 'phi0': 0.31, 'rcut': 4.85, 'rho0':1.056}
element_params['Pd'] = {'r1nne': 2.75, 'Ece': 3.91, 'Be': 1.22, 'beta': 1.87, 'phi0': 0.26, 'rcut': 5.36, 'rho0':1.233}
element_params['Pt'] = {'r1nne': 2.77, 'Ece': 5.77, 'Be': 1.77, 'beta': 2.21, 'phi0': 0.22, 'rcut': 5.41, 'rho0':1.096}
element_params['Av'] = {'r1nne': 2.70, 'Ece': 4.10, 'Be': 1.10, 'beta': 1.90, 'phi0': 0.25, 'rcut': 5.30, 'rho0':1.0}

# χ cross-element parameters as defined in the second original paper
chivals = {}
chivals['Cu'] = {'Cu': 0.000, 'Ag':-0.106, 'Au': 0.000, 'Ni': 0.017, 'Pd':-0.022, 'Pt':-0.090}
chivals['Ag'] = {'Cu':-0.106, 'Ag': 0.000, 'Au': 0.019, 'Ni':-0.085, 'Pd':-0.125, 'Pt':-0.068}
chivals['Au'] = {'Cu': 0.000, 'Ag': 0.019, 'Au': 0.000, 'Ni': 0.124, 'Pd':-0.133, 'Pt': 0.005}
chivals['Ni'] = {'Cu': 0.017, 'Ag':-0.085, 'Au': 0.124, 'Ni': 0.000, 'Pd': 0.104, 'Pt':-0.008}
chivals['Pd'] = {'Cu':-0.022, 'Ag':-0.125, 'Au':-0.133, 'Ni': 0.104, 'Pd': 0.000, 'Pt': 0.001}
chivals['Pt'] = {'Cu':-0.090, 'Ag':-0.068, 'Au': 0.005, 'Ni':-0.008, 'Pd': 0.001, 'Pt': 0.090}


# Common utility functions
def H(r: npt.ArrayLike,  rcut: float) -> np.array:
    """Heaviside cutoff function that is 1 for r < rcut and 0 for r >= rcut""" 
    return np.heaviside(rcut - r, 0.5)

def fz(z: npt.ArrayLike) -> np.array:
    """Core f(z) function used by EAM-X potentials"""
    return np.exp(-z) - 1 + z

def d1fz(z: npt.ArrayLike) -> np.array:
    """First derivative of f(z)"""
    return -np.exp(-z) + 1

def d2fz(z: npt.ArrayLike) -> np.array:
    """Second derivative of f(z)"""
    return np.exp(-z)

def d3fz(z: npt.ArrayLike) -> np.array:
    """Third derivative of f(z)"""
    return -np.exp(-z)






class EAMXElement():
    
    def __init__(self,
                 rho0: float = 1.0,
                 beta: Optional[float] = None,
                 phi0: Optional[float] = None,
                 gamma: Optional[float] = None,
                 r1nne: Optional[float] = None,
                 rcut: Optional[float] = None,
                 Ece: Optional[float] = None,
                 Be: Optional[float] = None,
                 ref='fcc'):

        # Define neighbor shell information based on a reference
        if ref == 'fcc':
            self.Zs = np.array([12, 6, 24, 12])
            self.zetas = np.sqrt(np.array([1, 2, 3, 4]))
            self.nshellmax = self.Zs.size

            assert beta is not None
            assert phi0 is not None
            assert r1nne is not None
            assert rcut is not None
            assert Ece is not None
            assert Be is not None

            if gamma is None:
                gamma = 2 * beta

        else:
            raise ValueError('Unsupported ref style')

        self.rho0 = rho0
        self.beta = beta
        self.phi0 = phi0
        self.gamma = gamma
        self.r1nne = r1nne
        self.rcut = rcut
        self.Ece = Ece
        self.Be = Be

    @classmethod
    def by_symbol(cls, symbol):
        """Initializes based on published values for a given element symbol"""
        return cls(**element_params[symbol])


    # define rho(r) and derivatives
    # ignore derivatives of cutoff
    def rho(self, r, **params):
        """The rho(r) potential function"""
        rho0, beta, r1nne, rcut = self.__rho_params(**params)
        z = beta*(r - rcut)
        z1 = beta*(r1nne - rcut)

        return rho0 * (fz(z) / fz(z1)) * H(r, rcut)

    def d1rho(self, r, **params):
        """First derivative of rho(r)"""
        rho0, beta, r1nne, rcut = self.__rho_params(**params)
        z = beta*(r - rcut)
        z1 = beta*(r1nne - rcut)

        return rho0 * (beta * d1fz(z) / fz(z1)) * H(r, rcut)

    def d2rho(self, r, **params):
        """Second derivative of rho(r)"""
        rho0, beta, r1nne, rcut = self.__rho_params(**params)
        z = beta*(r - rcut)
        z1 = beta*(r1nne - rcut)

        return rho0 * (beta**2 * d2fz(z) / fz(z1)) * H(r, rcut)

    def d3rho(self, r, **params):
        """Third derivative of rho(r)"""
        rho0, beta, r1nne, rcut = self.__rho_params(**params)
        z = beta*(r - rcut)
        z1 = beta*(r1nne - rcut)

        return rho0 * (beta**3 * d3fz(z) / fz(z1)) * H(r, rcut)

    def __rho_params(self, **params):
        """Utility function that retrieves parameters for rho functions"""
        rho0 = params.get('rho0', self.rho0)
        beta = params.get('beta', self.beta)
        r1nne = params.get('r1nne', self.r1nne)
        rcut = params.get('rcut', self.rcut)

        return rho0, beta, r1nne, rcut


    # define rhobar and derivatives w.r.t. r1nn 
    def rhobar(self, r1nn, **params):
        """rhobar(r1nn), a.k.a. sum of rho, for a reference system with r1nn spacing"""
        rs = self.zetas * r1nn
        rhos = self.rho(rs, **params)
        return np.dot(self.Zs, rhos)

    def d1rhobar(self, r1nn, **params):
        """First derivative of rhobar(r1nn)"""
        rs = self.zetas * r1nn
        d1rhos = self.d1rho(rs, **params)
        return np.dot(self.Zs, d1rhos * self.zetas)

    def d2rhobar(self, r1nn, **params):
        """Second derivative of rhobar(r1nn)"""
        rs = self.zetas * r1nn
        d2rhos = self.d2rho(rs, **params)
        return np.dot(self.Zs, d2rhos * self.zetas**2)

    def d3rhobar(self, r1nn, **params):
        """Third derivative of rhobar(r1nn)"""
        rs = self.zetas * r1nn
        d3rhos = self.d3rho(rs, **params)
        return np.dot(self.Zs, d3rhos * self.zetas**3)


    # define rhobare and derivatives (rhobar and derivatives evaluated at equilibrium) 
    def rhobare(self, **params):
        """rhobar evaluated at equilibrium r1nne"""
        r1nne = params.get('r1nne', self.r1nne)
        return self.rhobar(r1nne, **params)

    def d1rhobare(self, **params):
        """First derivative of rhobar evaluated at equilibrium r1nne"""
        r1nne = params.get('r1nne', self.r1nne)
        return self.d1rhobar(r1nne, **params)

    def d2rhobare(self, **params):
        """Second derivative of rhobar evaluated at equilibrium r1nne"""
        r1nne = params.get('r1nne', self.r1nne)
        return self.d2rhobar(r1nne, **params)

    def d3rhobare(self, **params):
        """Third derivative of rhobar evaluated at equilibrium r1nne"""
        r1nne = params.get('r1nne', self.r1nne)
        return self.d3rhobar(r1nne, **params)


    # phi(r) and derivatives
    # ignore derivatives of cutoff
    def phi(self, r, **params):
        """The phi(r) potential function"""
        phi0, gamma, r1nne, rcut = self.__phi_params(**params)
        z = gamma * (r - rcut)
        z1 = gamma * (r1nne - rcut)

        return phi0 * (fz(z) / fz(z1)) * H(r, rcut)

    def d1phi(self, r, **params):
        """First derivative of phi(r)"""
        phi0, gamma, r1nne, rcut = self.__phi_params(**params)
        z = gamma * (r - rcut)
        z1 = gamma * (r1nne - rcut)

        return phi0 * (gamma * d1fz(z) / fz(z1)) * H(r, rcut)

    def d2phi(self, r, **params):
        """Second derivative of phi(r)"""
        phi0, gamma, r1nne, rcut = self.__phi_params(**params)
        z = gamma * (r - rcut)
        z1 = gamma * (r1nne - rcut)

        return phi0 * (gamma**2 * d2fz(z) / fz(z1)) * H(r, rcut)

    def d3phi(self, r, **params):
        """Third derivative of phi(r)"""
        phi0, gamma, r1nne, rcut = self.__phi_params(**params)
        z = gamma * (r - rcut)
        z1 = gamma * (r1nne - rcut)

        return phi0 * (gamma**3 * d3fz(z) / fz(z1)) * H(r, rcut)

    def __phi_params(self, **params):
        """Utility function that retrieves parameters for rho functions"""
        phi0 = params.get('phi0', self.phi0)
        gamma = params.get('gamma', self.gamma)
        r1nne = params.get('r1nne', self.r1nne)
        rcut = params.get('rcut', self.rcut)

        return phi0, gamma, r1nne, rcut


    # define phibar and derivatives
    def phibar(self, r1nn, **params):
        """phibar(r1nn), a.k.a. sum of phi, for a reference system with r1nn spacing"""
        rs = self.zetas * r1nn
        phis = self.phi(rs, **params) 
        return np.dot(self.Zs, phis)

    def d1phibar(self, r1nn, **params):
        """First derivative of phibar(r1nn)"""
        rs = self.zetas * r1nn
        d1phis = self.d1phi(rs, **params) 
        return np.dot(self.Zs, d1phis * self.zetas)

    def d2phibar(self, r1nn, **params):
        """Second derivative of phibar(r1nn)"""
        rs = self.zetas * r1nn
        d2phis = self.d2phi(rs, **params) 
        return np.dot(self.Zs, d2phis * self.zetas**2)

    def d3phibar(self, r1nn, **params):
        """Third derivative of phibar(r1nn)"""
        rs = self.zetas * r1nn
        d3phis = self.d3phi(rs, **params) 
        return np.dot(self.Zs, d3phis * self.zetas**3)


    # define phibare and derivatives (phibar and derivatives evaluated at equilibrium) 
    def phibare(self, **params):
        """phibar evaluated at equilibrium r1nne"""
        r1nne = params.get('r1nne', self.r1nne)
        return self.phibar(r1nne, **params)

    def d1phibare(self, **params):
        """First derivative of phibar evaluated at equilibrium r1nne"""
        r1nne = params.get('r1nne', self.r1nne)
        return self.d1phibar(r1nne, **params)

    def d2phibare(self, **params):
        """Second derivative of phibar evaluated at equilibrium r1nne"""
        r1nne = params.get('r1nne', self.r1nne)
        return self.d2phibar(r1nne, **params)

    def d3phibare(self, **params):
        """Third derivative of phibar evaluated at equilibrium r1nne"""
        r1nne = params.get('r1nne', self.r1nne)
        return self.d3phibar(r1nne, **params)


    # define U and derivatives at equilibrium
    def Ue(self, **params):
        """Potential energy U at equilibrium"""
        r1nne, Ece, Be = self.__Ue_params(**params)
        return -Ece

    def d2Ue(self, **params):
        """Second derivative of U at equilibrium"""
        r1nne, Ece, Be = self.__Ue_params(**params)
        return 9 * Be * r1nne / math.sqrt(2.)

    def d3Ue(self, **params):
        """Third derivative of U at equilibrium"""
        r1nne, Ece, Be = self.__Ue_params(**params)
        return -27 * math.sqrt( math.sqrt(2.) * Be**3 * r1nne**3 / Ece )

    def __Ue_params(self, **params):
        r1nne = params.get('r1nne', self.r1nne)
        Ece = params.get('Ece', self.Ece)
        Be = params.get('Be', self.Be)
        return r1nne, Ece, Be


    # Compute coefficients for embedding function
    def F0(self, **params):
        """F0 embedding energy function coefficient"""
        return self.Ue(**params) - self.phibare(**params) / 2.

    def F1(self, **params):
        """F1 embedding energy function coefficient"""
        return -self.d1phibare(**params) / (2. * self.d1rhobare(**params))

    def F2(self, **params):
        """F2 embedding energy function coefficient"""
        F1 = self.F1(**params)
        d2U = self.d2Ue(**params)
        d2phi = self.d2phibare(**params)
        d1rho = self.d1rhobare(**params)
        d2rho = self.d2rhobare(**params)
        return (d2U - d2phi / 2. - F1 * d2rho) / d1rho**2

    def F3(self, **params):
        """F3 embedding energy function coefficient"""
        F1 = self.F1(**params)
        F2 = self.F2(**params)
        d3U = self.d3Ue(**params)
        d3phi = self.d3phibare(**params)
        d1rho = self.d1rhobare(**params)
        d2rho = self.d2rhobare(**params)
        d3rho = self.d3rhobare(**params)
        return (d3U - d3phi / 2. - F1 * d3rho - 3. * F2 * d1rho * d2rho) / d1rho**3
        
    def F4(self, **params):
        """F4 embedding energy function coefficient"""
        F0 = self.F0(**params)
        F1 = self.F1(**params)
        F2 = self.F2(**params)
        F3 = self.F3(**params)
        rhobare = self.rhobare(**params)
        return -24. * (F0 - F1 * rhobare + F2 * rhobare**2 / 2. - F3 * rhobare**3 / 6.) / rhobare**4

    def F(self, rhobar, **params):
        """The F(rhobar) potential function"""
        rhobare = self.rhobare(**params)
        F0 = self.F0(**params)
        F1 = self.F1(**params)
        F2 = self.F2(**params)
        F3 = self.F3(**params)
        F4 = self.F4(**params)
        drhobar = rhobar - rhobare
        return F0 + F1 * drhobar + F2 * drhobar**2 / 2. + F3 * drhobar**3 / 6. + F4 * drhobar**4 / 24.


    # define criteria for bounds on parameters
    # check params against those criteria and flag if they fail
    def paramOK(self, **params):
        F0 = self.F0(**params)
        F1 = self.F1(**params)
        F2 = self.F2(**params)
        F3 = self.F3(**params)
        F4 = self.F4(**params)
        
        fail = False

        if F2 <= 0.0:
            print('Parameters failed criteria that F2 > 0')
            fail = True

        if F4 <= 0.0:
            print('Parameters failed criteria that F4 > 0')
            fail = True

        if 2 * F2 * F4 - F3**2 <= 0.0 and F3 <= 0.0:
            print('Parameters failed criteria that 2*F2*F4 - F3^2 > 0 or F3 > 0')
            fail = True

        r1nne = params.get('r1nne', self.r1nne)
        rcut = params.get('rcut', self.rcut)
        rcutmax = math.sqrt(self.nshellmax + 1) * r1nne  # max is figured from settings at top for FCC only 
        if rcut >= rcutmax:
            print('Parameters failed criteria that rcut < rcutmax')
            fail = True

        if fail:
            print(" F0 = ", F0)
            print(" F1 = ", F1)
            print(" F2 = ", F2)
            print(" F3 = ", F3)
            print(" F4 = ", F4)
            print(" rcutmax = ", rcutmax)
            print(" rcut = ", rcut)
            
            return 0.0
        
        return 1.0


class EAMX():

    def __init__(self, elements=None, chis=None):
        if elements is None:
            self.elements = {}
        if chis is None:
            self.chis = {}

    def add_element(self,
                    symbol: str,
                    mass: float,
                    
                    element = None,
                    rho0: float = 1.0,
                    beta: Optional[float] = None,
                    phi0: Optional[float] = None,
                    gamma: Optional[float] = None,
                    r1nne: Optional[float] = None,
                    rcut: Optional[float] = None,
                    Ece: Optional[float] = None,
                    Be: Optional[float] = None,
                    ref='fcc'):
        """Adds a new element to the EAMX potential"""
        
        # Check if already defined
        if symbol in self.elements:
            raise ValueError('Parameters already defined for symbol')


        newelement = EAMXElement(symbol, rho0=rho0, beta=beta, phi0=phi0,
                                 gamma=gamma, r1nne=r1nne, rcut=rcut, Ece=Ece,
                                 Be=Be, ref=ref)
        self.elements.append(newelement)
        
        self.chis[symbol] = {}
        for sym in self.chis:
            self.chis[sym][symbol] = 0.0

    def add_element_by_symbol(self, symbol):
        """Adds a new element to the EAMX potential using published parameters for a element symbol"""
        self.add_element(symbol, **element_params[symbol])

    def set_chi(self, symbol1, symbol2, chi, symmetric=True):
        """Set a chi value to use with a pair of element symbols"""
        self.chis[symbol1][symbol2] = chi
        if symmetric:
            self.chis[symbol2][symbol1] = chi

    def set_chi_by_symbols(self, symbol1, symbol2, symmetric=True):
        """Set a chi value for two elements to the associated published value"""
        chi = chivals[symbol1][symbol2]
        self.set_chi(symbol1, symbol2, chi, symmetric=symmetric)

    