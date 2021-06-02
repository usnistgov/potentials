
import numpy as np
from atomman.tools import aslist

class EamAlloySetflBuilder():
    """
    Class supporting the construction of LAMMPS eam/alloy setfl parameter files     
    """
    
    def __init__(self, symbols=None, numbers=None, masses=None, alats=None, lattices=None):
        """
        Class initializer. Element information can be set at this time.
        
        Parameters
        ----------
        symbols : str or list, optional
            Element symbol(s).  If given, equal numbers of the other parameters must also
            be given.  Alternatively, values can be set after initialization using set_symbols().
        numbers : int or list, optional
            Element number(s).  If given, equal numbers of the other parameters must also
            be given.  Alternatively, values can be set after initialization using set_symbols().
        masses : float or list, optional
            Element mass(es).  If given, equal numbers of the other parameters must also
            be given.  Alternatively, values can be set after initialization using set_symbols().
        alats : float or list, optional
            Element lattice constant(s).  If given, equal numbers of the other parameters must also
            be given.  Alternatively, values can be set after initialization using set_symbols().
        lattices : str or list, optional
            Element lattice type(s).  If given, equal numbers of the other parameters must also
            be given.  Alternatively, values can be set after initialization using set_symbols().
        """
        self.__F_function = {}
        self.__F_kwargs = {}
        self.__rho_function = {}
        self.__rho_kwargs = {}
        self.__phi_r_function = {}
        self.__phi_r_kwargs = {}
        self.__phi_r_mult = {}
        self.__symbol = []
        self.__number = {}
        self.__mass = {}
        self.__alat = {}
        self.__lattice = {}
        
        if symbols is not None:
            try:
                assert numbers is not None
                assert masses is not None
                assert alats is not None
                assert lattices is not None
            except:
                raise ValueError('symbols, numbers, masses, alats, and lattices must all be given or none given')
            
            symbols = aslist(symbols)
            numbers = aslist(numbers)
            masses = aslist(masses)
            alats = aslist(alats)
            lattices = aslist(lattices)
            
            try:
                assert len(numbers) == len(symbols)
                assert len(masses) == len(symbols)
                assert len(alats) == len(symbols)
                assert len(lattices) == len(symbols)
            except:
                raise ValueError('size of symbols, numbers, masses, alats, and lattices must be the same')
                 
            for symbol, number, mass, alat, lattice in zip(symbols, numbers, masses, alats, lattices):
                self.set_symbol(symbol, number, mass, alat, lattice)
            
        else:
            try:
                assert numbers is None
                assert masses is None
                assert alats is None
                assert lattices is None
            except:
                raise ValueError('symbols, numbers, masses, alats, and lattices must all be given or none given')   
            
    def set_symbol(self, symbol, number, mass, alat, lattice):
        """
        Sets element information for a given symbol model.
        
        Parameters
        ----------
        symbol : str
            Element symbol.
        number : int
            Element number.
        mass : float
            Element mass.
        alat : float
            Element lattice constant.
        lattices : str
            Element lattice type.
        """
        
        if symbol not in self.__symbol:
            self.__symbol.append(symbol)
        
        self.__number[symbol] = number
        self.__mass[symbol] = mass
        self.__alat[symbol] = alat
        self.__lattice[symbol] = lattice
    
    def set_F_function(self, symbol, function, **kwargs):
        """
        Sets the F(rho) function for an element symbol.
        
        Parameters
        ----------
        symbol : str
            The element symbol to associate the function with.
        function : function
            The F(rho) function.
        **kwargs : any
            Any additional keyword parameters to pass to the function. 
        """
        self.__F_function[symbol] = function
        self.__F_kwargs[symbol] = kwargs
    
    def set_rho_function(self, symbol, function, **kwargs):
        """
        Sets the rho(r) function for an element symbol.
        
        Parameters
        ----------
        symbol : str
            The element symbol to associate the function with.
        function : function
            The rho(r) function.
        **kwargs : any
            Any additional keyword parameters to pass to the function. 
        """
        self.__rho_function[symbol] = function
        self.__rho_kwargs[symbol] = kwargs
    
    def set_phi_function(self, symbols, function, **kwargs):
        """
        Sets the phi(r) function for a pair of element symbols. 
        
        Parameters
        ----------
        symbols : list
            The two element symbols to associate the function with.
        function : function
            The phi(r) function.
        **kwargs : any
            Any additional keyword parameters to pass to the function. 
        """
        assert len(symbols) == 2
        symbolstr = '-'.join(sorted(symbols))
        self.__phi_r_function[symbolstr] = function
        self.__phi_r_kwargs[symbolstr] = kwargs
        self.__phi_r_mult[symbolstr] = True
    
    def set_phi_r_function(self, symbols, function, **kwargs):
        """
        Sets the r*phi(r) function for a pair of element symbols. 
        
        Parameters
        ----------
        symbols : list
            The two element symbols to associate the function with.
        function : function
            The r*phi(r) function.
        **kwargs : any
            Any additional keyword parameters to pass to the function. 
        """
        assert len(symbols) == 2
        symbolstr = '-'.join(sorted(symbols))
        self.__phi_r_function[symbolstr] = function
        self.__phi_r_kwargs[symbolstr] = kwargs
        self.__phi_r_mult[symbolstr]
        
    def F(self, symbol, rho):
        """
        Returns F(rho) values assoicated with a symbol.
        
        Parameters
        ----------
        symbol : str
            The element symbol associated with the F(rho) function to use.
        rho : float or array-like object
            The rho value(s) to compute F(rho) for.
            
        Returns
        -------
        float or numpy.NDArray
            The F(rho) values
        """
        try:
            function = self.__F_function[symbol]
            kwargs = self.__F_kwargs[symbol]
        except:
            raise KeyError(f'F function not set for {symbol}')
        
        return function(rho, **kwargs)
            
    def rho(self, symbol, r):
        """
        Returns rho(r) values assoicated with a symbol.
        
        Parameters
        ----------
        symbol : str
            The element symbol associated with the rho(r) function to use.
        r : float or array-like object
            The r value(s) to compute rho(r) for.
            
        Returns
        -------
        float or numpy.NDArray
            The rho(r) values
        """
        try:
            function = self.__rho_function[symbol]
            kwargs = self.__rho_kwargs[symbol]
        except:
            raise KeyError(f'rho function not set for {symbol}')
        
        return function(r, **kwargs)
        
    def phi_r(self, symbols, r):
        """
        Returns r*phi(r) values assoicated with a pair of symbols.
        
        Parameters
        ----------
        symbols : list
            The pair of element symbols associated with the r*phi(r) function to use.
        r : float or array-like object
            The r value(s) to compute r*phi(r) for.
            
        Returns
        -------
        float or numpy.NDArray
            The r*phi(r) values
        """
        assert len(symbols) == 2
        symbolstr = '-'.join(sorted(symbols))
        
        try:
            function = self.__phi_r_function[symbolstr]
            kwargs = self.__phi_r_kwargs[symbolstr]
        except:
            raise KeyError(f'phi function not set for {symbols}')
        
        if self.__phi_r_mult:
            return r * function(r, **kwargs)
        else:
            return function(r, **kwargs)
    
    def phi(self, symbols, r):
        """
        Returns phi(r) values assoicated with a pair of symbols.
        
        Parameters
        ----------
        symbols : list
            The pair of element symbols associated with the phi(r) function to use.
        r : float or array-like object
            The r value(s) to compute phi(r) for.
            
        Returns
        -------
        float or numpy.NDArray
            The phi(r) values
        """
        assert len(symbols) == 2
        symbolstr = '-'.join(sorted(symbols))
        
        try:
            function = self.__phi_r_function[symbolstr]
            kwargs = self.__phi_r_kwargs[symbolstr]
        except:
            raise KeyError(f'phi function not set for {symbols}')
        
        if self.__phi_r_mult:
            return function(r, **kwargs)
        else:
            return function(r, **kwargs) / r

    def build(self, numr=10000, cutoffr=6.0, numrho=10000, cutoffrho=500.0,
              header=None, xf='%25.16e', ncolumns=5, outfile=None):
        """
        Constructs a setfl parameter file using the pre-defined symbols and functions.
        
        Parameters
        ----------
        numr : int, optional
            The number of r points to include in the tabulation.  Default value is 10000.
        cutoffr : float, optional
            The largest (cutoff) r value to include in the tabulation.  Default value is 6.0.
        numrho : int, optional
            The number of rho points to include in the tabulation.  Default value is 10000.
        cutoffrho : float, optional
            The largest (cutoff) rho value to include in the tabulation.  Default value is 500.0.
        header : str, optional
            Comments (up to three lines long) to include for the parameter file's header.
        xf : str, optional
            The c-style formatter to use for floating point numbers.  Default value is '%25.16e'.
        ncolumns : int, optional
            Indicates how many columns the tabulated values are split by.  Default value is 5.
        outfile : str or file-like object
            If given, the contents will be written to the file-like object or file name given by a str.
            If not given, the parameter file contents will be returned as a str.
            
        Returns
        -------
        str
            The parameter file contents (returned if outfile is not given).
        """
        nelements = len(self.__symbol)
        if nelements == 0:
            raise ValueError('Must set symbols before building')
        
        # Check header information and use it to start eamdata
        if header is None:
            header = '\n\n\n'
        else:
            header = header.splitlines()
            if len(header) > 3:
                raise ValueError("Header is limited to three lines")
            while len(header) < 3:
                header.append('')
            header = '\n'.join(header)+'\n'
        eamdata = header

        # Add elemental symbol header information
        eamdata += str(nelements)
        for symbol in self.__symbol:
            eamdata += ' ' + symbol
        eamdata += '\n'

        # Generate r and rhobar tables
        r = np.linspace(0, cutoffr, numr)
        rhobar = np.linspace(0, cutoffrho, numrho)

        # Add r and rho header info
        # ([1] terms in tables are deltas)
        eamdata += ('%i '+xf+' %i '+xf+' '+xf+'\n') % (numrho, rhobar[1], numr, r[1], cutoffr)

        line = []
        for symbol in self.__symbol:

            # Per element-symbol header
            eamdata += ('%i '+xf+' '+xf+' %s\n') % (self.__number[symbol], self.__mass[symbol],
                                                    self.__alat[symbol], self.__lattice[symbol])

            # Build F and rho values for symbol
            vals = []
            vals.append(self.F(symbol, rhobar))
            vals.append(self.rho(symbol, r))
            vals = np.hstack(vals)

            # Tabulate values
            for j in range(len(vals)):
                line.append(xf % vals[j])
                
                if (j + 1) % ncolumns == 0:
                    eamdata += ' '.join(line) + '\n'
                    line = []

            if len(line) > 0:
                eamdata += ' '.join(line) + '\n'
                line = []

        # phi*r values
        vals = []
        for i in range(nelements):
            for j in range(i+1):
                symbols = [self.__symbol[i], self.__symbol[j]]
                vals.append(self.phi_r(symbols, r))
        vals = np.hstack(vals)

        # Tabulate values
        for j in range(len(vals)):
            line.append(xf % (vals[j]))
            
            if (j + 1) % ncolumns == 0:
                eamdata += ' '.join(line) + '\n'
                line = []
                
        if len(line) > 0:
            eamdata += ' '.join(line) + '\n'
            line = []

        # Save or display
        if outfile is None:
            return eamdata
        
        elif isinstance(outfile, str):
            with open(outfile, 'w') as f:
                f.write(eamdata)
        
        elif hasattr(outfile, 'write'):
            outfile.write(eamdata)
        
        else:
            raise TypeError('Invalid outfile type')