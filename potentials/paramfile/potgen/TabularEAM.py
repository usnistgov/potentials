import numpy as np

from .tools import get_atomicsymbol, aslist
import warnings

class TabularEAM():
    """
    Class for reading/writing eam funcfl and setfl formatted parameter files
    """
    def __init__(self, f=None, style=None, 
                 number=None, mass=None, alat=None, lattice=None,
                 F_rho=None, rho_r=None, rphi_r=None, phi_r=None, z_r=None, 
                 numrho=None, deltarho=None, cutoffrho=None,
                 numr=None, deltar=None, cutoffr=None): 
        """
        Class initializer.
        
        Parameters
        ----------
        f : str or file-like object
            The filename or file object to read.
        style : str, optional
            The eam style of the file being read in.  If not given, will attempt to
            determine it.  More informative error messages will be raised if eamstyle
            is given.        
        """
        if f is not None:
            try:
                assert F_rho is None
                assert rho_r is None
                assert rphi_r is None
                assert phi_r is None
                assert z_r is None
                assert numrho is None
                assert deltarho is None
                assert cutoffrho is None
                assert numr is None
                assert deltar is None
                assert cutoffr is None
            except:
                raise ValueError('f cannot be given with parameter values')      
        
            self.read(f, style=style)
        else:
            self.define(style=style, F_rho=F_rho, rho_r=rho_r,
                        number=number, mass=mass, alat=alat, lattice=lattice,
                        rphi_r=rphi_r, phi_r=phi_r, z_r=z_r, 
                        numrho=numrho, deltarho=deltarho, cutoffrho=cutoffrho,
                        numr=numr, deltar=deltar, cutoffr=cutoffr)
    
    @property
    def supported_styles(self):
        """list : The eam styles supported by this class"""
        return ['eam', 'eam/alloy', 'eam/fs']
    
    @property
    def style(self):
        """str : The eam style for the file read in"""
        return self.__style
    
    @property
    def numrho(self):
        """int : The number of rho values used to tabulate F_rho"""
        return self.__numrho
    
    @property
    def deltarho(self):
        """float : The rho step size used to tabulate F_rho"""
        return self.__deltarho
    
    @property
    def numr(self):
        """int : The number of r values used to tabulate rho_r, phi_r, rphi_r and z_r"""
        return self.__numrho
    
    @property
    def deltar(self):
        """float : The r step size used to tabulate rho_r, phi_r, rphi_r and z_r"""
        return self.__deltar
    
    @property
    def cutoffr(self):
        """float : The maximum cutoff value of r"""
        return self.__cutoffr
    
    @property
    def header(self):
        """str or dict : The comment header(s) for the files.  Is str for styles eam/alloy and eam/fs, dict for style eam"""
        return self.__header
    
    @property
    def symbols(self):
        """list : The list of element model symbols"""
        return self.__symbols
    
    @property
    def number(self):
        return self.__number
    
    @property
    def mass(self):
        return self.__mass
    
    @property
    def alat(self):
        return self.__alat
    
    @property
    def lattice(self):
        return self.__lattice
    
    @property
    def rho(self):
        """numpy.NDArray : The rho values corresponding to the tabulated F_rho values"""
        return np.linspace(0, self.numrho * self.deltarho, self.numrho, endpoint=False)
    
    @property
    def r(self):
        """numpy.NDArray : The r values corresponding to the tabulated rho_r, phi_r, rphi_r and z_r values"""
        return np.linspace(0, self.numr * self.deltar, self.numr, endpoint=False)        
    
    def F_rho(self, symbol=None):
        """
        Returns the tabulated embedding energy values.
        
        Paramters
        ---------
        symbol : str, optional
            The symbol model to retrieve the F_rho tabulated values for. Optional
            if the file is for an elemental potential (only 1 symbol).
        """
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('symbol must be given to identify the interaction')
        
        if symbol not in self.symbols:
            raise ValueError(f'No symbol model {symbol} found')
        
        return self.__F_table[symbol]
        
    def rho_r(self, symbol=None):
        """
        Returns the tabulated electron density values.
        
        Paramters
        ---------
        symbol : str or list, optional
            The symbol model(s) to retrieve rho_r tabulated values for.  The eam and eam/alloy
            formats assign rho_r on a per-element basis, so only one unique symbol can be given.
            The eam/fs format assigns rho_r on a pair basis, so two symbols can be given.  If only
            1 symbol is given for eam/fs, then the self pair interaction is returned.  Optional
            if the file is for an elemental potential (only 1 symbol).
        """
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('symbol must be given to identify the interaction')
        
        symbol = aslist(symbol)
        for s in symbol:        
            if s not in self.symbols:
                raise ValueError(f'No symbol model {s} found')
            
        if self.style == 'eam/fs':
            if len(symbol) == 1:
                symbol = 2 * symbol
            elif len(symbol) != 2:
                raise ValueError('Invalid number of symbol models given: must be 1 or 2')
            symbolstr = '-'.join(symbol)
            
            return self.__rho_table[symbolstr]
        
        else:
            if len(symbol) == 2:
                if symbol[0] == symbol[1]:
                    symbol = symbol[0]
                else:
                    raise ValueError('style does not support rho for two different elements')
            elif len(symbol) == 1:
                symbol = symbol[0]
            else:
                raise ValueError('Invalid number of symbol models given: must be 1 or 2')
                
            return self.__rho_table[symbol]
            
    def z_r(self, symbol=None):
        """
        Returns the tabulated effective charge values.
        
        Paramters
        ---------
        symbol : str or list, optional
            The symbol model to retrieve z_r tabulated values for.  Optional
            if the file is for an elemental potential (only 1 symbol).
        """
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('symbol must be given to identify the interaction')
        
        if symbol not in self.symbols:
            raise ValueError(f'No symbol model {symbol} found')
        
        # Directly return z table for eam style
        if self.style == 'eam':
            return self.__z_table[symbol]
        
        # Convert from rphi table for other styles
        else:
            rphi = self.rphi_r(symbol)
            return (rphi / (27.2 * 0.529))**0.5
    
    def phi_r(self, symbol=None):
        """
        Returns the tabulated pair energy values.
        
        Paramters
        ---------
        symbol : str or list, optional
            The symbol model(s) to retrieve phi_r tabulated values for.  If only
            1 symbol is given then the self pair interaction is returned.  Optional
            if the file is for an elemental potential (only 1 symbol).
        """
        r = self.r
        rphi = self.rphi_r(symbol)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return rphi / r

    def rphi_r(self, symbol=None):
        """
        Returns the tabulated r * pair energy values.
        
        Paramters
        ---------
        symbol : str or list, optional
            The symbol model(s) to retrieve phi_r tabulated values for.  If only
            1 symbol is given then the self pair interaction is returned.  Optional
            if the file is for an elemental potential (only 1 symbol).
        """
        
        if symbol is None:
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
            else:
                raise ValueError('symbol must be given to identify the interaction')
        
        symbol = aslist(symbol)
        for s in symbol:        
            if s not in self.symbols:
                raise ValueError(f'No symbol model {s} found')
            
        if len(symbol) == 1:
            symbol = 2 * symbol
        elif len(symbol) != 2:
            raise ValueError('Invalid number of symbol models given: must be 1 or 2')
        
        if self.style == 'eam':
            #return 27.2 * 0.529 * self.z_r(symbol[0]) * self.z_r(symbol[1])
            return 27.211386245987406 * 0.529177210903 * self.z_r(symbol[0]) * self.z_r(symbol[1])
        else:
            symbolstr = '-'.join(sorted(symbol))
            return self.__rphi_table[symbolstr]    
        
    def read(self, f, eamstyle=None):
        """
        Reads a tabular eam setfl or funcfl formatted file.
        
        Parameters
        ----------
        f : str or file-like object
            The filename or file object to read.
        eamstyle : str, optional
            The eam style of the file being read in.  If not given, will attempt to
            determine it.  More informative error messages will be raised if eamstyle
            is given.        
        """
        
        if eamstyle is None:
            try:
                self.read_setfl(f)
            except:
                try:
                    self.read_funcfl(f)
                except:
                    raise ValueError('Failed to read file as setfl or funcfl.  Try setting eamstyle for more informative errors.')
                    
        elif eamstyle in self.supported_styles:
            
            if eamstyle == 'eam':
                self.read_funcfl(f)
            else:
                self.read_setfl(f, eamstyle)
        else:
            raise ValueError(f'Unsupported eamstyle {eamstyle}')
    
    #def define(self, ):

    def read_funcfl(self, f):
        """
        Reads a funcfl formatted tabular eam parameter file.
        
        Parameters
        ----------
        f : str, file-like object or list of such
            The filename(s) or file object(s) to read.
        """
        
        # Initialize style-dependent class properties
        self.__style = 'eam'
        self.__F_table = {}
        self.__z_table = {}
        self.__rho_table = {}
        self.__symbols = []
        self.__header = {}
        self.__number = {}
        self.__mass = {}
        self.__alat = {}
        self.__lattice = {}
        
        for fi in aslist(f):
        
            if hasattr(fi, 'readlines'):
                lines = fi.readlines()
            else:
                with open(fi) as fp:
                    lines = fp.readlines()

            # Read line 1 to header
            header = lines[0].strip()

            # Read line 2 for element number, mass, alat and lattice
            terms = lines[1].split()
            try:
                assert len(terms) == 4
                number = int(terms[0].strip())
                symbol = get_atomicsymbol(number)
                self.__symbols.append(symbol)
                
                self.__header[symbol] = header
                self.__number[symbol] = number
                self.__mass[symbol] = float(terms[1].strip())
                self.__alat[symbol] = float(terms[2].strip())
                self.__lattice[symbol] = terms[3].strip()
            except:
                print(terms)
                raise ValueError('Invalid funcfl file (line 2): atomic number, atomic mass, lattice parameter, lattice type')

            # Read line 3 for numrho, deltarho, numr, deltar, and cutoffr
            terms = lines[2].split()
            try:
                assert len(terms) == 5
                self.__numrho = int(terms[0])
                self.__deltarho = float(terms[1])
                self.__numr = int(terms[2])
                self.__deltar = float(terms[3])
                self.__cutoffr = float(terms[4])
            except:
                print(terms)
                raise ValueError('Invalid funcfl file (line 3): numrho, deltarho, numr, deltar, cutoffr')

            # Break remaining data into terms
            terms = ' '.join(lines[3:]).split()
            nterms = len(terms)
            expected_nterms = self.numrho + 2 * self.numr
            if nterms != expected_nterms:
                raise ValueError(f'Expected {expected_nterms} terms, found {nterms}')

            self.__F_table[symbol] = np.array(terms[:self.numrho], dtype=float)
            self.__z_table[symbol] = np.array(terms[self.numrho: self.numrho + self.numr], dtype=float)
            self.__rho_table[symbol] = np.array(terms[self.numrho + self.numr:], dtype=float)

    def read_setfl(self, f, eamstyle=None):
        raise NotImplementedError('asfd')

    def write_funcfl(self, f=None, header='', symbol=None, xf='%25.16e'):
        raise NotImplementedError('asfd')

    def write_setfl(self, f=None, header='', style=None, symbols=None, xf='%25.16e'):

    
        # Set/check style
        if style is None:
            if self.style == 'eam':
                style = 'eam/alloy'
            else:
                style = self.style
            assert style in ['eam/alloy', 'eam/fs']
        
        # Add space to xf
        xfs = xf + ' '
                
        # Add header to content
        test = header.split('\n')
        if len(test) <= 3:
            header = header + '\n'*(3-len(test))
        else:
            raise ValueError('header limited to three lines')    
        content = header +'\n'
        
        # Identify the symbol models included
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)
            for symbol in symbols:
                if symbol not in self.symbols:
                    raise ValueError(f'No symbol model {symbol} found')
        content += f'{len(symbols)} {" ".join(symbols)}\n'
            
        content += f'{self.numrho} {self.deltarho:e} {self.numr} {self.deltar:e} {self.cutoffr:e}\n'
        
        for symbol in symbols:
            # Add symbol model header
            content += f'{self.number[symbol]} {self.mass[symbol]} {self.alat[symbol]} {self.lattice[symbol]}\n'

            # Add F(rho) values
            F_rho = self.F_rho(symbol)
            for i in range(self.numrho):
                content += xfs % F_rho[i]
                if i % 5 == 4:
                    content += '\n'
            if i % 5 != 4:
                content += '\n'

            if style == 'eam/alloy':
                # Add rho(r) on a per-symbol basis
                rho_r = self.rho_r(symbol)
                for i in range(self.numr):
                    content += xfs % rho_r[i]
                    if i % 5 == 4:
                        content += '\n'
                if i % 5 != 4:
                    content += '\n'
            
            elif style == 'eam/fs':
                # Add rho(r) on a symbol pair basis
                for symbol2 in symbols:
                    syms = [symbol, symbol2]
                    rho_r = self.rho_r(syms)
                    for i in range(self.numr):
                        content += xfs % rho_r[i]
                        if i % 5 == 4:
                            content += '\n'
                    if i % 5 != 4:
                        content += '\n'
        
        # Add r*phi(r) values
        for j in range(len(symbols)):
            for k in range(0, j+1):
                rphi_r = self.rphi_r([symbols[j], symbols[k]])
                for i in range(self.numr):
                    content += xfs % rphi_r[i]
                    if i % 5 == 4:
                        content += '\n'
                if i % 5 != 4:
                    content += '\n'

        if f is None:
            return content
        else:
            with open(f, 'w') as fp:
                fp.write(content)