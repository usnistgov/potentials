from __future__ import print_function, division
from copy import deepcopy
import numpy as np

class EAMsetfl(object):
    """Class for representing an EAM-style potential"""

    def __init__(self, fp=None):
        
        #Set default values
        self.__numr = None
        self.__deltar = None
        self.__numrho = None
        self.__deltarho = None
        self.__symbols = []
        self.__tabularflag = False
        self.header = ''
        self.__style = None
        
        #Read in data from a file
        if fp is not None:
            self.readsetfl(fp)
            
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
    
    def pairvalues(self, symbols, numr=None, deltar=None):
        #Find index for symbol
        try:
            assert len(symbols) == 2
            j = self.symbols.index(symbols[0])
            k = self.symbols.index(symbols[1])
            if j >= k:
                i = sum(range(j+1)) + k
            else:
                i = sum(range(k+1)) + j
        except:
            raise ValueError('invalid symbols')

        #Return tabular data
        if self.__tabularflag:
            if numr is not None: raise ValueError('cannot change numr for tabulated data')
            if deltar is not None: raise ValueError('cannot change deltar for tabulated data')
            return self.__pairtables[i]
        
        else:
            raise ValueError('NOT YET!')
            
    def densityvalues(self, symbols, numr=None, deltar=None):
        #Find index for symbol
        
        if self.style == 'alloy':
            try:
                if isinstance(symbols, (list, tuple)):
                    assert len(symbols) == 1
                    i = self.symbols.index(symbols[0])
                else:
                    i = self.symbols.index(symbols)
            except:
                raise ValueError('invalid symbols')
        elif self.style == 'fs':
            try:
                assert len(symbols) == 2
                j = self.symbols.index(symbols[0])
                k = self.symbols.index(symbols[1])
                i = j*len(self.symbols) + k
            except:
                raise ValueError('invalid symbols')
        
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
    
    def readsetfl(self, f):
        """Reads in an eam/alloy or eam/fs setfl file"""
        
        if hasattr(f, 'readlines'):
            lines = f.readlines()
        else:
            with open(f) as fp:
                lines = fp.readlines()

        #Read lines 1-3 to header
        self.header = ''.join(lines[:3]).strip()

        #Read line 4 for symbols
        self.__symbols = lines[3].split()[1:]
        if len(self.__symbols) != int(lines[3].split()[0]):
            raise ValueError('Invalid potential file (line 4): inconsistent number of element symbols')

        #Read line 5 for numrho, deltarho, numr, deltar, and cutoffr
        terms = lines[4].split()
        if True:
            assert len(terms) == 5
            self.numrho =   int(terms[0])
            self.deltarho = float(terms[1])
            self.numr =     int(terms[2])
            self.deltar =   float(terms[3])
            self.cutoffr =  float(terms[4])
        else:
            print(terms)
            raise ValueError('Invalid potential file (line 5): numrho, deltarho, numr, deltar, cutoffr')

        print(self.numrho, self.deltarho, self.numr, self.deltar, self.cutoffr)
            
        self.__tabularflag = True
        self.__embedtables = []
        self.__densitytables = []
        self.__pairtables = []
        self.__elementinfos = []
                    
        #Break remaining data into terms
        terms = ' '.join(lines[5:]).split()
        print(len(terms))
        
        #Count data to identify style
        nsymbols = len(self.__symbols)
        npairsets = sum(range(1,nsymbols+1))
        datacount = len(terms) - 4 * nsymbols 
        print(nsymbols, npairsets, datacount)
        
        #If number of data points is consistent with the eam/alloy style
        if datacount == nsymbols * (self.numrho + self.numr) + npairsets * self.numr:
            self.style = 'alloy'
            c = 0
            
            #Read per-symbol data
            for i in range(nsymbols):
                self.__elementinfos.append(          terms[c:              c+4])
                self.__embedtables.append(  np.array(terms[c+4:            c+4+self.numrho],           dtype=float))
                self.__densitytables.append(np.array(terms[c+4+self.numrho:c+4+self.numrho+self.numr], dtype=float))
                c += 4 + self.numrho + self.numr
            
            #Read pair data
            for i in range(npairsets):
                self.__pairtables.append(np.array(terms[c:c+self.numr], dtype=float))
                c += self.numr
                
        #If number of data points is consistent with the eam/fs style
        elif datacount == nsymbols * self.numrho + nsymbols**2 * self.numr + npairsets * self.numr:
            self.style = 'fs'
            c = 0
            
            #Read per-symbol data
            for i in range(nsymbols):
                self.__elementinfos.append(          terms[c:  c+4])
                self.__embedtables.append(  np.array(terms[c+4:c+4+self.numrho],      dtype=float))
                c += 4 + self.numrho
                for j in range(nsymbols):
                    self.__densitytables.append(np.array(terms[c:c+self.numr], dtype=float))
                    c += self.numr
            
            #Read pair data
            for i in range(npairsets):
                self.__pairtables.append(np.array(terms[c:c+self.numr], dtype=float))
                c += self.numr