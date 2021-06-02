from copy import deepcopy
import numpy as np

from .tools import get_atomicsymbol

class EAMfuncfl(object):
    """Class for representing an EAM-style potential"""
    
    def __init__(self, style=None, fp=None):
        
        # Set default values
        self.__numr = None
        self.__deltar = None
        self.__numrho = None
        self.__deltarho = None
        self.__symbols = []
        self.__tabularflag = False
        self.__header = ''
        self.__style = style
        
        #Read in data from a file
        if fp is not None:
            self.readfuncfl(fp)

    @property
    def style(self):
        if self.__style is not None:
            return self.__style
        else:
            raise ValueError('style not set')

    @style.setter
    def style(self, value):
        allowedstyles = ['eam', 'eam/alloy', 'eam/fs']
        if value is None or value in allowedstyles:
            self.__style = value
        else:
            raise ValueError(f'{value} is not a supported style')

    @property
    def symbols(self):
        return deepcopy(self.__symbols)

    @property
    def numr(self):
        if self.__numr is not None:
            return self.__numr
        else:
            raise ValueError('numr not set')

    @numr.setter
    def numr(self, value):
        if not self.__tabularflag:
            try:
                assert value == int(value)
                self.__numr = int(value)
            except:
                raise TypeError('numr must be an integer')
        else:
            raise ValueError('cannot set numr for tabulated data')

    @property
    def numrho(self):
        if self.__numrho is not None:
            return self.__numrho
        else:
            raise ValueError('numrho not set')

    @numrho.setter
    def numrho(self, value):
        if not self.__tabularflag:
            try:
                assert value == int(value)
                self.__numrho = int(value)
            except:
                raise TypeError('numrho must be an integer')
        else:
            raise ValueError('cannot set numrho for tabulated data')
    
    @property
    def deltar(self):
        if self.__deltar is not None:
            return self.__deltar
        else:
            raise ValueError('deltar not set')

    @deltar.setter
    def deltar(self, value):
        if not self.__tabularflag:
            try:
                self.__deltar = float(value)
            except:
                raise TypeError('deltar must be a number')
        else:
            raise ValueError('cannot set deltar for tabulated data')
    
    @property
    def deltarho(self):
        if self.__deltarho is not None:
            return self.__deltarho
        else:
            raise ValueError('deltarho not set')

    @deltarho.setter
    def deltarho(self, value):
        if not self.__tabularflag:
            try:
                self.__deltarho = float(value)
            except:
                raise TypeError('deltarho must be a number')
        else:
            raise ValueError('cannot set deltarho for tabulated data')
    
    @property
    def header(self):
        test = self.__header.split('\n')
        nlines = self.__number_header_lines
        if len(test) <= nlines:
            return self.__header + '\n'*(nlines-len(test))
        else:
            raise ValueError('too many header lines for the style')   

    @header.setter
    def header(self, value):
        if isinstance(value, str):
            test = value.split('\n')
            if len(test) <= self.__number_header_lines:
                self.__header = value
            else:
                raise ValueError('too many header lines for the style')    
        else:
            raise TypeError('header must be a string')
    
    def __number_header_lines(self):
        """Returns the number of allowed header lines for the set style"""
        try:
            assert self.style == 'eam'
        except:
            return 3
        else:
            return 1

    def pairvalues(self, symbols, numr=None, deltar=None):
        # Find index for symbol
        try:
            assert len(symbols) == 2
            j = self.symbols.index(symbols[0])
            k = self.symbols.index(symbols[1])
            i = sum(range(j+1)) + k
        except:
            raise ValueError('invalid symbols')

        # Return tabular data
        if self.__tabularflag:
            if numr is not None: raise ValueError('cannot change numr for tabulated data')
            if deltar is not None: raise ValueError('cannot change deltar for tabulated data')
            return self.__pairtables[i]
        
        else:
            raise ValueError('NOT YET!')
            
    def densityvalues(self, symbols, numr=None, deltar=None):
        # Find index for symbol
        
        if self.style == 'eam/alloy':
            try:
                if isinstance(symbols, (list, tuple)):
                    assert len(symbols) == 1
                    i = self.symbols.index(symbols[0])
                else:
                    i = self.symbols.index(symbols)
            except:
                raise ValueError('invalid symbols')
        elif self.style == 'eam/fs':
            try:
                assert len(symbols) == 2
                j = self.symbols.index(symbols[0])
                k = self.symbols.index(symbols[1])
                i = j*len(self.symbols) + k
            except:
                raise ValueError('invalid symbols')
        elif self.style == 'eam':

        
        #Return tabular data
        if self.__tabularflag:
            if numr is not None: raise ValueError('cannot change numr for tabulated data')
            if deltar is not None: raise ValueError('cannot change deltar for tabulated data')
            return self.__densitytables[i]
        else:
            raise ValueError('NOT YET!')
            
    def embedvalues(self, symbol, numrho=None, deltarho=None):
        #Find index for symbol
        try:
            i = self.symbols.index(symbol)
        except:
            raise ValueError('invalid symbol')
        
        #Return tabular data
        if self.__tabularflag:
            if numrho is not None: raise ValueError('cannot change numrho for tabulated data')
            if deltarho is not None: raise ValueError('cannot change deltarho for tabulated data')
            return self.__embedtables[i]
        
        else:
            raise ValueError('NOT YET!')
        
   
    def rvalues(self, numr=None, deltar=None):
        """Return r values"""
            
        if numr is None:   numr =   self.numr
        if deltar is None: deltar = self.deltar
        return np.linspace(0, numr*deltar, numr, endpoint=False)
            
    def rhovalues(self, numrho=None, deltarho=None):
        """Return r values"""
            
        if numrho is None:   numrho =   self.numrho
        if deltarho is None: deltarho = self.deltarho
        return np.linspace(0, numrho*deltarho, numrho, endpoint=False)
    
    def readfuncfl(self, f):
        """Reads in an eam funcfl file"""
        
        if hasattr(f, 'readlines'):
            lines = f.readlines()
        else:
            with open(f) as fp:
                lines = fp.readlines()

        # Read line 1 to header
        self.header = lines[0].strip()

        # Read line 2 for element number, mass, alat and lattice
        terms = lines[1].split()
        try:
            assert len(terms) == 4
            number = int(terms[0].strip())
            #mass = float(terms[1].strip())
            #alat = float(terms[2].strip())
            #lattice = terms[3].strip()
            self.__symbols = [get_atomicsymbol(number)]
        except:
            print(terms)
            raise ValueError('Invalid potential file (line 2): atomic number, atomic mass, lattice parameter, lattice type')

        # Read line 3 for numrho, deltarho, numr, deltar, and cutoffr
        terms = lines[2].split()
        try:
            assert len(terms) == 5
            self.numrho =   int(terms[0])
            self.deltarho = float(terms[1])
            self.numr =     int(terms[2])
            self.deltar =   float(terms[3])
            self.cutoffr =  float(terms[4])
        except:
            print(terms)
            raise ValueError('Invalid potential file (line 3): numrho, deltarho, numr, deltar, cutoffr')
                    
        # Break remaining data into terms
        terms = ' '.join(lines[3:]).split()
        nterms = len(terms)
        expected_nterms = self.numrho + 2 * self.numr
        if nterms != expected_nterms:
            raise ValueError(f'Expected {expected_nterms} terms, found {nterms}')
        
        self.__style = 'eam'

        self.__embedtables = [np.array(terms[:self.numrho])]
        self.__chargetables = [np.array(terms[self.numrho: self.numrho + self.numr])]
        self.__densitytables = [np.array(terms[self.numrho + self.numr:])]
