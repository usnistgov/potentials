# coding: utf-8
# Standard Python libraries
import sys
from pathlib import Path
import warnings

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://requests.readthedocs.io/en/master/
import requests

# atomman imports
from .tools import atomic_mass, aslist, uber_open_rmode
from . import Artifact

class BasePotentialLAMMPS():
    """
    Base parent class for PotentialLAMMPS objects
    """
    def __init__(self, model, **kwargs):
        """
        Initializes an instance and loads content from a data model.
        
        Parameters
        ----------
        model : str or file-like object
            A JSON/XML data model for the content.
        **kwargs : any, optional
            Any other keyword parameters supported by the child class
        """
        # Check if base class is initialized directly
        self.__module_name = sys.modules[self.__module__].__name__
        if self.__module_name == 'potentials.BasePotentialLAMMPS':
            raise TypeError("Don't use the base class")
        
        # Pass parameters to load
        self.load(model, **kwargs)

    def __str__(self):
        """str: The string of the Potential returns its human-readable id"""
        if self.id is not None:
            return self.id
        else:
            classname = self.__module_name.split('.')[-1]
            return f'Unnamed {classname}'

    @property
    def id(self):
        """str : Human-readable identifier for the LAMMPS implementation."""
        return self._id
    
    @property
    def key(self):
        """str : uuid hash-key for the LAMMPS implementation."""
        return self._key
    
    @property
    def potid(self):
        """str : Human-readable identifier for the potential model."""
        return self._potid
    
    @property
    def potkey(self):
        """str : uuid hash-key for the potential model."""
        return self._potkey
    
    @property
    def units(self):
        """str : LAMMPS units option."""
        return self._units
    
    @property
    def atom_style(self):
        """str : LAMMPS atom_style option."""
        return self._atom_style
    
    @property
    def symbols(self):
        """list of str : All atom-model symbols."""
        return self._symbols
    
    @property
    def pair_style(self):
        return self._pair_style
    
    @property
    def allsymbols(self):
        """bool : indicates if all model symbols must be listed."""
        return self._allsymbols

    @property
    def status(self):
        """str : Indicates the status of the implementation (active, superseded, retracted)"""
        return self._status

    @property
    def model(self):
        """DataModelDict.DataModelDict : The loaded data model content"""
        return self.__model

    @property
    def modelroot(self):
        """str : The root element for the associated data model"""
        raise NotImplementedError("Not defined for the base class")


    def load(self, model, **kwargs):
        """
        Loads data model info associated with a LAMMPS potential.
        
        Parameters
        ----------
        model : str or file-like object
            A JSON/XML data model for the content.
        **kwargs : any, optional
            Any other keyword parameters supported by the child class
        """
        # Load model and find model root
        self.__model = DM(model).find(self.modelroot)

        self._id = self.model['id']
        self._key = self.model['key']
        try:
            self._potid = self.model['potential']['id']
        except:
            self._potid = None
        try:
            self._potkey = self.model['potential']['key']
        except:
            self._potkey = None
        self._units = self.model.get('units', 'metal')
        self._atom_style = self.model.get('atom_style', 'atomic')
        try:
            self._pair_style = self.model['pair_style']['type']
        except:
            self._pair_style = None

        allsymbols = self.model.get('allsymbols', False)
        if isinstance(allsymbols, bool):
            self._allsymbols = allsymbols
        elif allsymbols.lower() == 'true':
            self._allsymbols = True
        elif allsymbols.lower() == 'false':
            self._allsymbols = False
        else:
            raise ValueError(f'Invalid allsymbols value "{allsymbols}"')

        self._status = self.model.get('status', 'active')

        self._symbols = []
        self._elements = []

    def normalize_symbols(self, symbols):
        """
        Modifies a given list of symbols to be compatible with the potential.
        Mostly, this converts symbols to a list if it is not already one, and
        adds additional symbols if the potential's allsymbols setting is True.

        Parameters
        ----------
        symbols : str or list-like object
            The initial list of symbols
        
        Returns
        -------
        list
            The updated list.
        """
        
        # Convert symbols to a list if needed
        symbols = aslist(symbols)
        
        # Check that all symbols are set
        for symbol in symbols:
            assert symbol is not None, 'symbols list incomplete: found None value'
        
        # Add missing symbols if potential's allsymbols is True
        if self.allsymbols:
            for symbol in self.symbols:
                if symbol not in symbols:
                    symbols.append(symbol)
        
        return symbols

    def elements(self, symbols=None):
        """
        Returns a list of element names associated with atom-model symbols.
        
        Parameters
        ----------
        symbols : list of str, optional
            A list of atom-model symbols.  If None (default), will use all of
            the potential's symbols.
        
        Returns
        -------
        list of str
            The str element symbols corresponding to the atom-model symbols.
        """
        # Return all elements if symbols is None
        if symbols is None:
            return self._elements
        
        # Normalize symbols
        symbols = self.normalize_symbols(symbols)
        
        # Get all matching elements
        elements = []
        for symbol in symbols:
            i = self.symbols.index(symbol)
            elements.append(self._elements[i])
        
        return elements

    def asdict(self):
        """Returns a flat dict of the metadata fields"""
        d = {}
        d['id'] = self.id
        d['key'] = self.key
        d['potid'] = self.potid
        d['potkey'] = self.potkey
        d['units'] = self.units
        d['atom_style'] = self.atom_style
        d['allsymbols'] = self.allsymbols
        d['pair_style'] = self.pair_style
        d['status'] = self.status
        d['symbols'] = self.symbols
        d['elements'] = self.elements()

        return d

    def asmodel(self):
        return DM([(self.modelroot, self.model)])

    def pair_info(self, symbols=None, masses=None, prompt=True):
        """
        Generates the LAMMPS input command lines associated with a KIM
        Potential and a list of atom-model symbols.
        
        Parameters
        ----------
        symbols : list of str, optional
            List of atom-model symbols corresponding to the atom types in a
            system.  If None (default), then all atom-model symbols will
            be included in the order that they are listed in the data model.
        masses : list, optional
            Can be given to override the default symbol-based masses for each
            atom type.  Must be a list of the same length as symbols.  Any
            values of None in the list indicate that the default value be used
            for that atom type.
        prompt : bool, optional
            If True (default), then a screen prompt will appear asking for the isotope
            number if no mass is pre-defined for a symbol and the associated element 
            lacks a single standard atomic/ionic mass.  If False, then an error will
            be raised for these cases instead.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential.
        """
        raise NotImplementedError('Needs to be defined by the child class')

    def pair_data_info(self, filename, pbc, symbols=None, masses=None,
                       atom_style=None, units=None, prompt=True):
        """
        Generates the LAMMPS command lines associated with both a potential
        and reading an atom data file.

        Parameters
        ----------
        filename : path-like object
            The file path to the atom data file for LAMMPS to read in.
        pbc : array-like object
            The three boolean periodic boundary conditions.
        symbols : list of str, optional
            List of atom-model symbols corresponding to the atom types in a
            system.  If None (default), then all atom-model symbols will
            be included in the order that they are listed in the data model.
        masses : list, optional
            Can be given to override the default symbol-based masses for each
            atom type.  Must be a list of the same length as symbols.  Any
            values of None in the list indicate that the default value be used
            for that atom type.
        atom_style : str, optional
            The LAMMPS atom_style setting to use for the output.  If not given,
            will use the default value set for the potential.
        units : str, optional
            The LAMMPS unit setting to use for the output.  If not given,
            will use the default value set for the potential.
        prompt : bool, optional
            If True (default), then a screen prompt will appear asking for the isotope
            number if no mass is pre-defined for a symbol and the associated element 
            lacks a single standard atomic/ionic mass.  If False, then an error will
            be raised for these cases instead.
        
        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential and a data
            file to read.
        """
        raise NotImplementedError('Needs to be defined by the child class')



    def pair_restart_info(self):
        pass