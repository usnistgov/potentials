# coding: utf-8
# Standard libraries
import io
import warnings
from pathlib import Path
from typing import Callable, Optional, Tuple, Union

# https://scipy.org/
from scipy.interpolate import CubicSpline

# https://numpy.org/
import numpy as np
import numpy.typing as npt

# https://matplotlib.org/
import matplotlib.pyplot as plt

# Local imports
from ..tools import numderivative

class EAM():
    """
    Class for building and analyzing LAMMPS funcfl eam parameter files 
    """
    def __init__(self,
                 f: Union[str, Path, io.IOBase, None] = None,
                 header: Optional[str] = None,
                 number: Optional[int] = None,
                 mass: Optional[float] = None,
                 alat: Optional[float] = None,
                 lattice: Optional[str] = None,
                 constants: str = 'lammps',
                 numr: Optional[int] = None,
                 cutoffr: Optional[float] = None,
                 deltar: Optional[float] = None,
                 numrho: Optional[int] = None,
                 cutoffrho: Optional[float] = None,
                 deltarho: Optional[float] = None):
        """
        Class initializer. Element information can be set at this time.
        
        Parameters
        ----------
        f : path-like object or file-like object, optional
            An existing parameter file to read in, either as a file path or as
            an open file-like object.  The default values of all other init
            parameters will be set based on the contents of this file if given.
            Not required if the potential functions are to be manually defined.
        header : str, optional
            Specifies the comments header to include at the beginning of the
            parameter file when generated.  Note that funcfl comments are
            limited to a single line.
        number : int, optional
            Element number.  If given, mass, alat and lattice must also be
            given.
        mass : float, optional
            Particle mass.  If given, number, alat and lattice must also be
            given.
        alat : float, optional
            Lattice constant.  If given, number, mass and lattice must also be
            given.
        lattice : str, optional
            Lattice type. If given, number, mass and alat must also be given.
        constants : str or tuple, optional
            Specifies the conversion constants to use for Hartree to eV and Bohr
            to Angstroms, which is used for converting z to phi.  Default value
            of "lammps" uses 27.2 and 0.529, respectively, which are what LAMMPS
            itself uses.  "precise" uses higher precision values.  Alternatively,
            a tuple of two floats allows for the constants to be directly
            defined.
        numr : int, optional
            The number of r values for which rho(r) and r*phi(r) should be
            tabulated. 
        cutoffr : float, optional
            The cutoff r value to use. If not given, will be set as 
            (numr - 1) * deltar.
        deltar : float, optional
            The r step size to use for the tabulation.  If not given, will
            be set as cutoffr / (numr - 1).
        numrho : int, optional
            The number of rho values for which F(rho) should be
            tabulated. 
        cutoff : float, optional
            The cutoff rho value to use. If not given, will be set as 
            (numrho - 1) * deltarho.
        delta : float, optional
            The rho step size to use for the tabulation.  If not given, will
            be set as cutoffrho / (numrho - 1).
        """
        if constants == 'lammps':
            self.__hartree = 27.2
            self.__bohr = 0.529
        elif constants == 'precise':
            self.__hartree = 27.211386245987406 
            self.__bohr = 0.529177210903
        else:
            try:
                assert len(constants) == 2
                self.__hartree = float(constants[0])
                self.__bohr = float(constants[1])
            except:
                raise ValueError('Invalid constants: must be "lammps", "precise" or two floats')

        # Initialize F terms
        self.__F_rho = None
        self.__F_rho_kwargs = None
        self.__F_rho_table = None

        # Initialize rho terms
        self.__rho_r = None
        self.__rho_r_kwargs = None
        self.__rho_r_table = None

        # Initialize phi terms
        self.__z_r = None
        self.__z_r_kwargs = None
        self.__z_r_table = None
        self.__phi_r = None
        self.__phi_r_kwargs = None
        self.__phi_r_table = None
        self.__rphi_r = None
        self.__rphi_r_kwargs = None
        self.__rphi_r_table = None
        
        # Initialize symbol terms
        self.__number = None
        self.__mass = None
        self.__alat = None
        self.__lattice = None

        if f is not None:
            self.load(f)

        else:
            # Initialize header
            if header is None:
                header = ''
            self.header = header

            # Set symbol values
            if (number is not None or mass is not None
                or alat is not None or lattice is not None):
                try:
                    assert number is not None
                    assert mass is not None
                    assert alat is not None
                    assert lattice is not None                
                except:
                    raise ValueError('number, mass, alat, and lattice must all be given or none given')
                self.set_symbol_info(number, mass, alat, lattice)

            # Set r
            if numr is not None:
                self.set_r(num=numr, cutoff=cutoffr, delta=deltar)
            
            # Set rho
            if numrho is not None:
                self.set_rho(num=numrho, cutoff=cutoffrho, delta=deltarho)

    @property
    def pair_style(self) -> str:
        """The LAMMPS pair_style associated with the class"""
        return 'eam'

    @property
    def hartree(self) -> float:
        """float: conversion constant from Hartree to eV"""
        return self.__hartree

    @property
    def bohr(self) -> float:
        """float: conversion constant from Bohr to Angstrom"""
        return self.__bohr

    @property
    def header(self) -> str:
        return self.__header
    
    @header.setter
    def header(self, value: str):
        if isinstance(value, str):
            value = value.strip()
            if '\n' not in value:
                self.__header = value
            else:
                raise ValueError('header limited to a single line')    
        else:
            raise TypeError('header must be a string')

    @property
    def numr(self) -> int:
        """int : The number of r values"""
        return self.__numr

    @property
    def cutoffr(self) -> float:
        """float : The cutoff r value"""
        return self.__cutoffr
    
    @property
    def deltar(self) -> float:
        """float : The step size between the r values"""
        return self.__deltar

    @property
    def r(self) -> np.ndarray:
        """numpy.NDArray : The r values associated with the tabulated functions"""
        try:
            self.numr
        except:
            raise AttributeError('r values not set: use set_r()')
        return np.linspace(0, self.numr * self.deltar, self.numr, endpoint=False)        

    def set_r(self,
              num: Optional[int] = None,
              cutoff: Optional[float] = None,
              delta: Optional[float] = None):
        """
        Sets the r values to use for tabulation.

        Parameters
        ----------
        num : int, optional
            The number of r values for which rho(r) and r*phi(r) should be
            tabulated. 
        cutoff : float, optional
            The cutoff r value to use. If not given, will be set as 
            (num - 1) * delta.
        delta : float, optional
            The r step size to use for the tabulation.  If not given, will
            be set as cutoff / (num - 1).
        """
        # Get current r values if they exist
        try:
            old_r = self.r
        except:
            old_r = None

        self.__numr = int(num)

        if cutoff is not None and delta is not None:
            self.__cutoffr = float(cutoff)
            self.__deltar = float(delta)
        elif delta is not None:
            self.__cutoffr = (int(num) - 1) * float(delta)
            self.__deltar = float(delta)
        elif cutoff is not None:
            self.__cutoffr = float(cutoff)
            self.__deltar = float(cutoff) / (int(num) - 1)
        else:
            raise ValueError('Either or both cutoff and delta are required')

        # Change existing tables to spline functions
        if old_r is not None:
            if self.__rho_r_table is not None:
                self.set_rho_r(table=self.rho_r(), r=old_r)
            if self.__rphi_r_table is not None:
                self.set_rphi_r(table=self.rphi_r(), r=old_r)
            elif self.__phi_r_table is not None:
                self.set_phi_r(table=self.phi_r(), r=old_r)
            elif self.__z_r_table is not None:
                self.set_z_r(table=self.z_r(), r=old_r)

    @property
    def numrho(self) -> int:
        """int : The number of rho values"""
        return self.__numrho

    @property
    def cutoffrho(self) -> float:
        """float : The cutoff rho value"""
        return self.__cutoffrho
    
    @property
    def deltarho(self) -> float:
        """float : The step size between the rho values"""
        return self.__deltarho

    @property
    def rho(self) -> np.ndarray:
        """numpy.NDArray : The rho values associated with the tabulated functions"""
        try:
            self.numrho
        except:
            raise AttributeError('rho values not set: use set_rho()')
        return np.linspace(0, self.numrho * self.deltarho, self.numrho, endpoint=False)
    
    def set_rho(self,
                num: Optional[int] = None,
                cutoff: Optional[float] = None,
                delta: Optional[float] = None):
        """
        Sets the rho values to use for tabulation.

        Parameters
        ----------
        num : int, optional
            The number of rho values for which F(rho) should be
            tabulated. 
        cutoff : float, optional
            The cutoff rho value to use. If not given, will be set as 
            (num - 1) * delta.
        delta : float, optional
            The rho step size to use for the tabulation.  If not given, will
            be set as cutoff / (num - 1).
        """
        # Get current rho values if they exist
        try:
            old_rho = self.rho
        except:
            old_rho = None

        self.__numrho = int(num)

        if cutoff is not None and delta is not None:
            self.__cutoffrho = float(cutoff)
            self.__deltarho = float(delta)
        elif delta is not None:
            self.__cutoffrho = (int(num) - 1) * float(delta)
            self.__deltarho = float(delta)
        elif cutoff is not None:
            self.__cutoffrho = float(cutoff)
            self.__deltarho = float(cutoff) / (int(num) - 1)
        else:
            raise ValueError('Either or both cutoff and delta are required')

        # Change existing tables to spline functions
        if old_rho is not None and self.__F_rho_table is not None:
            self.set_F_rho(table=self.F_rho(), rho=old_rho)

    def symbol_info(self) -> dict:
        """
        Gets the assigned information associated with the potential's symbol
        model.

        Returns
        -------
        dict
            Contains the symbol model values of number, mass, alat and lattice.
        """
        if self.__number is None:
            raise KeyError(f'No info set: use set_symbol_info()')

        return {
            'number': self.__number,
            'mass': self.__mass,
            'alat': self.__alat,
            'lattice': self.__lattice,
        }   

    def set_symbol_info(self,
                        number: int,
                        mass: float,
                        alat: float,
                        lattice: str):
        """
        Sets the information for the potential's symbol model.
        
        Parameters
        ----------
        number : int
            Element number.
        mass : float 
            Particle mass.
        alat : float
            Lattice constant.
        lattice : str
            Lattice type.
        """
            
        self.__number = number
        self.__mass = mass
        self.__alat = alat
        self.__lattice = lattice

    def F_rho(self, rho: Optional[npt.ArrayLike] = None) -> np.ndarray:
        """
        Returns F(rho) values.

        Paramters
        ---------
        rho : array-like, optional
            The value(s) of rho to evaluate F_rho at.  If not given, will
            use the rho values set.

        Returns
        -------
        numpy.ndarray
            The F(rho) values corresponding to the given/set rho values.
        """        
        if self.__F_rho_table is not None:
            if rho is None:
                # Directly return table
                return self.__F_rho_table
            
            else:
                # Build spline of table
                fxn = CubicSpline(self.rho, self.__F_rho_table)
                v = fxn(rho)
                v[np.abs(v) <= 1e-100] = 0.0
                return v
        
        elif self.__F_rho is not None:

            # Set default rho
            if rho is None:
                rho = self.rho
            
            # Evaluate fxn at rho
            fxn = self.__F_rho
            kwargs = self.__F_rho_kwargs
            v = fxn(rho, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            return v    
        
        else:
            raise KeyError(f'F(rho) not set')

    def set_F_rho(self,
                  table: Optional[npt.ArrayLike] = None,
                  rho: Optional[npt.ArrayLike] = None,
                  fxn: Optional[Callable] = None,
                  **kwargs):
        """
        Sets the F(rho) function.
        
        Parameters
        ----------
        table : array-like, optional
            Allows for tabulated F(rho) values to be given.  The function
            will be generated as a cubic spline based on table and rho values.
            Cannot be given with fxn or kwargs.
        rho : array-like, optional
            The rho values to associate with the table values.  If table is
            given and rho is not, then rho is taken as the rho values set.
        fxn : function, optional
            Allows for F_rho to be directly defined as a function.  Cannot
            be given with table or rho.
        **kwargs : any
            Parameter kwargs to pass to fxn when called.  This allows for
            a general fxn to be used with symbol-specific parameters passed in.
        """
        # Set function for tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if rho is None:
                if len(table) != len(self.rho):
                    raise ValueError('Number of table and rho values not the same')

                # Save tabulated values
                self.__F_rho_table = np.asarray(table)
                self.__F_rho = None
                self.__F_rho_kwargs = None

            else:
                
                if len(table) != len(rho):
                    raise ValueError('Number of table and rho values not the same')

                # Build spline using table
                self.__F_rho = CubicSpline(rho, table)
                self.__F_rho_kwargs = {}
                self.__F_rho_table = None
        
        else:
            # Set function and parameters
            self.__F_rho = fxn
            self.__F_rho_kwargs = kwargs
            self.__F_rho_table = None

    def rho_r(self, r: Optional[npt.ArrayLike] = None) -> np.ndarray:
        """
        Returns rho(r) values.

        Paramters
        ---------
        r : array-like, optional
            The value(s) of r to evaluate rho(r) at.  If not given, will
            use the r values set.
        
        Returns
        -------
        numpy.ndarray
            The rho(r) values corresponding to the given/set r values.
        """        
        if self.__rho_r_table is not None:
            if r is None:
                # Directly return table
                return self.__rho_r_table

            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__rho_r_table)
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif self.__rho_r is not None:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__rho_r
            kwargs = self.__rho_r_kwargs
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v
        
        else:
            raise KeyError(f'rho(r) not set')

    def set_rho_r(self,
                  table: Optional[npt.ArrayLike] = None,
                  r: Optional[npt.ArrayLike] = None,
                  fxn: Optional[Callable] = None,
                  **kwargs):
        """
        Sets the rho(r) function.
        
        Parameters
        ----------
        table : array-like, optional
            Allows for tabulated rho(r) values to be given.  The function
            will be generated as a cubic spline based on table and r values.
            Cannot be given with fxn or kwargs.
        r : array-like, optional
            The r values to associate with the table values.  If table is
            given and r is not, then r is taken as the r values set.
        fxn : function, optional
            Allows for rho_r to be directly defined as a function.  Cannot
            be given with table or r.
        **kwargs : any
            Parameter kwargs to pass to fxn when called.  This allows for
            a general fxn to be used with symbol-specific parameters passed in.
        """

        # Handle tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if r is None:
                if len(table) != len(self.r):
                    raise ValueError('Number of table and r values not the same')
                
                # Save tabulated values
                self.__rho_r_table = np.asarray(table)
                self.__rho_r = None
                self.__rho_r_kwargs = None
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__rho_r = CubicSpline(r, table)
                self.__rho_r_kwargs = {}
                self.__rho_r_table = None

        else:
            # Set function and parameters
            self.__rho_r = fxn
            self.__rho_r_kwargs = kwargs
            self.__rho_r_table = None

    def z_r(self, r: Optional[npt.ArrayLike] = None) -> np.ndarray:
        """
        Returns z(r) values.

        Parameters
        ----------
        r : array-like, optional
            The value(s) of r to evaluate z(r) at.  If not given, will
            use the r values set.
        
        Returns
        -------
        numpy.ndarray
            The z(r) values corresponding to the given/set r values.
        """
        
        if self.__z_r_table is not None:
            if r is None:
                # Directly return table
                return self.__z_r_table
            
            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__z_r_table)
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif self.__z_r is not None:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__z_r
            kwargs = self.__z_r_kwargs
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v
        
        elif self.__rphi_r is not None or self.__rphi_r_table is not None:
            
            # Evaluate from rphi_r
            rphi_r = self.rphi_r(r=r)
            return (rphi_r / (self.hartree * self.bohr))**0.5
        
        # Evaluate if phi(r) is set 
        elif self.__phi_r is not None:
            
            # Evaluate from phi_r
            phi_r = self.phi_r(r=r)
            if r is None:
                r = self.r
            rphi_r = r * phi_r
            return (rphi_r / (self.hartree * self.bohr))**0.5

        else:
            raise KeyError(f'Neither z(r), r*phi(r) nor phi(r) set')

    def set_z_r(self,
                table: Optional[npt.ArrayLike] = None,
                r: Optional[npt.ArrayLike] = None,
                fxn: Optional[Callable] = None,
                **kwargs):
        """
        Sets the z(r) function.
        
        Parameters
        ----------
        table : array-like, optional
            Allows for tabulated z(r) values to be given.  The function
            will be generated as a cubic spline based on table and r values.
            Cannot be given with fxn or kwargs.
        r : array-like, optional
            The r values to associate with the table values.  If table is
            given and r is not, then r is taken as the r values set.
        fxn : function, optional
            Allows for z_r to be directly defined as a function.  Cannot
            be given with table or r.
        **kwargs : any
            Parameter kwargs to pass to fxn when called.  This allows for
            a general fxn to be used with symbol-specific parameters passed in.
        """
        # Set function for tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if r is None:
                if len(table) != len(self.r):
                    raise ValueError('Number of table and r values not the same')
                
                # Save tabulated values
                self.__z_r_table = np.asarray(table)
                self.__z_r = None
                self.__z_r_kwargs = None
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__z_r = CubicSpline(r, table)
                self.__z_r_kwargs = {}
                self.__z_r_table = None
        
        else:
            # Set function and parameters
            self.__z_r = fxn
            self.__z_r_kwargs = kwargs
            self.__z_r_table = None

        # Unset rphi_r and phi_r
        self.__rphi_r = None
        self.__rphi_r_kwargs = None
        self.__rphi_r_table = None
        self.__phi_r = None
        self.__phi_r_kwargs = None
        self.__phi_r_table = None

    def rphi_r(self, r: Optional[npt.ArrayLike] = None) -> np.ndarray:
        """
        Returns r*phi(r) values.

        Paramters
        ---------
        r : array-like, optional
            The value(s) of r to evaluate r*phi(r) at.  If not given, will
            use the r values set.
        
        Returns
        -------
        numpy.ndarray
            The r*phi(r) values corresponding to the given/set r values.
        """
        if self.__rphi_r_table is not None:
            if r is None:
                # Directly return table
                return self.__rphi_r_table
            
            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__rphi_r_table)
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif self.__rphi_r is not None:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__rphi_r
            kwargs = self.__rphi_r_kwargs
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v
        
        elif self.__z_r is not None or self.__z_r_table is not None:
            
            # Evaluate from z(r)
            z_r = self.z_r(r=r)
            return self.hartree * self.bohr * z_r * z_r

        elif self.__phi_r is not None:

            # Evaluate from phi(r)
            phi_r = self.phi_r(r=r)
            if r is None:
                r = self.r
            return r * phi_r
        
        else:
            raise KeyError(f'Neither z(r), r*phi(r) nor phi(r) set')

    def set_rphi_r(self,
                   table: Optional[npt.ArrayLike] = None,
                   r: Optional[npt.ArrayLike] = None,
                   fxn: Optional[Callable] = None,
                   **kwargs):
        """
        Sets the r*phi(r) function.
        
        Parameters
        ----------
        table : array-like, optional
            Allows for tabulated r*phi(r) values to be given.  The function
            will be generated as a cubic spline based on table and rho values.
            Cannot be given with fxn or kwargs.
        r : array-like, optional
            The r values to associate with the table values.  If table is
            given and r is not, then r is taken as the r values set.
        fxn : function, optional
            Allows for rphi_r to be directly defined as a function.  Cannot
            be given with table or r.
        **kwargs : any
            Parameter kwargs to pass to fxn when called.  This allows for
            a general fxn to be used with symbol-specific parameters passed in.
        """
        # Set function for tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if r is None:
                if len(table) != len(self.r):
                    raise ValueError('Number of table and r values not the same')
                
                # Save tabulated values
                self.__rphi_r_table = np.asarray(table)
                self.__rphi_r = None
                self.__rphi_r_kwargs = None
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__rphi_r = CubicSpline(r, table)
                self.__rphi_r_kwargs = {}
                self.__rphi_r_table = None
        
        else:
            # Set function and parameters
            self.__rphi_r = fxn
            self.__rphi_r_kwargs = kwargs
            self.__rphi_r_table = None

        # Unset z_r and phi_r
        self.__z_r = None
        self.__z_r_kwargs = None
        self.__z_r_table = None
        self.__phi_r = None
        self.__phi_r_kwargs = None
        self.__phi_r_table = None

    def phi_r(self, r: Optional[npt.ArrayLike] = None) -> np.ndarray:
        """
        Returns phi(r) values.

        Paramters
        ---------
        r : array-like, optional
            The value(s) of r to evaluate phi(r) at.  If not given, will
            use the r values set.
        
        Returns
        -------
        numpy.ndarray
            The phi(r) values corresponding to the given/set r values.
        """
        if self.__phi_r_table is not None:
            if r is None:
                # Directly return table
                return self.__phi_r_table
            
            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__phi_r_table)
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif self.__phi_r is not None:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__phi_r
            kwargs = self.__phi_r_kwargs
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v

        elif self.__z_r is not None or self.__z_r_table is not None:
            
            # Evaluate from z_r
            z_r = self.z_r(r)
            if r is None:
                r = self.r
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=RuntimeWarning)
                return (self.hartree * self.bohr * z_r * z_r) / r
        
        # Evaluate if r*phi(r) is set
        elif self.__rphi_r is not None or self.__rphi_r_table is not None:

            # Evaluate from rphi_r
            rphi_r = self.rphi_r(r=r)
            if r is None:
                r = self.r
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=RuntimeWarning)
                return rphi_r / r
        
        else:
            raise KeyError(f'Neither z(r), r*phi(r) nor phi(r) set')

    def set_phi_r(self,
                  table: Optional[npt.ArrayLike] = None,
                  r: Optional[npt.ArrayLike] = None,
                  fxn: Optional[Callable] = None,
                  **kwargs):
        """
        Sets the phi(r) function.
        
        Parameters
        ----------
        table : array-like, optional
            Allows for tabulated phi(r) values to be given.  The function
            will be generated as a cubic spline based on table and rho values.
            Cannot be given with fxn or kwargs.
        r : array-like, optional
            The r values to associate with the table values.  If table is
            given and r is not, then r is taken as the r values set.
        fxn : function, optional
            Allows for phi_r to be directly defined as a function.  Cannot
            be given with table or r.
        **kwargs : any
            Parameter kwargs to pass to fxn when called.  This allows for
            a general fxn to be used with symbol-specific parameters passed in.
        """
        # Set function for tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if r is None:
                if len(table) != len(self.r):
                    raise ValueError('Number of table and r values not the same')
                
                # Save tabulated values
                self.__phi_r_table = np.asarray(table)
                self.__phi_r = None
                self.__phi_r_kwargs = None
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__phi_r = CubicSpline(r, table)
                self.__phi_r_kwargs = {}
                self.__phi_r_table = None
        
        else:
            # Set function and parameters
            self.__phi_r = fxn
            self.__phi_r_kwargs = kwargs
            self.__phi_r_table = None

        # Unset rphi_r and z_r
        self.__rphi_r = None
        self.__rphi_r_kwargs = None
        self.__rphi_r_table = None
        self.__z_r = None
        self.__z_r_kwargs = None
        self.__z_r_table = None

    def print_overview(self):
        """Prints an overview of set values"""
        print('at#  mass      alat       lat')
        print('{:3} {:7} {:13} {:3}'.format(*self.symbol_info().values()))
        print()
        
        try:
            rho = self.rho
        except:
            print('rho: not set')
        else:
            print('rho:', rho)
        
        try:
            r = self.r
        except:
            print('r: not set')
        else:
            print('r:', r) 

        try:
            F_rho = self.F_rho()
        except:
            print('\nF(rho): not set')
        else:
            print('\nF(rho):', F_rho)
        
        try:
            z_r = self.z_r()
        except:
            print('\nz(r): not set')
        else:
            print('\nz(r):', z_r)

        try:
            rho_r = self.rho_r()
        except:
            print('\nrho(r): not set')
        else:
            print('\nrho(r):', rho_r)

    def load(self, f: Union[str, Path, io.IOBase]):
        """
        Reads in an eam funcfl file
        
        Parameters
        ----------
        f : path-like object or file-like object
            The parameter file to read in, either as a file path or as an open
            file-like object.
        """
        
        if hasattr(f, 'readlines'):
            lines = f.readlines()
        else:
            with open(f) as fp:
                lines = fp.readlines()

        # Read line 1 to header
        self.header = lines[0].strip()

        # Read line 2 for element number, mass, alat and lattice
        terms = lines[1].split()
        number = int(terms[0])
        mass = float(terms[1])
        alat = float(terms[2])
        lattice = str(terms[3])
        self.set_symbol_info(number, mass, alat, lattice)

        # Read line 3 for numrho, deltarho, numr, deltar, and cutoffr
        terms = lines[2].split()
        try:
            assert len(terms) == 5
            numrho =   int(terms[0])
            deltarho = float(terms[1])
            numr =     int(terms[2])
            deltar =   float(terms[3])
            cutoffr =  float(terms[4])
        except:
            print(terms)
            raise ValueError('Invalid potential file (line 5): numrho, deltarho, numr, deltar, cutoffr')
        self.set_r(num=numr, cutoff=cutoffr, delta=deltar)
        self.set_rho(num=numrho, delta=deltarho)

        # Read remaining content as space-delimited terms
        c = 0
        terms = ' '.join(lines[3:]).split()
        expected = self.numrho + 2 * self.numr
        if len(terms) != expected:
            raise ValueError(f'Invalid number of tabulated values')

        # Read F(rho)
        start = c
        end = c + self.numrho
        F_rho_table = np.array(terms[start:end],dtype=float)
        self.set_F_rho(table=F_rho_table)
        c += self.numrho
        
        # Read z(r)
        start = c
        end = c + self.numr
        z_r_table = np.array(terms[start:end],dtype=float)
        self.set_z_r(table=z_r_table)
        c += self.numr    

        # Read rho(r)
        start = c
        end = c + self.numr
        rho_r_table = np.array(terms[start:end], dtype=float)
        self.set_rho_r(table=rho_r_table)

    def build(self,
              f: Union[str, Path, io.IOBase, None] = None,
              xf: str = '%25.16e',
              ncolumns: int = 5) -> Optional[str]:
        """
        Constructs an eam funcfl parameter file.
        
        Parameters
        ----------
        f : str or file-like object, optional
            If given, the contents will be written to the file-like object or file name given by a str.
            If not given, the parameter file contents will be returned as a str.
        xf : str, optional
            The c-style formatter to use for floating point numbers.  Default value is '%25.16e'.
        ncolumns : int, optional
            Indicates how many columns the tabulated values are split by.  Default value is 5.
        
        Returns
        -------
        str
            The parameter file contents (returned if f is not given).
        """

        # Initialize funcfl str
        funcfl = ''

        # Add header
        funcfl = self.header + '\n'

        # Add symbol header
        info = self.symbol_info()
        terms = (info['number'], info['mass'], info['alat'], info['lattice'])
        funcfl += f'%i {xf} {xf} %s\n' % terms

        # Add r and rho header info
        terms = (self.numrho, self.deltarho, self.numr, self.deltar, self.cutoffr)
        funcfl += f'%i {xf} %i {xf} {xf}\n' % terms

        line = []

        # Build array of all values
        vals = np.hstack([self.F_rho(), self.z_r(), self.rho_r()])
        
        # Tabulate values
        for j in range(len(vals)):
            line.append(xf % vals[j])
            
            if (j + 1) % ncolumns == 0:
                funcfl += ' '.join(line) + '\n'
                line = []

        if len(line) > 0:
            funcfl += ' '.join(line) + '\n'
            line = []

        # Save or return
        if f is None:
            return funcfl
        
        elif isinstance(f, str):
            with open(f, 'w') as fp:
                fp.write(funcfl)
        
        elif hasattr(f, 'write'):
            f.write(funcfl)
        
        else:
            raise TypeError('f must be a path or a file-like object')

    def plot_F_rho(self,
                   n: int = 0,
                   figsize: Tuple[float, float] = None,
                   matplotlib_axes: Optional[plt.axes] = None,
                   xlim: Optional[Tuple[float, float]] = None,
                   ylim: Optional[Tuple[float, float]] = None,
                   ) -> Optional[plt.figure]:
        """
        Generates a plot of F(rho) vs. rho.

        Parameters
        ----------
        n : int, optional
            Indicates which derivative of the function to plot.  Default
            value is 0 (no derivative).  Derivatives are computed numerically
            based on the tabulation values.
        figsize : tuple, optional
            The figsize parameter of matplotlib.pyplot.figure to use in
            generating the figure.  Default value is (10, 6).  Ignored if
            matplotlib_axes is given.
        matplotlib_axes : matplotlib.pyplot.axes, optional
            Allows for the plot to be added to an existing plotting axes rather
            than generating a new figure.
        xlim : tuple, optional
            The range of values to plot along the x axis.  If not given will be
            set to (0, max rho). 
        ylim : tuple, optional
            The range of values to plot along the y axis.  If not given will
            use the default pyplot settings.

        Returns
        -------
        matplotlib.pyplot.figure
            The generated figure.  Returned if matplotlib_axes is not given.
        """
        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes
        
        ρ = self.rho
        F = self.F_rho()
        ax1.plot(*numderivative(ρ, F, n=n))
        ax1.set_xlabel('ρ', size='x-large')
        
        if n == 0:
            ylabel = 'F(ρ)'
        elif n == 1:
            ylabel = '∂F(ρ) / ∂ρ'
        else:
            ylabel = f'∂$^{n}$F(ρ) / ∂$ρ^{n}$'
        ax1.set_ylabel(ylabel, size='x-large')
        
        if xlim is None:
            xlim = (0, ρ[-1])
        ax1.set_xlim(xlim)
        
        if ylim is not None:
            ax1.set_ylim(ylim)
        
        if matplotlib_axes is None:
            return fig
        
    def plot_rho_r(self,
                   n: int = 0,
                   figsize: Tuple[float, float] = None,
                   matplotlib_axes: Optional[plt.axes] = None,
                   xlim: Optional[Tuple[float, float]] = None,
                   ylim: Optional[Tuple[float, float]] = None,
                   ) -> Optional[plt.figure]:
        """
        Generates a plot of rho(r) vs. r.

        Parameters
        ----------
        n : int, optional
            Indicates which derivative of the function to plot.  Default
            value is 0 (no derivative).  Derivatives are computed numerically
            based on the tabulation values.
        figsize : tuple, optional
            The figsize parameter of matplotlib.pyplot.figure to use in
            generating the figure.  Default value is (10, 6).  Ignored if
            matplotlib_axes is given.
        matplotlib_axes : matplotlib.pyplot.axes, optional
            Allows for the plot to be added to an existing plotting axes rather
            than generating a new figure.
        xlim : tuple, optional
            The range of values to plot along the x axis.  If not given will be
            set to (0, max r). 
        ylim : tuple, optional
            The range of values to plot along the y axis.  If not given will
            use the default pyplot settings.

        Returns
        -------
        matplotlib.pyplot.figure
            The generated figure.  Returned if matplotlib_axes is not given.
        """
        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes
        
        r = self.r
        ρ = self.rho_r()
        ax1.plot(*numderivative(r, ρ, n=n))
        ax1.set_xlabel('r', size='x-large')
        
        if n == 0:
            ylabel = 'ρ(r)'
        elif n == 1:
            ylabel = '∂ρ(r) / ∂r'
        else:
            ylabel = f'∂$^{n}$ρ(r) / ∂$r^{n}$'
        ax1.set_ylabel(ylabel, size='x-large')
        
        if xlim is None:
            xlim = (0, r[-1])
        ax1.set_xlim(xlim)
        
        if ylim is not None:
            ax1.set_ylim(ylim)
        
        if matplotlib_axes is None:
            return fig
        
    def plot_rphi_r(self,
                    n: int = 0,
                    figsize: Tuple[float, float] = None,
                    matplotlib_axes: Optional[plt.axes] = None,
                    xlim: Optional[Tuple[float, float]] = None,
                    ylim: Optional[Tuple[float, float]] = None,
                    ) -> Optional[plt.figure]:
        """
        Generates a plot of r*phi(r) vs. r.

        Parameters
        ----------
        n : int, optional
            Indicates which derivative of the function to plot.  Default
            value is 0 (no derivative).  Derivatives are computed numerically
            based on the tabulation values.
        figsize : tuple, optional
            The figsize parameter of matplotlib.pyplot.figure to use in
            generating the figure.  Default value is (10, 6).  Ignored if
            matplotlib_axes is given.
        matplotlib_axes : matplotlib.pyplot.axes, optional
            Allows for the plot to be added to an existing plotting axes rather
            than generating a new figure.
        xlim : tuple, optional
            The range of values to plot along the x axis.  If not given will be
            set to (0, max r). 
        ylim : tuple, optional
            The range of values to plot along the y axis.  If not given will
            use the default pyplot settings.

        Returns
        -------
        matplotlib.pyplot.figure
            The generated figure.  Returned if matplotlib_axes is not given.
        """
        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes
        
        r = self.r
        rϕ = self.rphi_r()
        ax1.plot(*numderivative(r, rϕ, n=n))
        ax1.set_xlabel('r', size='x-large')
        
        if n == 0:
            ylabel = 'r*ϕ(r)'
        elif n == 1:
            ylabel = '∂(r*ϕ(r)) / ∂r'
        else:
            ylabel = f'∂$^{n}$(r*ϕ(r)) / ∂$r^{n}$'
        ax1.set_ylabel(ylabel, size='x-large')
        
        if xlim is None:
            xlim = (0, r[-1])
        ax1.set_xlim(xlim)
        
        if ylim is not None:
            ax1.set_ylim(ylim)
        
        if matplotlib_axes is None:
            return fig
        
    def plot_phi_r(self,
                   n: int = 0,
                   figsize: Tuple[float, float] = None,
                   matplotlib_axes: Optional[plt.axes] = None,
                   xlim: Optional[Tuple[float, float]] = None,
                   ylim: Optional[Tuple[float, float]] = None,
                   ) -> Optional[plt.figure]:
        """
        Generates a plot of phi(r) vs. r.

        Parameters
        ----------
        n : int, optional
            Indicates which derivative of the function to plot.  Default
            value is 0 (no derivative).  Derivatives are computed numerically
            based on the tabulation values.
        figsize : tuple, optional
            The figsize parameter of matplotlib.pyplot.figure to use in
            generating the figure.  Default value is (10, 6).  Ignored if
            matplotlib_axes is given.
        matplotlib_axes : matplotlib.pyplot.axes, optional
            Allows for the plot to be added to an existing plotting axes rather
            than generating a new figure.
        xlim : tuple, optional
            The range of values to plot along the x axis.  If not given will be
            set to (0, max r). 
        ylim : tuple, optional
            The range of values to plot along the y axis.  If not given will
            use the default pyplot settings.

        Returns
        -------
        matplotlib.pyplot.figure
            The generated figure.  Returned if matplotlib_axes is not given.
        """
        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes
        
        r = self.r
        ϕ = self.phi_r()
        ax1.plot(*numderivative(r, ϕ, n=n))
        ax1.set_xlabel('r', size='x-large')
        
        if n == 0:
            ylabel = 'ϕ(r)'
        elif n == 1:
            ylabel = '∂ϕ(r) / ∂r'
        else:
            ylabel = f'∂$^{n}$ϕ(r) / ∂$r^{n}$'
        ax1.set_ylabel(ylabel, size='x-large')
        
        if xlim is None:
            xlim = (0, r[-1])
        ax1.set_xlim(xlim)
        
        if ylim is not None:
            ax1.set_ylim(ylim)
        
        if matplotlib_axes is None:
            return fig
        
    def plot_z_r(self, 
                 n: int = 0,
                 figsize: Tuple[float, float] = None,
                 matplotlib_axes: Optional[plt.axes] = None,
                 xlim: Optional[Tuple[float, float]] = None,
                 ylim: Optional[Tuple[float, float]] = None,
                 ) -> Optional[plt.figure]:
        """
        Generates a plot of z(r) vs. r.

        Parameters
        ----------
        n : int, optional
            Indicates which derivative of the function to plot.  Default
            value is 0 (no derivative).  Derivatives are computed numerically
            based on the tabulation values.
        figsize : tuple, optional
            The figsize parameter of matplotlib.pyplot.figure to use in
            generating the figure.  Default value is (10, 6).  Ignored if
            matplotlib_axes is given.
        matplotlib_axes : matplotlib.pyplot.axes, optional
            Allows for the plot to be added to an existing plotting axes rather
            than generating a new figure.
        xlim : tuple, optional
            The range of values to plot along the x axis.  If not given will be
            set to (0, max r). 
        ylim : tuple, optional
            The range of values to plot along the y axis.  If not given will
            use the default pyplot settings.

        Returns
        -------
        matplotlib.pyplot.figure
            The generated figure.  Returned if matplotlib_axes is not given.
        """
        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes
        
        r = self.r
        z = self.z_r()
        ax1.plot(*numderivative(r, z, n=n))
        ax1.set_xlabel('r', size='x-large')
        
        if n == 0:
            ylabel = 'z(r)'
        elif n == 1:
            ylabel = '∂z(r) / ∂r'
        else:
            ylabel = f'∂$^{n}$z(r) / ∂$r^{n}$'
        ax1.set_ylabel(ylabel, size='x-large')
        
        if xlim is None:
            xlim = (0, r[-1])
        ax1.set_xlim(xlim)
        
        if ylim is not None:
            ax1.set_ylim(ylim)
        
        if matplotlib_axes is None:
            return fig