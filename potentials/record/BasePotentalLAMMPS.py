# coding: utf-8
# Standard Python libraries
import sys
from pathlib import Path

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from datamodelbase.record import Record
from datamodelbase import query

# atomman imports
from ..tools import aslist

class BasePotentialLAMMPS(Record):
    """
    Base parent class for PotentialLAMMPS objects
    """
    def __init__(self, model, name=None, **kwargs):
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
        if self.__module__ == __name__:
            raise TypeError("Don't use base class")
        
        # Pass parameters to load
        self.load_model(model, name=name, **kwargs)

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
    def pot_dir(self):
        """str : The directory containing files associated with a given potential."""
        return self.__pot_dir
    
    @pot_dir.setter
    def pot_dir(self, value):
        self.__pot_dir = str(value)

    @property
    def artifacts(self):
        """list : The list of file artifacts for the potential including download URLs."""
        return self.__artifacts

    def download_files(self, pot_dir=None, overwrite=False, verbose=False):
        """
        Downloads all artifact files associated with the potential.  The files
        will be saved to the pot_dir directory.

        Parameters
        ----------
        pot_dir : str, optional
            The path to the directory where the files are to be saved.  If not
            given, will use whatever pot_dir value was previously set.  If
            given here, will change the pot_dir value so that the pair_info
            lines properly point to the downloaded files.
        overwrite : bool, optional
            If False (default), then the files will not be downloaded if
            similarly named files already exist in the pot_dir.
        verbose : bool, optional
            If True, info statements will be printed.  Default
            value is False.
        
        Returns
        -------
        num_downloaded : int
            The number of artifacts downloaded.
        num_skipped : int
            The number of artifacts not downloaded.
        """
        
        if pot_dir is not None:
            self.pot_dir = pot_dir
        
        num_downloaded = 0
        num_skipped = 0
        if len(self.artifacts) > 0:
            if not Path(self.pot_dir).is_dir():
                Path(self.pot_dir).mkdir(parents=True)

            for artifact in self.artifacts:
                success = artifact.download(self.pot_dir, overwrite=overwrite,
                                            verbose=verbose)
                if success:
                    num_downloaded += 1
                else:
                    num_skipped += 1

        return num_downloaded, num_skipped

    def load_model(self, model, name=None, **kwargs):
        """
        Loads data model info associated with a LAMMPS potential.
        
        Parameters
        ----------
        model : str or file-like object
            A JSON/XML data model for the content.
        **kwargs : any, optional
            Any other keyword parameters supported by the child class
        """
        # Load model
        super().load_model(model, name=name)

        # Extract values from model
        pot = self.model[self.modelroot]

        self._id = pot['id']
        try:
            self.name
        except:
            self.name = self.id

        self._key = pot['key']
        try:
            self._potid = pot['potential']['id']
        except:
            self._potid = None
        try:
            self._potkey = pot['potential']['key']
        except:
            self._potkey = None
        self._units = pot.get('units', 'metal')
        self._atom_style = pot.get('atom_style', 'atomic')
        try:
            self._pair_style = pot['pair_style']['type']
        except:
            self._pair_style = None

        allsymbols = pot.get('allsymbols', False)
        if isinstance(allsymbols, bool):
            self._allsymbols = allsymbols
        elif allsymbols.lower() == 'true':
            self._allsymbols = True
        elif allsymbols.lower() == 'false':
            self._allsymbols = False
        else:
            raise ValueError(f'Invalid allsymbols value "{allsymbols}"')

        self._status = pot.get('status', 'active')

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

    def metadata(self):
        """Returns a flat dict of the metadata fields"""
        d = {}
        d['name'] = self.name
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

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, id=None,
                     potid=None, potkey=None, units=None,
                     atom_style=None, pair_style=None, status=None,
                     symbols=None, elements=None):
        
        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.str_match.pandas(dataframe, 'key', key)
            &query.str_match.pandas(dataframe, 'id', id)
            &query.str_match.pandas(dataframe, 'potkey', potkey)
            &query.str_match.pandas(dataframe, 'potid', potid)
            &query.str_match.pandas(dataframe, 'units', units)
            &query.str_match.pandas(dataframe, 'atom_style', atom_style)
            &query.str_match.pandas(dataframe, 'pair_style', pair_style)
            &query.str_match.pandas(dataframe, 'status', status)
            &query.in_list.pandas(dataframe, 'symbols', symbols)
            &query.in_list.pandas(dataframe, 'elements', elements)
        )
        return matches

    def build_model(self):
        return self.model

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
        raise NotImplementedError('Needs to be defined by the child class')