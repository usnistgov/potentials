# coding: utf-8
# Standard Python libraries
import io
from pathlib import Path
from typing import Optional, Tuple, Union
import warnings
import datetime

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/yabadaba
from yabadaba import query 

# local imports
from ..tools import aslist
from .BasePotentialLAMMPS import BasePotentialLAMMPS
class PotentialLAMMPSKIM(BasePotentialLAMMPS):
    """
    Class for building LAMMPS input lines from a potential-LAMMPS-KIM data model.
    """
    
    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 id: Optional[str] = None, 
                 potkey: Optional[str] = None,
                 potid: Optional[str] = None,
                 symbolset: Union[str, list, None] = None):
        """
        Initializes an instance and loads content from a data model.
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            A JSON/XML data model for the content.
        name : str, optional
            The record name to use.  If not given, this will be set to the
            potential's id.
        id : str, optional
            The full KIM model id indicating the version to use.  If not given,
            then the newest known version will be used.
        potkey : str, optional
            Specifies which potential (by potkey value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            This controls which symbols are available.
        potid : str, optional
            Specifies which potential (by potid value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            This controls which symbols are available.
        symbolset : str or list, optional
            Specifies which potential (by symbols value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            If potkey or potid is not given, then the first potential entry
            found with all listed symbols will be selected.
        """
        super().__init__(model=model, name=name, id=id, potkey=potkey, potid=potid,
                         symbolset=symbolset)
        if model is None and id is not None:
            self.id = id
    
    @property
    def style(self) -> str:
        """str: The record style"""
        return 'potential_LAMMPS_KIM'

    @property
    def shortcode(self) -> str:
        """str : The kim model shortcode"""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self.__shortcode

    @property
    def modelroot(self) -> str:
        """str : The root element for the associated data model"""
        return 'potential-LAMMPS-KIM'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'potential_LAMMPS_KIM.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'potential_LAMMPS_KIM.xsd')

    def download_files(self,
                       pot_dir: Optional[str] = None,
                       overwrite: bool = False,
                       verbose: bool = False) -> Tuple[int, int]:
        """
        Downloads all artifact files associated with the potential.  The files
        will be saved to the pot_dir directory.

        Note kim potentials never have files to download.

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
        if verbose:
            print('no files for kim potentials')
        return (0, 0)

    def load_model(self,
                   model,
                   name: Optional[str] = None,
                   id: Optional[str] = None, 
                   potkey: Optional[str] = None,
                   potid: Optional[str] = None,
                   symbolset: Union[str, list, None] = None):
        """
        Loads data model info associated with a LAMMPS potential.
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict
            A JSON/XML data model for the content.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        id : str, optional
            The full KIM model id indicating the version to use.  If not given,
            then the newest known version will be used.
        potkey : str, optional
            Specifies which potential (by potkey value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            This controls which symbols are available.
        potid : str, optional
            Specifies which potential (by potid value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            This controls which symbols are available.
        symbolset : str or list, optional
            Specifies which potential (by symbols value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            If potkey or potid is not given, then the first potential entry
            found with all listed symbols will be selected.
        """
        # Call parent load to read model and some parameters
        super().load_model(model, name=name)
        kimpot = self.model[self.modelroot]
        
        # Handle shortcode, id and name identifiers
        self.__shortcode = kimpot['id']
        if id is not None:
            self._id = id
        else:
            # Get last known id
            self._id = kimpot.aslist('full-kim-id')[-1]
        
        # Set key as shortcode plus version
        self._key = self.id.split('__')[-1]
        
        # Set name as shortcode
        if self.name is None:
            self.name = self.shortcode
        
        # Explicitly set pair_style
        self._pair_style = 'kim'
        
        # Initialize fields for atomic info
        self._potkeys = []
        self._potids = []
        self._symbolsets = []
        self._elementsets = []
        self._masssets = []
        self._chargesets = []
        self._fullsymbols = []
        self._fullelements = []
        self._fullmasses = []
        self._fullcharges = []
        
        # Loop over associated potentials
        for pot in kimpot.aslist('potential'):
            self._potkeys.append(pot['key'])
            self._potids.append(pot['id'])
            
            # Loop over atomic info
            symbols = []
            elements = []
            masses = []
            charges = []
            for atom in pot.aslist('atom'):
                element = atom.get('element', None)
                symbol = atom.get('symbol', None)
                mass = atom.get('mass', None)
                charge = float(atom.get('charge', 0.0))
            
                # Check if element is listed
                if element is None:
                    if mass is None:
                        raise KeyError('mass is required for each atom if element is not listed')
                    if symbol is None:
                        raise KeyError('symbol is required for each atom if element is not listed')
                    else:
                        element = symbol
                
                # Check if symbol is listed.
                if symbol is None:
                    symbol = element
                
                # Add values to the subset lists
                symbols.append(symbol)
                elements.append(element)
                masses.append(mass)
                charges.append(charge)

                # Add values to the full lists
                if symbol not in self._fullsymbols:
                    self._fullsymbols.append(symbol)
                    self._fullelements.append(element)
                    self._fullmasses.append(mass)
                    self._fullcharges.append(charge)
            self._symbolsets.append(symbols)
            self._elementsets.append(elements)
            self._masssets.append(masses)
            self._chargesets.append(charges)

        # Set initial atomic infos to all values
        self._symbols = self._fullsymbols
        self._elements = self._fullelements
        self._masses = self._fullmasses
        self._charges = self._fullcharges

        # Select the potential model
        self.select_potential(potkey=potkey, potid=potid, symbolset=symbolset)

    def mongoquery(self,
                   name: Union[str, list, None] = None,
                   key: Union[str, list, None] = None,
                   id: Union[str, list, None] = None,
                   potid: Union[str, list, None] = None,
                   potkey: Union[str, list, None] = None,
                   units: Union[str, list, None] = None,
                   atom_style: Union[str, list, None] = None,
                   pair_style: Union[str, list, None] = None,
                   status: Union[str, list, None] = None,
                   symbols: Union[str, list, None] = None,
                   elements: Union[str, list, None] = None) -> dict:
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        name : str or list, optional
            The record name(s) to parse by.
        key : str or list, optional
            The UUID4 key(s) associated with the LAMMPS implementations to
            parse by.
        id : str or list, optional
            The unique id(s) associated with the LAMMPS implementations to
            parse by.
        potid : str or list, optional
            The unique id(s) associated with the general potential model to
            parse by.
        potkey : str or list, optional
            The UUID4 key(s) associated with the general potential model to
            parse by.
        units : str or list, optional
            The LAMMPS unit style(s) to parse by.
        atom_style : str or list, optional
            The LAMMPS atom_style values(s) to parse by.
        pair_style : str or list, optional
            The LAMMPS pair_style values(s) to parse by.
        status : str or list, optional
            The implementation status value(s) to parse by.
        symbols : str or list, optional
            Symbol model(s) to parse by.
        elements : str or list, optional
            Elemental tag(s) to parse by.
        
        Returns
        -------
        dict
            The Mongo-style query
        """

        # Return bad query if pair_style kim not included
        if pair_style is not None and 'kim' not in aslist(pair_style):
            return {"not.kim.pair_style":"get nothing"}
        
        # Transform key, id values into shortcodes for query
        shortcodes = set()
        if key is not None:
            for k in aslist(key):
                shortcode = '_'.join(k.split('_')[:-1])
                shortcodes.add(shortcode)
        if id is not None:
            for i in aslist(id):
                k = i.split('__')[-1]
                shortcode = '_'.join(k.split('_')[:-1])
                shortcodes.add(shortcode)
        if len(shortcodes) == 0:
            shortcodes = None
        else:
            shortcodes = list(shortcodes)

        mquery = {}
        query.str_match.mongo(mquery, f'name', name)

        root = f'content.{self.modelroot}'
        #query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', shortcodes)
        query.str_match.mongo(mquery, f'{root}.potential.id', potid)
        query.str_match.mongo(mquery, f'{root}.potential.key', potkey)
        query.in_list.mongo(mquery, f'{root}.potential.atom.symbol', symbols)
        query.in_list.mongo(mquery, f'{root}.potential.atom.element', elements)
        
        if status is not None:
            status = aslist(status)
            if 'active' in status:
                status.append(None)

        query.str_match.mongo(mquery, f'{root}.status', status)
        
        return mquery

    def cdcsquery(self,
                  key: Union[str, list, None] = None,
                  id: Union[str, list, None] = None,
                  potid: Union[str, list, None] = None,
                  potkey: Union[str, list, None] = None,
                  units: Union[str, list, None] = None,
                  atom_style: Union[str, list, None] = None,
                  pair_style: Union[str, list, None] = None,
                  status: Union[str, list, None] = None,
                  symbols: Union[str, list, None] = None,
                  elements: Union[str, list, None] = None) -> dict:
        """
        Builds a CDCS-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        key : str or list, optional
            The UUID4 key(s) associated with the LAMMPS implementations to
            parse by.
        id : str or list, optional
            The unique id(s) associated with the LAMMPS implementations to
            parse by.
        potid : str or list, optional
            The unique id(s) associated with the general potential model to
            parse by.
        potkey : str or list, optional
            The UUID4 key(s) associated with the general potential model to
            parse by.
        units : str or list, optional
            The LAMMPS unit style(s) to parse by.
        atom_style : str or list, optional
            The LAMMPS atom_style values(s) to parse by.
        pair_style : str or list, optional
            The LAMMPS pair_style values(s) to parse by.
        status : str or list, optional
            The implementation status value(s) to parse by.
        symbols : str or list, optional
            Symbol model(s) to parse by.
        elements : str or list, optional
            Elemental tag(s) to parse by.
        
        Returns
        -------
        dict
            The CDCS-style query
        """
        #  Return bad query if pair_style kim not included
        if pair_style is not None and 'kim' not in aslist(pair_style):
            return {"not.kim.pair_style":"get nothing"}

        # Transform key, id values into shortcodes for query
        shortcodes = set()
        if key is not None:
            for k in aslist(key):
                shortcode = '_'.join(k.split('_')[:-1])
                shortcodes.add(shortcode)
        if id is not None:
            for i in aslist(id):
                k = i.split('__')[-1]
                shortcode = '_'.join(k.split('_')[:-1])
                shortcodes.add(shortcode)
        if len(shortcodes) == 0:
            shortcodes = None
        else:
            shortcodes = list(shortcodes)

        mquery = {}
        root = self.modelroot

        #query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', shortcodes)
        query.str_match.mongo(mquery, f'{root}.potential.id', potid)
        query.str_match.mongo(mquery, f'{root}.potential.key', potkey)
        query.in_list.mongo(mquery, f'{root}.potential.atom.symbol', symbols)
        query.in_list.mongo(mquery, f'{root}.potential.atom.element', elements)

        if status is not None:
            status = aslist(status)
            if 'active' in status:
                status.append(None)

        query.str_match.mongo(mquery, f'{root}.status', status)

        return mquery

    @property
    def symbolsets(self) -> list:
        """list : The sets of symbols that correspond to all related potentials"""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._symbolsets

    @property
    def potids(self) -> list:
        """list : The ids of all related potentials"""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._potids
    
    @property
    def potkeys(self) -> list:
        """list : The keys of all related potentials"""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._potkeys

    def select_potential(self,
                         potkey: Optional[str] = None,
                         potid: Optional[str] = None,
                         symbolset: Union[str, list, None] = None):
        """
        Sets the potkey, potid, symbols, elements, masses and charges values
        based on identifying which potential associated with the KIM model
        implementation to use.  If only one potential is associated with the
        KIM model then any given values will be validated.

        Parameters
        ----------
        potkey : str, optional
            Specifies which potential (by potkey value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            This controls which symbols are available.
        potid : str, optional
            Specifies which potential (by potid value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            This controls which symbols are available.
        symbolset : str or list, optional
            Specifies which potential (by symbols value) to use.  Only important
            if the kim model is associated with multiple potential entries.
            If potkey or potid is not given, then the first potential entry
            found with all listed symbols will be selected.
        """
        # If only one potential is associated with the model
        if len(self.symbolsets) == 1:
            # Set values
            self._potid = self._potids[0]
            self._potkey = self._potkeys[0]
            self._symbols = self._symbolsets[0]
            self._elements = self._elementsets[0]
            self._masses = self._masssets[0]
            self._charges = self._chargesets[0]

            if symbolset is not None:
                # Check that symbols are in symbolset
                for symbol in aslist(symbolset):
                    if symbol not in self.symbols:
                        raise ValueError(f'symbolset does not match potential')
            if potkey is not None:
                if potkey != self.potkey:
                    raise ValueError('potkey does not match potential')
            if potid is not None:
                if potid != self.potid:
                    raise ValueError('potid does not match potential')

        # If multiple potentials are associated with the model
        else:
            if symbolset is None and potid is None and potkey is None:
                # Set default values
                self._potkey = None
                self._potid = None
                self._symbols = self._fullsymbols
                self._elements = self._fullelements
                self._masses = self._fullmasses
                self._charges = self._fullcharges

            elif potid is not None:
                # Find match and set values
                i = self.potids.index(potid)
                self._potid = self._potids[i]
                self._potkey = self._potkeys[i]
                self._symbols = self._symbolsets[i]
                self._elements = self._elementsets[i]
                self._masses = self._masssets[i]
                self._charges = self._chargesets[i]
                
                # Check that potkey is correct
                if potkey is not None:
                    if potkey != self.potkey:
                        raise ValueError('potkey does not match potential given by potid')
                
                # Check that symbols are in symbolset
                if symbolset is not None:
                    for symbol in aslist(symbolset):
                        if symbol not in self.symbols:
                            raise ValueError(f'symbolset does not match potential given by potid')
                
            elif potkey is not None:
                # Find match and set values
                i = self.potkeys.index(potkey)
                self._potid = self._potids[i]
                self._potkey = self._potkeys[i]
                self._symbols = self._symbolsets[i]
                self._elements = self._elementsets[i]
                self._masses = self._masssets[i]
                self._charges = self._chargesets[i]
                
                # Check that symbols are in symbolset
                if symbolset is not None:
                    for symbol in aslist(symbolset):
                        if symbol not in self.symbols:
                            raise ValueError('symbolset does not match potential given by potkey')

            else:
                # Search for first matching symbolset
                for i, symbols in enumerate(self.symbolsets):
                    match = True
                    for symbol in aslist(symbolset):
                        if symbol not in symbols:
                            match = False
                            break
                    if match:
                        break
                
                if match:
                    # Set values
                    self._potid = self._potids[i]
                    self._potkey = self._potkeys[i]
                    self._symbols = self._symbolsets[i]
                    self._elements = self._elementsets[i]
                    self._masses = self._masssets[i]
                    self._charges = self._chargesets[i]
                
                else:
                    # Check that symbols are in fullsymbols
                    for symbol in aslist(symbolset):
                        if symbol not in self._fullsymbols:
                            raise ValueError(f'symbol {symbol} not in any symbolsets')
                    
                    warnings.warn('No single entry for all symbols - cross interactions not recommended')
                    # Set default values
                    self._potkey = None
                    self._potid = None
                    self._symbols = self._fullsymbols
                    self._elements = self._fullelements
                    self._masses = self._fullmasses
                    self._charges = self._fullcharges

    def normalize_symbols(self,
                          symbols: Union[str, list]) -> list:
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
        # Call parent method
        symbols = super().normalize_symbols(symbols)
        
        # Call select_potential if needed
        if self.potid is None:
            self.select_potential(symbols)

        return symbols

    def pair_info(self,
                  symbols: Union[str, list, None] = None,
                  masses: Union[float, list, None] = None,
                  units: Optional[str] = None,
                  prompt: bool = False,
                  comments: bool = True,
                  lammpsdate: datetime.date = datetime.date(2020, 10, 29)
                  ) -> str:
        """
        Generates the LAMMPS input command lines associated with a KIM
        Potential and a list of atom-model symbols.
        
        Parameters
        ----------
        symbols : str or list, optional
            List of atom-model symbols corresponding to the atom types in a
            system.  If None (default), then all atom-model symbols will
            be included in the order that they are listed in the data model.
        masses : float or list, optional
            Can be given to override the default symbol-based masses for each
            atom type.  Must be a list of the same length as symbols.  Any
            values of None in the list indicate that the default value be used
            for that atom type.
        units : str, optional
            The LAMMPS unit setting to use for the output.  If not given,
            will use the default value set for the potential.
        prompt : bool, optional
            If True, then a screen prompt will appear for radioactive elements
            with no standard mass to ask for the isotope to use. If False
            (default), then the most stable isotope will be automatically used.
        comments : bool, optional
            Indicates if print command lines detailing information on the potential
            are to be included.  Default value is True.
        lammpsdate : datetime, optional
            The LAMMPS version date that is to be used.  The generated commands
            may differ based on the version of LAMMPS used.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential.
        """
        # Handle units
        if units is None:
            units = self.units
        
        # If no symbols supplied use all for potential
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = self.normalize_symbols(symbols)

        if masses is not None:
            
            # Check length of masses
            masses = aslist(masses)
            assert len(masses) == len(symbols), 'supplied masses must be same length as symbols'
            
            # Change None values to default values
            defaultmasses = self.masses(symbols, prompt=prompt)
            for i in range(len(masses)):
                if masses[i] is None:
                    masses[i] = defaultmasses[i]
        else:
            masses = self.masses(symbols, prompt=prompt)
        
        # Generate kim_init line
        if lammpsdate >= datetime.date(2021, 3, 10):
            info = f'kim init {self.id} {units}\n'
        else:        
            info = f'kim_init {self.id} {units}\n'

        # Generate kim_interactions  line
        if lammpsdate >= datetime.date(2021, 3, 10):
            info += f'kim interactions {" ".join(symbols)}\n'
        else:        
            info += f'kim_interactions {" ".join(symbols)}\n'
        
        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        return info

    def pair_data_info(self,
                       filename: Union[str, Path],
                       pbc: npt.ArrayLike,
                       symbols: Union[str, list, None] = None,
                       masses: Union[float, list, None] = None,
                       atom_style: Optional[str] = None,
                       units: Optional[str] = None,
                       prompt: bool = False,
                       comments: bool = True,
                       lammpsdate: datetime.date = datetime.date(2020, 10, 29)
                       ) -> str:
        """
        Generates the LAMMPS command lines associated with both a potential
        and reading an atom data file.

        Parameters
        ----------
        filename : path-like object
            The file path to the atom data file for LAMMPS to read in.
        pbc : array-like object
            The three boolean periodic boundary conditions.
        symbols : str or list, optional
            List of atom-model symbols corresponding to the atom types in a
            system.  If None (default), then all atom-model symbols will
            be included in the order that they are listed in the data model.
        masses : float or list, optional
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
            If True, then a screen prompt will appear for radioactive elements
            with no standard mass to ask for the isotope to use. If False
            (default), then the most stable isotope will be automatically used.
        comments : bool, optional
            Indicates if print command lines detailing information on the potential
            are to be included.  Default value is True.
        lammpsdate : datetime, optional
            The LAMMPS version date that is to be used.  The generated commands
            may differ based on the version of LAMMPS used.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential and a data
            file to read.
        """
        # Handle units
        if units is None:
            units = self.units

        # If no symbols supplied use all for potential
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = self.normalize_symbols(symbols)

        if masses is not None:
            
            # Check length of masses
            masses = aslist(masses)
            assert len(masses) == len(symbols), 'supplied masses must be same length as symbols'
            
            # Change None values to default values
            defaultmasses = self.masses(symbols, prompt=prompt)
            for i in range(len(masses)):
                if masses[i] is None:
                    masses[i] = defaultmasses[i]
        else:
            masses = self.masses(symbols, prompt=prompt)

         # Add comment line
        info = '# Script and atom data file prepared using atomman Python package\n\n'

        # Generate kim_init line
        if lammpsdate >= datetime.date(2021, 3, 10):
            info = f'kim init {self.id} {units}\n'
        else:        
            info = f'kim_init {self.id} {units}\n'

        # Change atom_style if needed
        if atom_style is not None:
            info += f'atom_style {atom_style}\n'

        # Set boundary flags to p or m based on pbc values
        bflags = np.array(['m','m','m'])
        bflags[pbc] = 'p'
        info += f'\nboundary {bflags[0]} {bflags[1]} {bflags[2]}\n'
        
        # Set read_data command 
        info += f'read_data {filename}\n\n'

        # Generate kim_interactions  line
        if lammpsdate >= datetime.date(2021, 3, 10):
            info += f'kim interactions {" ".join(symbols)}\n'
        else:        
            info += f'kim_interactions {" ".join(symbols)}\n'
        
        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        return info

    def pair_restart_info(self,
                          filename: Union[str, Path],
                          symbols: Union[str, list, None] = None,
                          masses: Union[float, list, None] = None,
                          units: Optional[str] = None,
                          prompt: bool = False,
                          comments: bool = True,
                          lammpsdate: datetime.date = datetime.date(2020, 10, 29)
                          ) -> str:
        """
        Generates the LAMMPS command lines associated with both a potential
        and reading an atom data file.

        Parameters
        ----------
        filename : path-like object
            The file path to the restart file for LAMMPS to read in.
        symbols : str or list, optional
            List of atom-model symbols corresponding to the atom types in a
            system.  If None (default), then all atom-model symbols will
            be included in the order that they are listed in the data model.
        masses : float or list, optional
            Can be given to override the default symbol-based masses for each
            atom type.  Must be a list of the same length as symbols.  Any
            values of None in the list indicate that the default value be used
            for that atom type.
        units : str, optional
            The LAMMPS unit setting to use for the output.  If not given,
            will use the default value set for the potential.
        prompt : bool, optional
            If True, then a screen prompt will appear for radioactive elements
            with no standard mass to ask for the isotope to use. If False
            (default), then the most stable isotope will be automatically used.
        comments : bool, optional
            Indicates if print command lines detailing information on the potential
            are to be included.  Default value is True.
        lammpsdate : datetime, optional
            The LAMMPS version date that is to be used.  The generated commands
            may differ based on the version of LAMMPS used.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential and a restart
            file to read.
        """
        # Handle units
        if units is None:
            units = self.units

        # If no symbols supplied use all for potential
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = self.normalize_symbols(symbols)

        if masses is not None:
            
            # Check length of masses
            masses = aslist(masses)
            assert len(masses) == len(symbols), 'supplied masses must be same length as symbols'
            
            # Change None values to default values
            defaultmasses = self.masses(symbols, prompt=prompt)
            for i in range(len(masses)):
                if masses[i] is None:
                    masses[i] = defaultmasses[i]
        else:
            masses = self.masses(symbols, prompt=prompt)

        # Add comment line
        info = '# Script prepared using atomman Python package\n\n'
    
        # Generate kim_init line
        if lammpsdate >= datetime.date(2021, 3, 10):
            info = f'kim init {self.id} {units}\n'
        else:        
            info = f'kim_init {self.id} {units}\n'

        # Set read_data command 
        info += f'read_restart {filename}\n'

        # Generate kim_interactions  line
        if lammpsdate >= datetime.date(2021, 3, 10):
            info += f'kim interactions {" ".join(symbols)}\n'
        else:        
            info += f'kim_interactions {" ".join(symbols)}\n'

        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        return info