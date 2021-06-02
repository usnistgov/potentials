from ..tools import aslist
from copy import deepcopy
from scipy.interpolate import CubicSpline

import numpy as np

import warnings

class EAM():
    """
    Class for building and analyzing LAMMPS funcfl eam parameter files 
    """
    def __init__(self, filename=None, header=None,
                 number=None, mass=None, alat=None, lattice=None,
                 constants='lammps'):
        """
        Class initializer. Element information can be set at this time.
        
        Parameters
        ----------
        number : int or list, optional
            Element number.  If given, mass, alat and lattice
            must also be given.
        mass : float or list, optional
            Particle mass.  If given, number, alat and lattice
            must also be given.
        alat : float or list, optional
            Lattice constant.  If given, number, mass and lattice
            must also be given.
        lattice : str or list, optional
            Lattice type. If given, number, mass and alat
            must also be given.
        constants : str or tuple, optional
            Specifies the conversion constants to use for Hartree to eV and Bohr
            to Angstroms, which is used for converting z to phi.  Default value
            of "lammps" uses 27.2 and 0.529, respectively, which are what LAMMPS
            itself uses.  "precise" uses higher precision values.  Alternatively,
            a tuple of two floats allows for the constants to be directly
            defined.
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

        if filename is not None:
            self.load(filename)

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
                self.set_symbol(number, mass, alat, lattice)

    @property
    def hartree(self):
        """float: conversion constant from Hartree to eV"""
        return self.__hartree

    @property
    def bohr(self):
        """float: conversion constant from Bohr to Angstrom"""
        return self.__bohr

    @property
    def header(self):
        return self.__header
    
    @header.setter
    def header(self, value):
        if isinstance(value, str):
            value = value.strip()
            if '\n' not in value:
                self.__header = value
            else:
                raise ValueError('header limited to a single line')    
        else:
            raise TypeError('header must be a string')

    @property
    def numr(self):
        """int : The number of r values"""
        return self.__numr

    @property
    def cutoffr(self):
        """float : The cutoff r value"""
        return self.__cutoffr
    
    @property
    def deltar(self):
        """float : The step size between the r values"""
        return self.__deltar

    @property
    def r(self):
        """numpy.NDArray : The r values associated with the tabulated functions"""
        try:
            self.numr
        except:
            raise AttributeError('r values not set: use set_r()')
        return np.linspace(0, self.numr * self.deltar, self.numr, endpoint=False)        

    def set_r(self, num, cutoff=None, delta=None):
        """
        Sets the r values to use for tabulation.

        Parameters
        ----------
        num : int
            The number of r values for which rho(r) and r*phi(r) should be
            tabulated. 
        cutoff : float, optional
            The cutoff r value to use. If not given, will be set as 
            (num - 1) * delta.
        delta : float, optional
            The r step size to use for the tabulation.  If not given, will
            be set as cutoff / (num - 1)
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
    def numrho(self):
        """int : The number of rho values"""
        return self.__numrho

    @property
    def cutoffrho(self):
        """float : The cutoff rho value"""
        return self.__cutoffrho
    
    @property
    def deltarho(self):
        """float : The step size between the rho values"""
        return self.__deltarho

    @property
    def rho(self):
        """numpy.NDArray : The rho values associated with the tabulated functions"""
        try:
            self.numrho
        except:
            raise AttributeError('rho values not set: use set_rho()')
        return np.linspace(0, self.numrho * self.deltarho, self.numrho, endpoint=False)
    
    def set_rho(self, num=None, cutoff=None, delta=None):
        """
        Sets the rho values to use for tabulation.

        Parameters
        ----------
        num : int
            The number of rho values for which F(rho) should be
            tabulated. 
        cutoff : float, optional
            The cutoff rho value to use. If not given, will be set as 
            (num - 1) * delta.
        delta : float, optional
            The rho step size to use for the tabulation.  If not given, will
            be set as cutoff / (num - 1)
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

    def symbol_info(self):
        """
        Gets the assigned information associated with a symbol.
        """
        if self.__number is None:
            raise KeyError(f'No info set: use set_symbol_info()')

        return {
            'number': self.__number,
            'mass': self.__mass,
            'alat': self.__alat,
            'lattice': self.__lattice,
        }   

    def set_symbol_info(self, number, mass, alat, lattice):
        """
        Sets information for symbol model(s).
        
        Parameters
        ----------
        number : int or list, optional
            Element number.
        mass : float or list, optional
            Particle mass.
        alat : float or list, optional
            Lattice constant.
        lattice : str or list, optional
            Lattice type.
        """
            
        self.__number = number
        self.__mass = mass
        self.__alat = alat
        self.__lattice = lattice

    def F_rho(self, rho=None):
        """
        Returns F(rho) values.

        Paramters
        ---------
        rho : array-like, optional
            The value(s) of rho to evaluate F_rho at.  If not given, will
            use the rho values set.
        """        
        # Set default rho
        if rho is None:
            rho = self.rho

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

    def set_F_rho(self, table=None, rho=None, fxn=None, **kwargs):
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

    def rho_r(self, r=None):
        """
        Returns rho(r) values.

        Paramters
        ---------
        r : array-like, optional
            The value(s) of r to evaluate rho(r) at.  If not given, will
            use the r values set.
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
            return v
        
        else:
            raise KeyError(f'rho(r) not set')

    def set_rho_r(self, table=None, r=None, fxn=None, **kwargs):
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

    def z_r(self, r=None):
        """
        Returns z(r) values.

        Parameters
        ----------
        r : array-like, optional
            The value(s) of r to evaluate z(r) at.  If not given, will
            use the r values set.
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

    def set_z_r(self, table=None, r=None, fxn=None, **kwargs):
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

    def rphi_r(self, r=None):
        """
        Returns r*phi(r) values.

        Paramters
        ---------
        r : array-like, optional
            The value(s) of r to evaluate r*phi(r) at.  If not given, will
            use the r values set.
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

    def set_rphi_r(self, table=None, r=None, fxn=None, **kwargs):
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

    def phi_r(self, r=None):
        """
        Returns phi(r) values.

        Paramters
        ---------
        r : array-like, optional
            The value(s) of r to evaluate phi(r) at.  If not given, will
            use the r values set.
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
            return v

        elif self.__z_r is not None:
            
            # Evaluate from z_r
            z_r = self.z_r(r)
            if r is None:
                r = self.r
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=RuntimeWarning)
                return (self.hartree * self.bohr * z_r * z_r) / r
        
        # Evaluate if r*phi(r) is set
        elif self.__rphi_r is not None:

            # Evaluate from rphi_r
            rphi_r = self.rphi_r(r=r)
            if r is None:
                r = self.r
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=RuntimeWarning)
                return rphi_r / r
        
        else:
            raise KeyError(f'Neither z(r), r*phi(r) nor phi(r) set')

    def set_phi_r(self, table=None, r=None, fxn=None, **kwargs):
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

    def load(self, f):
        """Reads in an eam funcfl file"""
        
        if hasattr(f, 'readlines'):
            lines = f.readlines()
        else:
            with open(f) as fp:
                lines = fp.readlines()

        # Read line 1 to header
        header = lines[0].strip()

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