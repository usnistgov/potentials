# coding: utf-8
# Standard libraries
from copy import deepcopy
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
from .EAMAlloy import EAMAlloy
from ..tools import aslist, numderivative
class ADP(EAMAlloy):
    """
    Class for building and analyzing LAMMPS setfl adp parameter files 
    """
    def __init__(self,
                 f: Union[str, Path, io.IOBase, None] = None,
                 header: Optional[str] = None,
                 symbol: Union[str, list, None] = None,
                 number: Union[int, list, None] = None,
                 mass: Union[float, list, None] = None,
                 alat: Union[float, list, None] = None,
                 lattice: Union[str, list, None] = None,
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
            parameter file when generated.  Note that setfl comments are
            limited to three lines.
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

        # Initialize u terms
        self.__u_r = {}
        self.__u_r_kwargs = {}
        self.__u_r_table = {}
        
        # Initialize w terms
        self.__w_r = {}
        self.__w_r_kwargs = {}
        self.__w_r_table = {}
        
        super().__init__(f=f, header=header, symbol=symbol, number=number,
                         mass=mass, alat=alat, lattice=lattice,
                         numr=numr, cutoffr=cutoffr, deltar=deltar,
                         numrho=numrho, cutoffrho=cutoffrho, deltarho=deltarho)

    @property
    def pair_style(self) -> str:
        """The LAMMPS pair_style associated with the class"""
        return 'adp'

    def u_r(self,
            symbol: Optional[str] = None,
            r: Optional[npt.ArrayLike] = None) -> np.ndarray:
        """
        Returns u(r) values for a pair interaction.

        Paramters
        ---------
        symbol : str, optional
            The model symbol(s) associated with the function.  Can be either
            a single symbol for elemental interactions, or a pair of symbols.
            Not required if only one symbol has been set.
        r : array-like, optional
            The value(s) of r to evaluate u(r) at.  If not given, will
            use the r values set.
        
        Returns
        -------
        numpy.ndarray
            The u(r) values corresponding to the given/set r values.
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

        if symbolstr in self.__u_r_table:
            if r is None:
                # Directly return table
                return self.__u_r_table[symbolstr]

            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__u_r_table[symbolstr])
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif symbolstr in self.__u_r:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__u_r[symbolstr]
            kwargs = self.__u_r_kwargs[symbolstr]
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v

        else:
            raise KeyError(f'u(r) not set for {symbolstr}')

    def set_u_r(self,
                symbol: Union[str, list],
                table: Optional[npt.ArrayLike] = None,
                r: Optional[npt.ArrayLike] = None,
                fxn: Optional[Callable] = None,
                **kwargs):
        """
        Sets the u(r) function for a pair interaction.
        
        Parameters
        ----------
        symbol : str or list
            The model symbol(s) to associate the function with.  Can either be
            a single symbol for elemental interactions, or a pair of symbols.
        table : array-like, optional
            Allows for tabulated u(r) values to be given.  Cannot be given
            with fxn or kwargs.
        r : array-like, optional
            The r values to associate with the table values.  If table is
            given and r is not, then r is taken as the r values set.
        fxn : function, optional
            Allows for u_r to be directly defined as a function.  Cannot
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
            if symbol not in self.symbols:
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
                self.__u_r_table[symbolstr] = np.asarray(table)
                if symbolstr in self.__u_r:
                    del self.__u_r[symbolstr]
                    del self.__u_r_kwargs[symbolstr]
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__u_r[symbolstr] = CubicSpline(r, table)
                self.__u_r_kwargs[symbolstr] = {}
                if symbolstr in self.__u_r_table:
                    del self.__u_r_table[symbolstr]

        else:
            # Set function and parameters
            self.__u_r[symbolstr] = fxn
            self.__u_r_kwargs[symbolstr] = kwargs
            if symbolstr in self.__u_r_table:
                del self.__u_r_table[symbolstr]

    def w_r(self,
            symbol: Optional[str] = None,
            r: Optional[npt.ArrayLike] = None) -> np.ndarray:
        """
        Returns w(r) values for a pair interaction.

        Paramters
        ---------
        symbol : str, optional
            The model symbol(s) associated with the function.  Can be either
            a single symbol for elemental interactions, or a pair of symbols.
            Not required if only one symbol has been set.
        r : array-like, optional
            The value(s) of r to evaluate w(r) at.  If not given, will
            use the r values set.
        
        Returns
        -------
        numpy.ndarray
            The w(r) values corresponding to the given/set r values.
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

        if symbolstr in self.__w_r_table:
            if r is None:
                # Directly return table
                return self.__w_r_table[symbolstr]

            else:
                # Build spline of table
                fxn = CubicSpline(self.r, self.__w_r_table[symbolstr])
                v = fxn(r)
                v[np.abs(v) <= 1e-100] = 0.0
                v[r > self.cutoffr] = 0.0
                return v
        
        elif symbolstr in self.__w_r:

            # Set default r
            if r is None:
                r = self.r
            
            # Evaluate fxn at r
            fxn = self.__w_r[symbolstr]
            kwargs = self.__w_r_kwargs[symbolstr]
            v = fxn(r, **kwargs)
            v[np.abs(v) <= 1e-100] = 0.0
            v[r > self.cutoffr] = 0.0
            return v

        else:
            raise KeyError(f'u(r) not set for {symbolstr}')

    def set_w_r(self,
                symbol: Union[str, list],
                table: Optional[npt.ArrayLike] = None,
                r: Optional[npt.ArrayLike] = None,
                fxn: Optional[Callable] = None,
                **kwargs):
        """
        Sets the w(r) function for a pair interaction.
        
        Parameters
        ----------
        symbol : str or list
            The model symbol(s) to associate the function with.  Can either be
            a single symbol for elemental interactions, or a pair of symbols.
        table : array-like, optional
            Allows for tabulated w(r) values to be given.  Cannot be given
            with fxn or kwargs.
        r : array-like, optional
            The r values to associate with the table values.  If table is
            given and r is not, then r is taken as the r values set.
        fxn : function, optional
            Allows for w_r to be directly defined as a function.  Cannot
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
            if symbol not in self.symbols:
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
                self.__w_r_table[symbolstr] = np.asarray(table)
                if symbolstr in self.__w_r:
                    del self.__w_r[symbolstr]
                    del self.__w_r_kwargs[symbolstr]
            
            else:
                if len(table) != len(r):
                    raise ValueError('Number of table and r values not the same')
                
                # Build spline using table
                self.__w_r[symbolstr] = CubicSpline(r, table)
                self.__w_r_kwargs[symbolstr] = {}
                if symbolstr in self.__w_r_table:
                    del self.__w_r_table[symbolstr]

        else:
            # Set function and parameters
            self.__w_r[symbolstr] = fxn
            self.__w_r_kwargs[symbolstr] = kwargs
            if symbolstr in self.__w_r_table:
                del self.__w_r_table[symbolstr]

    def print_overview(self):
        """Prints an overview of set values"""
        super().print_overview()
        
        print('\nu(r):')
        for i in range(len(self.symbols)):
            for j in range(0, i+1):
                symbols = [self.symbols[i], self.symbols[j]]
                try:
                    print(symbols[0], symbols[1], self.u_r(symbols))
                except:
                    print(symbols[0], symbols[1], 'not set')

        print('\nw(r):')
        for i in range(len(self.symbols)):
            for j in range(0, i+1):
                symbols = [self.symbols[i], self.symbols[j]]
                try:
                    print(symbols[0], symbols[1], self.w_r(symbols))
                except:
                    print(symbols[0], symbols[1], 'not set')

    def load(self, f: Union[str, Path, io.IOBase]):
        """
        Reads in an adp setfl file
        
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
        expected = numsymbols * (4 + self.numrho + self.numr) + 3 * numsets * self.numr
        if len(terms) != expected:
            raise ValueError(f'Invalid number of tabulated values: {expected} expected, {len(terms)} found')

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
        
        # Iterate over unique symbol pairs for rphi(r)
        for i in range(nsymbols):
            for j in range(0, i+1):
                symbolpair = [symbols[i], symbols[j]]

                # Read pair data
                start = c
                end = c + self.numr
                rphi_r_table = np.array(terms[start:end], dtype=float)
                self.set_rphi_r(symbolpair, table=rphi_r_table)

                c += self.numr

        # Iterate over unique symbol pairs for u(r)
        for i in range(nsymbols):
            for j in range(0, i+1):
                symbolpair = [symbols[i], symbols[j]]

                # Read pair data
                start = c
                end = c + self.numr
                u_r_table = np.array(terms[start:end], dtype=float)
                self.set_u_r(symbolpair, table=u_r_table)

                c += self.numr

        # Iterate over unique symbol pairs for w(r)
        for i in range(nsymbols):
            for j in range(0, i+1):
                symbolpair = [symbols[i], symbols[j]]

                # Read pair data
                start = c
                end = c + self.numr
                w_r_table = np.array(terms[start:end], dtype=float)
                self.set_w_r(symbolpair, table=w_r_table)

                c += self.numr

    def build(self,
              f: Union[str, Path, io.IOBase, None] = None,
              xf: str = '%25.16e',
              ncolumns: int = 5) -> Optional[str]:
        """
        Constructs an adp setfl parameter file.
        
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
                vals.append(self.rphi_r(symbolpair))

        # Build array of all u(r) values
        for i in range(nsymbols):
            for j in range(i+1):
                symbolpair = [self.symbols[i], self.symbols[j]]
                vals.append(self.u_r(symbolpair))

        # Build array of all w(r) values
        for i in range(nsymbols):
            for j in range(i+1):
                symbolpair = [self.symbols[i], self.symbols[j]]
                vals.append(self.w_r(symbolpair))
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
        
    def plot_u_r(self,
                 symbols: Union[str, list, None] = None,
                 n: int = 0,
                 figsize: Tuple[float, float] = None,
                 matplotlib_axes: Optional[plt.axes] = None,
                 xlim: Optional[Tuple[float, float]] = None,
                 ylim: Optional[Tuple[float, float]] = None,
                 ) -> Optional[plt.figure]:
        """
        Generates a plot of u(r) vs. r.

        Parameters
        ----------
        symbols : str or list, optional
            A list of the symbol model pairs to include in the plot.  For each
            pair, the two symbols can be specified as a list or a single symbol
            can be given for the self-interaction.  If no value is given, all
            u(r) functions will be plotted.
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
            u = self.u_r(symbol)
            ax1.plot(*numderivative(r, u, n=n), label='-'.join(symbol))
        ax1.set_xlabel('r', size='x-large')
        
        if len(symbols) > 1:
            ax1.legend()

        if n == 0:
            ylabel = 'u(r)'
        elif n == 1:
            ylabel = '∂(u(r)) / ∂r'
        else:
            ylabel = f'∂$^{n}$(u(r)) / ∂$r^{n}$'
        ax1.set_ylabel(ylabel, size='x-large')
        
        if xlim is None:
            xlim = (0, r[-1])
        ax1.set_xlim(xlim)
        
        if ylim is not None:
            ax1.set_ylim(ylim)
        
        if matplotlib_axes is None:
            return fig
    
    def plot_w_r(self,
                 symbols: Union[str, list, None] = None,
                 n: int = 0,
                 figsize: Tuple[float, float] = None,
                 matplotlib_axes: Optional[plt.axes] = None,
                 xlim: Optional[Tuple[float, float]] = None,
                 ylim: Optional[Tuple[float, float]] = None,
                 ) -> Optional[plt.figure]:
        """
        Generates a plot of w(r) vs. r.

        Parameters
        ----------
        symbols : str or list, optional
            A list of the symbol model pairs to include in the plot.  For each
            pair, the two symbols can be specified as a list or a single symbol
            can be given for the self-interaction.  If no value is given, all
            w(r) functions will be plotted.
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
            w = self.w_r(symbol)
            ax1.plot(*numderivative(r, w, n=n), label='-'.join(symbol))
        ax1.set_xlabel('r', size='x-large')
        
        if len(symbols) > 1:
            ax1.legend()

        if n == 0:
            ylabel = 'w(r)'
        elif n == 1:
            ylabel = '∂(w(r)) / ∂r'
        else:
            ylabel = f'∂$^{n}$(w(r)) / ∂$r^{n}$'
        ax1.set_ylabel(ylabel, size='x-large')
        
        if xlim is None:
            xlim = (0, r[-1])
        ax1.set_xlim(xlim)
        
        if ylim is not None:
            ax1.set_ylim(ylim)
        
        if matplotlib_axes is None:
            return fig