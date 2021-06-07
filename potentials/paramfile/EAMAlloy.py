from copy import deepcopy
import warnings

from scipy.interpolate import CubicSpline

import numpy as np

import matplotlib.pyplot as plt

from ..tools import aslist, numderivative
class EAMAlloy():
    """
    Class for building and analyzing LAMMPS setfl eam/alloy parameter files 
    """
    def __init__(self, filename=None, header=None,
                 symbol=None, number=None, mass=None, alat=None, lattice=None,
                 numr=None, cutoffr=None, deltar=None,
                 numrho=None, cutoffrho=None, deltarho=None):
        """
        Class initializer. Element information can be set at this time.
        
        Parameters
        ----------
        symbol : str or list, optional
            Model symbol(s).  Equal numbers of symbol, number, mass, alat and
            lattice must be given.
        number : int or list, optional
            Element number(s).  Equal numbers of symbol, number, mass, alat and
            lattice must be given.
        mass : float or list, optional
            Particle mass(es).  Equal numbers of symbol, number, mass, alat and
            lattice must be given.
        alat : float or list, optional
            Lattice constant(s).  Equal numbers of symbol, number,
            mass, alat and lattice must be given.
        lattice : str or list, optional
            Lattice type(s). Equal numbers of symbol, number, mass,
            alat and lattice must be given.
        """

        # Initialize F terms
        self.__F_rho = {}
        self.__F_rho_kwargs = {}
        self.__F_rho_table = {}
        
        # Initialize rho terms
        self.__rho_r = {}
        self.__rho_r_kwargs = {}
        self.__rho_r_table = {}
        
        # Initialize phi terms
        self.__phi_r = {}
        self.__phi_r_kwargs = {}
        self.__phi_r_table = {}
        self.__rphi_r = {}
        self.__rphi_r_kwargs = {}
        self.__rphi_r_table = {}
        
        # Initialize symbol terms
        self.__symbol = []
        self.__number = {}
        self.__mass = {}
        self.__alat = {}
        self.__lattice = {}

        if filename is not None:
            self.load(filename)

        else:
            # Initialize header
            if header is None:
                header = ''
            self.header = header

            # Set symbol values
            if (symbol is not None or number is not None or mass is not None
                or alat is not None or lattice is not None):
                try:
                    assert symbol is not None
                    assert number is not None
                    assert mass is not None
                    assert alat is not None
                    assert lattice is not None                
                except:
                    raise ValueError('symbols, numbers, masses, alats, and lattices must all be given or none given')
                self.set_symbol_info(symbol, number, mass, alat, lattice)

            # Set r
            if numr is not None:
                self.set_r(num=numr, cutoff=cutoffr, delta=deltar)
            
            # Set rho
            if numrho is not None:
                self.set_rho(num=numrho, cutoff=cutoffrho, delta=deltarho)

    @property
    def pair_style(self):
        """The LAMMPS pair_style associated with the class"""
        return 'eam/alloy'

    @property
    def header(self):
        return self.__header
    
    @header.setter
    def header(self, value):
        if isinstance(value, str):
            test = value.split('\n')
            if len(test) <= 3:
                self.__header = value + '\n'*(3-len(value))
            else:
                raise ValueError('header limited to three lines')    
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
            for symbol in list(self.__rho_r_table.keys()):
                self.set_rho_r(symbol, table=self.rho_r(symbol), r=old_r)
            for symbolstr in list(self.__rphi_r_table.keys()):
                symbols = symbolstr.split('-')
                self.set_rphi_r(symbols, table=self.rphi_r(symbols), r=old_r)
            for symbolstr in list(self.__phi_r_table.keys()):
                symbols = symbolstr.split('-')
                self.set_phi_r(symbols, table=self.phi_r(symbols), r=old_r)

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
        if old_rho is not None:
            for symbol in list(self.__F_rho_table.keys()):
                self.set_F_rho(symbol, table=self.F_rho(symbol), rho=old_rho)

    @property
    def symbols(self):
        """list : The list of symbol models currently set"""
        return deepcopy(self.__symbol)

    def symbol_info(self, symbol=None):
        """
        Gets the assigned information associated with a symbol.
        """
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('Multiple symbols set: specify which one')

        if symbol not in self.symbols:
            raise KeyError(f'No info set for {symbol}: use set_symbol_info()')
        
        return {
            'symbol' : symbol,
            'number': self.__number[symbol],
            'mass': self.__mass[symbol],
            'alat': self.__alat[symbol],
            'lattice': self.__lattice[symbol],
        }

    def set_symbol_info(self, symbol, number, mass, alat, lattice):
        """
        Sets information for symbol model(s).
        
        Parameters
        ----------
        symbol : str or list, optional
            Model symbol(s).  Equal numbers of symbol, number, mass, alat and
            lattice must be given.
        number : int or list, optional
            Element number(s).  Equal numbers of symbol, number, mass, alat and
            lattice must be given.
        mass : float or list, optional
            Particle mass(es).  Equal numbers of symbol, number, mass, alat and
            lattice must be given.
        alat : float or list, optional
            Lattice constant(s).  Equal numbers of symbol, number,
            mass, alat and lattice must be given.
        lattice : str or list, optional
            Lattice type(s). Equal numbers of symbol, number, mass,
            alat and lattice must be given.
        """
        
        # Check that an equal number of all values has been given
        symbol = aslist(symbol)
        number = aslist(number)
        mass = aslist(mass)
        alat = aslist(alat)
        lattice = aslist(lattice)
        assert len(number) == len(symbol)
        assert len(mass) == len(symbol)
        assert len(alat) == len(symbol)
        assert len(lattice) == len(symbol)

        for i in range(len(symbol)):
            if symbol[i] not in self.__symbol:
                self.__symbol.append(symbol[i])
            
            self.__number[symbol[i]] = number[i]
            self.__mass[symbol[i]] = mass[i]
            self.__alat[symbol[i]] = alat[i]
            self.__lattice[symbol[i]] = lattice[i]

    def F_rho(self, symbol=None, rho=None):
        """
        Returns F(rho) values for a given symbol model.

        Paramters
        ---------
        symbol : str, optional
            The model symbol associated with the function.  Not required
            if only one symbol has been set.
        rho : array-like, optional
            The value(s) of rho to evaluate F_rho at.  If not given, will
            use the rho values set.
        """
        # Handle default symbol
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('Multiple symbols set: specify which one')
        
        if symbol in self.__F_rho_table:
            if rho is None:
                # Directly return table
                return self.__F_rho_table[symbol]

            else:
                # Build spline of table
                fxn = CubicSpline(self.rho, self.__F_rho_table[symbol])
                v = fxn(rho)
                v[np.abs(v) <= 1e-100] = 0.0
                return v
        
        elif symbol in self.__F_rho:

            # Set default rho
            if rho is None:
                rho = self.rho
            
            # Evaluate fxn at rho
            fxn = self.__F_rho[symbol]
            kwargs = self.__F_rho_kwargs[symbol]
            v = fxn(rho, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            return v
        
        else:
            raise KeyError(f'F(rho) not set for {symbol}')

    def set_F_rho(self, symbol, table=None, rho=None, fxn=None, **kwargs):
        """
        Sets the F(rho) function for a symbol.
        
        Parameters
        ----------
        symbol : str
            The model symbol to associate the function with.
        table : array-like, optional
            Allows for tabulated F(rho) values to be given.  Cannot be
            given with fxn or kwargs.
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
        # Check that symbol has been set beforehand
        if symbol not in self.symbols:
            raise KeyError(f'No info set for {symbol}: use set_symbol_info()')

        # Handle tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if rho is None:
                if len(table) != len(self.rho):
                    raise ValueError('Number of table and rho values not the same')
                
                # Save tabulated values
                self.__F_rho_table[symbol] = np.asarray(table)
                if symbol in self.__F_rho:
                    del self.__F_rho[symbol]
                    del self.__F_rho_kwargs[symbol]
            
            else:
                if len(table) != len(rho):
                    raise ValueError('Number of table and rho values not the same')
                
                # Build spline using table
                self.__F_rho[symbol] = CubicSpline(rho, table)
                self.__F_rho_kwargs[symbol] = {}
                if symbol in self.__F_rho_table:
                    del self.__F_rho_table[symbol]

        else:
            # Set function and parameters
            self.__F_rho[symbol] = fxn
            self.__F_rho_kwargs[symbol] = kwargs
            if symbol in self.__F_rho_table:
                del self.__F_rho_table[symbol]

    def rho_r(self, symbol=None, r=None):
        """
        Returns rho(r) values for a given symbol model.

        Paramters
        ---------
        symbol : str, optional
            The model symbol associated with the function.  Not required
            if only one symbol has been set.
        r : array-like, optional
            The value(s) of r to evaluate rho(r) at.  If not given, will
            use the r values set.
        """
        # Handle default symbol
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('Multiple symbols set: specify which one')
        
        if symbol in self.__rho_r_table:
            if r is None:
                # Directly return table
                return self.__rho_r_table[symbol]

            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__rho_r_table[symbol])
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif symbol in self.__rho_r:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__rho_r[symbol]
            kwargs = self.__rho_r_kwargs[symbol]
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v
        
        else:
            raise KeyError(f'rho(r) not set for {symbol}')

    def set_rho_r(self, symbol, table=None, r=None, fxn=None, **kwargs):
        """
        Sets the rho(r) function for a symbol.
        
        Parameters
        ----------
        symbol : str
            The model symbol to associate the function with.
        table : array-like, optional
            Allows for tabulated rho(r) values to be given.  Cannot be
            given with fxn or kwargs.
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
        # Check that symbol has been set beforehand
        if symbol not in self.symbols:
            raise KeyError(f'No info set for {symbol}: use set_symbol_info()')

        # Handle tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if r is None:
                if len(table) != len(self.r):
                    raise ValueError('Number of table and r values not the same')
                
                # Save tabulated values
                self.__rho_r_table[symbol] = np.asarray(table)
                if symbol in self.__rho_r:
                    del self.__rho_r[symbol]
                    del self.__rho_r_kwargs[symbol]
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__rho_r[symbol] = CubicSpline(r, table)
                self.__rho_r_kwargs[symbol] = {}
                if symbol in self.__rho_r_table:
                    del self.__rho_r_table[symbol]

        else:
            # Set function and parameters
            self.__rho_r[symbol] = fxn
            self.__rho_r_kwargs[symbol] = kwargs
            if symbol in self.__rho_r_table:
                del self.__rho_r_table[symbol]

    def rphi_r(self, symbol=None, r=None):
        """
        Returns r*phi(r) values for a pair interaction.

        Paramters
        ---------
        symbol : str, optional
            The model symbol(s) associated with the function.  Can be either
            a single symbol for elemental interactions, or a pair of symbols.
            Not required if only one symbol has been set.
        r : array-like, optional
            The value(s) of r to evaluate r*phi(r) at.  If not given, will
            use the r values set.
        """
        # Handle default symbol
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('Multiple symbols set: specify which one')

        symbols = aslist(symbol)
        if len(symbols) == 1:
            symbols = symbols + symbols
        elif len(symbols) != 2:
            raise ValueError('Invalid number of symbols: must be 1 or 2')
        symbolstr = '-'.join(sorted(symbols))

        if symbolstr in self.__rphi_r_table:
            if r is None:
                # Directly return table
                return self.__rphi_r_table[symbolstr]

            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__rphi_r_table[symbolstr])
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif symbolstr in self.__rphi_r:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__rphi_r[symbolstr]
            kwargs = self.__rphi_r_kwargs[symbolstr]
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v
        
        elif symbolstr in self.__phi_r or symbolstr in self.__phi_r_table:

            # Evaluate from phi_r
            phi_r = self.phi_r(symbol, r=r)
            if r is None:
                r = self.r
            return r * phi_r

        else:
            raise KeyError(f'Neither r*phi(r) nor phi(r) set for {symbolstr}')

    def set_rphi_r(self, symbol, table=None, r=None, fxn=None, **kwargs):
        """
        Sets the r*phi(r) function for a pair interaction.
        
        Parameters
        ----------
        symbol : str or list
            The model symbol(s) to associate the function with.  Can either be
            a single symbol for elemental interactions, or a pair of symbols.
        table : array-like, optional
            Allows for tabulated r*phi(r) values to be given.  Cannot be given
            with fxn or kwargs.
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
        symbols = aslist(symbol)
        if len(symbols) == 1:
            symbols = symbols + symbols
        elif len(symbols) != 2:
            raise ValueError('Invalid number of symbols: must be 1 or 2')

        # Check that symbol has been set beforehand
        for symbol in symbols:
            if symbol not in self.__symbol:
                raise KeyError(f'No info set for {symbol}: use set_symbol_info()')
        symbolstr = '-'.join(sorted(symbols))

        # Handle tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if r is None:
                if len(table) != len(self.r):
                    raise ValueError('Number of table and r values not the same')
                
                # Save tabulated values
                self.__rphi_r_table[symbolstr] = np.asarray(table)
                if symbolstr in self.__rphi_r:
                    del self.__rphi_r[symbolstr]
                    del self.__rphi_r_kwargs[symbolstr]
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__rphi_r[symbolstr] = CubicSpline(r, table)
                self.__rphi_r_kwargs[symbolstr] = {}
                if symbolstr in self.__rphi_r_table:
                    del self.__rphi_r_table[symbolstr]

        else:
            # Set function and parameters
            self.__rphi_r[symbolstr] = fxn
            self.__rphi_r_kwargs[symbolstr] = kwargs
            if symbolstr in self.__rphi_r_table:
                del self.__rphi_r_table[symbolstr]

        # Remove fxn from phi_r if it exists
        if symbolstr in self.__phi_r:
            del self.__phi_r[symbolstr]
            del self.__phi_r_kwargs[symbolstr]
        if symbolstr in self.__phi_r_table:
            del self.__phi_r_table[symbolstr]

    def phi_r(self, symbol=None, r=None):
        """
        Returns phi(r) values for a pair interaction.

        Paramters
        ---------
        symbol : str, optional
            The model symbol(s) associated with the function.  Can be either
            a single symbol for elemental interactions, or a pair of symbols.
            Not required if only one symbol has been set.
        r : array-like, optional
            The value(s) of r to evaluate phi(r) at.  If not given, will
            use the r values set.
        """
        # Handle default symbol
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('Multiple symbols set: specify which one')

        symbols = aslist(symbol)
        if len(symbols) == 1:
            symbols = symbols + symbols
        elif len(symbols) != 2:
            raise ValueError('Invalid number of symbols: must be 1 or 2')
        symbolstr = '-'.join(sorted(symbols))
  
        if symbolstr in self.__phi_r_table:
            if r is None:
                # Directly return table
                return self.__phi_r_table[symbolstr]

            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__phi_r_table[symbolstr])
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif symbolstr in self.__phi_r:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__phi_r[symbolstr]
            kwargs = self.__phi_r_kwargs[symbolstr]
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v
        
        elif symbolstr in self.__rphi_r or symbolstr in self.__rphi_r_table:
            
            # Evaluate from rphi_r
            rphi_r = self.rphi_r(symbol, r=r)
            if r is None:
                r = self.r
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=RuntimeWarning)
                return rphi_r / r

        else:
            raise KeyError(f'Neither r*phi(r) nor phi(r) set for {symbolstr}')

    def set_phi_r(self, symbol, table=None, r=None, fxn=None, **kwargs):
        """
        Sets the phi(r) function for a pair interaction.
        
        Parameters
        ----------
        symbol : str or list
            The model symbol(s) to associate the function with.  Can either be
            a single symbol for elemental interactions, or a pair of symbols.
        table : array-like, optional
            Allows for tabulated phi(r) values to be given.  Cannot be given
            with fxn or kwargs.
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
        symbols = aslist(symbol)
        if len(symbols) == 1:
            symbols = symbols + symbols
        elif len(symbols) != 2:
            raise ValueError('Invalid number of symbols: must be 1 or 2')

        # Check that symbol has been set beforehand
        for symbol in symbols:
            if symbol not in self.__symbol:
                raise KeyError(f'No info set for {symbol}: use set_symbol_info()')
        symbolstr = '-'.join(sorted(symbols))

        # Handle tabulated values
        if table is not None:
            if fxn is not None or len(kwargs) > 0:
                raise ValueError('fxn and kwargs cannot be given with table')
            
            if r is None:
                if len(table) != len(self.r):
                    raise ValueError('Number of table and r values not the same')
                
                # Save tabulated values
                self.__phi_r_table[symbolstr] = np.asarray(table)
                if symbolstr in self.__phi_r:
                    del self.__phi_r[symbolstr]
                    del self.__phi_r_kwargs[symbolstr]
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__phi_r[symbolstr] = CubicSpline(r, table)
                self.__phi_r_kwargs[symbolstr] = {}
                if symbolstr in self.__phi_r_table:
                    del self.__phi_r_table[symbolstr]

        else:
            # Set function and parameters
            self.__phi_r[symbolstr] = fxn
            self.__phi_r_kwargs[symbolstr] = kwargs
            if symbolstr in self.__phi_r_table:
                del self.__phi_r_table[symbolstr]

        # Remove fxn from rphi_r if it exists
        if symbolstr in self.__rphi_r:
            del self.__rphi_r[symbolstr]
            del self.__rphi_r_kwargs[symbolstr]
        if symbolstr in self.__rphi_r_table:
            del self.__rphi_r_table[symbolstr]

    def print_overview(self):
        """Prints an overview of set values"""
        print('sym at#  mass      alat       lat')
        for symbol in self.symbols:
            print('{:2} {:3} {:7} {:13} {:3}'.format(*self.symbol_info(symbol).values()))
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

        print('\nF(rho):')
        for symbol in self.symbols:
            try:
                print(symbol, self.F_rho(symbol))
            except:
                print(symbol, 'not set')
        
        print('\nrho(r):')
        for symbol in self.symbols:
            try:
                print(symbol, self.rho_r(symbol))
            except:
                print(symbol, 'not set')
        
        print('\nr*phi(r):')
        for i in range(len(self.symbols)):
            for j in range(0, i+1):
                symbols = [self.symbols[i], self.symbols[j]]
                try:
                    print(symbols[0], symbols[1], self.rphi_r(symbols))
                except:
                    print(symbols[0], symbols[1], 'not set')

    def load(self, f):
        """
        Reads in an eam/alloy setfl file
        
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

        # Read lines 1-3 to header
        self.header = ''.join(lines[:3]).strip()

        # Read line 4 for symbols
        symbols = lines[3].split()[1:]
        nsymbols = len(symbols)
        if nsymbols != int(lines[3].split()[0]):
            raise ValueError('Invalid potential file (line 4): inconsistent number of symbols')

        # Set initial dummy symbols info (replaced later)
        for symbol in symbols:
             self.set_symbol_info(symbol, 0, 0.0, 0.0, 'NA')

        # Read line 5 for numrho, deltarho, numr, deltar, and cutoffr
        terms = lines[4].split()
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
        terms = ' '.join(lines[5:]).split()
        numsymbols = len(self.symbols)
        numsets = sum(range(1, numsymbols+1))
        expected = numsymbols * (4 + self.numrho + self.numr) + numsets * self.numr
        if len(terms) != expected:
            raise ValueError(f'Invalid number of tabulated values')

        # Read per-symbol data
        for symbol in symbols:
            
            # Read symbol info
            number = int(terms[c])
            mass = float(terms[c+1])
            alat = float(terms[c+2])
            lattice = str(terms[c+3])
            self.set_symbol_info(symbol, number, mass, alat, lattice)

            # Read F(rho)
            start = c + 4
            end = c + 4 + self.numrho
            F_rho_table = np.array(terms[start:end],dtype=float)
            self.set_F_rho(symbol, table=F_rho_table)

            # Read rho(r)
            start = c + 4 + self.numrho
            end = c + 4 + self.numrho + self.numr
            rho_r_table = np.array(terms[start:end],dtype=float)
            self.set_rho_r(symbol, table=rho_r_table)
            
            # Increase c
            c += 4 + self.numrho + self.numr
        
        # Iterate over unique symbol pairs
        for i in range(nsymbols):
            for j in range(0, i+1):
                symbolpair = [symbols[i], symbols[j]]

                # Read pair data
                start = c
                end = c + self.numr
                rphi_r_table = np.array(terms[start:end], dtype=float)
                self.set_rphi_r(symbolpair, table=rphi_r_table)

                c += self.numr

    def build(self, f=None, xf='%25.16e', ncolumns=5):
        """
        Constructs an eam/alloy setfl parameter file.
        
        Parameters
        ----------
        f : str or file-like object
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

        # Initialize setfl str
        setfl = ''

        # Add header
        header = self.header.splitlines()
        while len(header) < 3:
            header.append('')
        header = '\n'.join(header)+'\n'
        setfl = header

        # Add symbol header info
        nsymbols = len(self.symbols)
        if nsymbols == 0:
            raise ValueError('No symbols set: no data to write')
        setfl += str(nsymbols)
        for symbol in self.symbols:
            setfl += ' ' + symbol
        setfl += '\n'

        # Add r and rho header info
        terms = (self.numrho, self.deltarho, self.numr, self.deltar, self.cutoffr)
        setfl += f'%i {xf} %i {xf} {xf}\n' % terms

        line = []

        # Loop over symbols
        for symbol in self.symbols:

            # Add symbol header
            info = self.symbol_info(symbol)
            terms = (info['number'], info['mass'], info['alat'], info['lattice'])
            setfl += f'%i {xf} {xf} %s\n' % terms

            # Tabulate F(rho) and rho(r) values
            vals = np.hstack([self.F_rho(symbol), self.rho_r(symbol)])
            for j in range(len(vals)):
                line.append(xf % vals[j])
                
                if (j + 1) % ncolumns == 0:
                    setfl += ' '.join(line) + '\n'
                    line = []

            if len(line) > 0:
                setfl += ' '.join(line) + '\n'
                line = []

        # Build array of all r*phi(r) values
        vals = []
        for i in range(nsymbols):
            for j in range(i+1):
                symbolpair = [self.symbols[i], self.symbols[j]]
                vals.append(self.phi_r(symbolpair))
        vals = np.hstack(vals)

        # Tabulate values
        for j in range(len(vals)):
            line.append(xf % (vals[j]))
            
            if (j + 1) % ncolumns == 0:
                setfl += ' '.join(line) + '\n'
                line = []
                
        if len(line) > 0:
            setfl += ' '.join(line) + '\n'
            line = []

        # Save or return
        if f is None:
            return setfl
        
        elif isinstance(f, str):
            with open(f, 'w') as fp:
                fp.write(setfl)
        
        elif hasattr(f, 'write'):
            f.write(setfl)
        
        else:
            raise TypeError('f must be a path or a file-like object')

    def plot_F_rho(self, symbols=None, n=0, figsize=None, matplotlib_axes=None,
                   xlim=None, ylim=None):

        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes
        
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)
        ρ = self.rho

        for symbol in symbols:
            F = self.F_rho(symbol)
            ax1.plot(*numderivative(ρ, F, n=n), label=symbol)
        
        if len(symbols) > 1:
            ax1.legend()
        
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

    def plot_rho_r(self, symbols=None, n=0, figsize=None, matplotlib_axes=None,
                   xlim=None, ylim=None):

        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes

        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)
        r = self.r

        for symbol in symbols:
            ρ = self.rho_r(symbol)
            ax1.plot(*numderivative(r, ρ, n=n), label=symbol)

        if len(symbols) > 1:
            ax1.legend()

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
        
    def plot_rphi_r(self, symbols=None, n=0, figsize=None, matplotlib_axes=None,
                    xlim=None, ylim=None):

        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes
        
        if symbols is None:
            symbols = []
            for i in range(len(self.symbols)):
                for j in range(0, i+1):
                    symbols.append([self.symbols[i], self.symbols[j]])
        else:
            symbols = aslist(symbols)
        r = self.r

        for symbol in symbols:
            symbol = aslist(symbol)
            if len(symbol) == 1:
                symbol += symbol
            rϕ = self.rphi_r(symbol)
            ax1.plot(*numderivative(r, rϕ, n=n), label='-'.join(symbol))
        ax1.set_xlabel('r', size='x-large')
        
        if len(symbols) > 1:
            ax1.legend()

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
        
    def plot_phi_r(self, symbols=None, n=0, figsize=None, matplotlib_axes=None,
                   xlim=None, ylim=None):

        # Initial plot setup and parameters
        if matplotlib_axes is None:
            if figsize is None:
                figsize = (10, 6)
            fig = plt.figure(figsize=figsize, dpi=72)
            ax1 = fig.add_subplot(111)
        else:
            ax1 = matplotlib_axes
        
        if symbols is None:
            symbols = []
            for i in range(len(self.symbols)):
                for j in range(0, i+1):
                    symbols.append([self.symbols[i], self.symbols[j]])
        else:
            symbols = aslist(symbols)
        r = self.r

        for symbol in symbols:
            symbol = aslist(symbol)
            if len(symbol) == 1:
                symbol += symbol
            rϕ = self.phi_r(symbol)
            ax1.plot(*numderivative(r, rϕ, n=n), label='-'.join(symbol))
        ax1.set_xlabel('r', size='x-large')
        
        if len(symbols) > 1:
            ax1.legend()

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