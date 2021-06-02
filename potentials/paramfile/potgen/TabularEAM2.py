import numpy as np

from .tools import get_atomicsymbol, aslist

from scipy.interpolate import CubicSpline
import warnings

class BaseEAM():
    
    def __init__(self):
        pass
        
    def F_rho(self, rho, symbol=None):
        """The embedding energy function F(rho)"""
        return 0*rho

    def rho_r(self, r, symbol=None):
        """The electron density function rho(r)"""
        return 0*r

    def phi_r(self, r, symbol=None):
        """The pair interaction function phi(r)"""
        return 0*r

    def rphi_r(self, r, symbol=None):
        """The pair interaction function as r * phi(r)"""
        return 0*r

    def z_r(self, r, symbol=None):
        """The effective charge function z(r)"""
        return 0*r

class TableEAM(BaseEAM):

    def __init__(self, f=None):

        self.__F_rho_table = {}
        self.__rho_r_table = {}
        self.__z_r_table = {}
        self.__numrho = None
        self.__deltarho = None
        self.__cutoffrho = None
        self.__numr = None
        self.__deltar = None
        self.__cutoffr = None

        if f is not None:
            self.load(f)

    @property
    def numrho(self):
        """int : The number of rho values associated with the F(rho) table."""
        return self.__numrho

    @property
    def deltarho(self):
        """float : The step size used between each rho value in the F(rho) table."""
        return self.__deltarho

    @property
    def cutoffrho(self):
        """float : The maximum rho value used with the F(rho) table."""
        return self.__cutoffrho

    @property
    def rho_table(self):
        """numpy.NDArray : The rho values from 0.0 to cutoffrho associated with the F(rho) table."""
        return self.__rho_table
    
    def set_rho(self, numrho=None, deltarho=None, cutoffrho=None):
        """
        Sets the values of rho which correspond to the F(rho) table values.  At
        least two out of the three parameters are required.  The rho values must
        be set prior to setting F(rho) values.

        Parameters
        ----------
        numrho : int, optional
            The number of rho points to use.
        deltarho : float, optional
            The rho step size to use.
        cutoffrho : float, optional
            The maximum rho value to use.
        """
        assert len(self.__F_rho_table) == 0, 'rho cannot be reset after F(rho) values have been set'

        # Identify numrho if needed
        if numrho is None:
            assert deltarho is not None and cutoffrho is not None, 'At least two parameters must be given'
            floatnumrho = cutoffrho / deltarho
            numrho = int(round(floatnumrho)) + 1
            assert np.isclose(numrho, floatnumrho), 'deltarho does not evenly divide cutoffrho'
        
        # Identify cutoffrho if needed
        elif cutoffrho is None:
            assert deltarho is not None, 'At least two parameters must be given'
            cutoffrho = deltarho * (numrho - 1)

        rho_table = np.linspace(0.0, cutoffrho, numrho)
        assert np.isclose(deltarho, rho_table[1]), 'deltarho mismatch'

        self.__numrho = numrho
        self.__deltarho = deltarho
        self.__cutoffrho = cutoffrho
        self.__rho_table = rho_table
            
    @property
    def numr(self):
        """int : The number of r values associated with the rho(r) and z(r) tables."""
        return self.__numr

    @property
    def deltar(self):
        """float : The step size used between each r value in the rho(r) and z(r) tables."""
        return self.__deltar

    @property
    def cutoffr(self):
        """float : The maximum r value used with the rho(r) and z(r) tables."""
        return self.__cutoffr

    @property
    def r_table(self):
        """numpy.NDArray : The r values from 0.0 to cutoffr associated with rho(r) and z(r) tables."""
        return self.__r_table
    
    def set_r(self, numrho=None, deltarho=None, cutoffrho=None):
        """
        Sets the values of r which correspond to the rho(r) and z(r) table values.  At
        least two out of the three parameters are required.  The r values must
        be set prior to setting rho(r) and z(r) values.

        Parameters
        ----------
        numrh : int, optional
            The number of r points to use.
        deltar : float, optional
            The r step size to use.
        cutoffr : float, optional
            The maximum r value to use.
        """
        assert len(self.__rho_r_table) == 0, 'r cannot be reset after rho(r) values have been set'
        assert len(self.__z_r_table) == 0, 'r cannot be reset after z(r) values have been set'

        # Identify numr if needed
        if numr is None:
            assert deltar is not None and cutoffr is not None, 'At least two parameters must be given'
            floatnumr = cutoffr / deltar
            numr = int(round(floatnumr)) + 1
            assert np.isclose(numr, floatnumr), 'deltar does not evenly divide cutoffr'
        
        # Identify cutoffr if needed
        elif cutoffr is None:
            assert deltar is not None, 'At least two parameters must be given'
            cutoffr = deltar * (numr - 1)

        r_table = np.linspace(0.0, cutoffr, numr)
        assert np.isclose(deltar, r_table[1]), 'deltar mismatch'

        self.__numr = numr
        self.__deltar = deltar
        self.__cutoffr = cutoffr
        self.__r_table = r_table

    def F_rho_table(self, symbol=None):
        """
        Accesses the table of F(rho) values.

        Parameters
        ----------
        symbol : str, optional
            The symbol for the element model to use.  Optional if the potential
            is for an element, i.e. only one F(rho) function.
        """
        if symbol is None:
            if len(self.__F_rho_table) == 1:
                symbol = list(self.__F_rho_table.keys())[0]
            elif len(self.__F_rho_table) == 0:
                raise ValueError('no F(rho) tables set')
            else:
                raise ValueError('symbol is needed as multiple F(rho) tables are set')
        
        if symbol in self.__F_rho_table:
            return self.__F_rho_table[symbol]
        else:
            raise ValueError(f'no F(rho) table has been set for symbol {symbol}')

    def set_F_rho(self, symbol, F_rho_table):

        assert self.numrho is not None, 'rho values must be set before setting F(rho)'
        assert len(F_rho_table) == len(self.r_table), 'number of F(rho) values must match number of set rho values'

        self.__F_rho_table[symbol] = np.asarray(F_rho_table, dtype=float)

    def rho_r_table(self):
        return self.__rho_r_table

    def z_r_table(self):
        return self.__z_r_table

    

    

    def F_rho(self, rho, symbol=None):
        """
        The embedding energy function F(rho).  Values are interpolated from
        F_rho_table using cubic splines.  If you don't want interpolations,
        then access the table directly.

        Parameters
        ----------
        rho : float or array-like object
            The rho values to evaluate F at.
        symbol : str, optional
            The symbol for the element model to use.  Optional if the potential
            is for an element, i.e. only one F(rho) function.
        """ 
        spline = CubicSpline()