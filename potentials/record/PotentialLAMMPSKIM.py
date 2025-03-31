# coding: utf-8
# Standard Python libraries
import io
from pathlib import Path
from typing import Optional, Tuple, Union
import datetime

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_query

# local imports
from ..tools import aslist, atomic_mass
from .PotentialInfo import PotentialInfo

class PotentialLAMMPSKIM(Record):
    """
    Class for building LAMMPS input lines from a potential-LAMMPS-KIM data model.
    """
    
    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 id: Optional[str] = None, 
                 potkey: Optional[str] = None,
                 potid: Optional[str] = None,
                 symbolset: Union[str, list, None] = None,
                 units: str = 'metal'):
        """
        Initializes an instance and loads content from a data model.
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            A JSON/XML data model for the content.
        name : str, optional
            The record name to use.  If not given, this will be set to the
            potential's id.
        database : yabadaba.Database, optional
            Allows for a default database to be associated with the record.
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

        # Call super with only name
        super().__init__(model=model, name=name, database=database)

        # Set default id as latest fullkimid if possible
        if id is None and self.fullkimids is not None:
            self.__id = self.fullkimids[-1]
        else:
            self.__id = id

        self.units = units

        # Select the potential model information to use
        self.select_potential(potkey=potkey, potid=potid, symbolset=symbolset)

    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'potential_LAMMPS_KIM'

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

    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'modelkey', modelpath='key')
        self._add_value('str', 'shortcode', modelpath='id')
        self._add_value('str', 'url', modelpath='URL')
        self._add_value('str', 'status', allowedvalues=('superseded', 'retracted'))
        self._add_value('record', 'potentials', recordclass=PotentialInfo,
                        modelpath='potential', metadatakey=False)
        self._add_value('strlist', 'fullkimids', modelpath='full-kim-id')
        

    @property
    def defaultname(self) -> Optional[str]:
        """str: The name to default to, usually based on other properties"""
        return self.shortcode

    @property
    def id(self):
        """str: The full kim model id for the potential implementation."""
        return self.__id

    @id.setter
    def id(self, val: str):
        self.__id = str(val)

    @property
    def key(self):
        """str: The short kim model id (shortcode plus version)"""
        return self.id[-19:]

    @property
    def potkey(self) -> Optional[str]:
        """str : uuid hash-key for the potential model."""
        return self.__potkey

    @property
    def potid(self) -> Optional[str]:
        """str : Human-readable identifier for the potential model."""
        return self.__potid

    @property
    def poturl(self) -> Optional[str]:
        """str : URL for an online copy of the potential model record."""
        return self.__poturl
    
    @property
    def dois(self) -> list:
        """list: DOIs associated with the potential model."""
        return self.__dois
    
    @property
    def units(self) -> str:
        """str : LAMMPS units option."""
        return self.__units

    @units.setter
    def units(self, val: Optional[str]):
        self.__units = val

    @property
    def atoms(self) -> list:
        """list : The list of atomic models represented by the potential."""
        return self.__atoms

    @property
    def pair_style(self) -> str:
        """str : LAMMPS pair_style option."""
        return 'kim'
    
    @property
    def atom_style(self) -> str:
        """str : LAMMPS atom_style option."""
        return 'atomic'

    @property
    def symbols(self) -> list:
        """list of str : All atom-model symbols."""
        symbols = []
        for atom in self.atoms:
            symbols.append(atom.symbol)
        return symbols

    def add_potential(self, **kwargs):
        """
        Initializes a new PotentialInfo object and appends it to the potentials list.
        """
        newpot = PotentialInfo(**kwargs)
        for pot in self.potentials:
            if pot.id == newpot.id:
                raise ValueError(f'PotentialInfo with id {pot.id} already exists')
        self.potentials.append(newpot)


    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        meta = super().metadata()

        meta['id'] = self.id
        meta['key'] = self.key
        meta['potid'] = self.potid
        meta['potkey'] = self.potkey
        meta['poturl'] = self.poturl
        meta['units'] = self.units
        meta['pair_style'] = self.pair_style
        meta['symbols'] = self.symbols
        meta['elements'] = self.elements()

        return meta


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
                   symbolset: Union[str, list, None] = None,
                   units: str = 'metal'):
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
        
        # Set default id as latest fullkimid if possible
        if id is None and self.fullkimids is not None:
            self.__id = self.fullkimids[-1]
        else:
            self.__id = id

        self.units = units

        # Select the potential model
        self.select_potential(potkey=potkey, potid=potid, symbolset=symbolset)

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        queries = super().queries

        queries.update({
            'id': load_query(
                style='list_contains',
                name='id',
                path=f'{self.modelroot}.full-kim-id',
                description="search based on the implementation's id (KIM ID)"),
            'key': load_query(
                style='dummy',
                description="search based on the implementation's key"),
            'potkey': load_query(
                style='str_match',
                name='potkey',
                path=f'{self.modelroot}.potential.key',
                description="search based on the potential's UUID key"),
            'potid': load_query(
                style='str_match',
                name='potid',
                path=f'{self.modelroot}.potential.id',
                description="search based on the potential's id"),
            'units': load_query(
                style='dummy',
                description="search based on LAMMPS units setting"),
            'atom_style': load_query(
                style='dummy',
                description="search based on LAMMPS atom_style setting"),
            'pair_style': load_query(
                style='dummy',
                value='kim',
                description="search based on LAMMPS pair_style setting"),
            'symbols': load_query(
                style='list_contains',
                name='symbols',
                path=f'{self.modelroot}.potential.atom.symbol',
                description="search based on atomic model symbols"),
            'elements': load_query(
                style='list_contains',
                name='elements',
                path=f'{self.modelroot}.potential.atom.element',
                description="search based on atomic model elements"),
        })

        return queries

    

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
        # Default cases
        if symbolset is None and potid is None and potkey is None:
            
            if len(self.potentials) == 1:

                # Point to single potential model
                self.__potid = self.potentials[0].id
                self.__potkey = self.potentials[0].key
                self.__poturl = self.potentials[0].url
                self.__dois = self.potentials[0].dois
                self.__atoms = self.potentials[0].atoms
            
            else:
                
                # Set empty or comprehensive values
                self.__potkey = None
                self.__potid = None
                self.__poturl = None
                self.__dois = None
                self.__atoms = []
                for potential in self.potentials:
                    self.atoms.extend(potential.atoms)

        else:
            
            # Loop over all potential models
            idmatch = False
            for potinfo in self.potentials:

                # Check if potid, potkey and symbolset match with potinfo
                idmatch = (potid is None or potinfo.id == potid)
                keymatch = (potkey is None or potinfo.key == potkey)
                symbolsmatch = True
                if symbolset is not None:
                    symbols = []
                    for atom in potinfo.atoms:
                        symbols.append(atom.symbol)
                    for symbol in aslist(symbolset):
                        if symbol not in symbols:
                            symbolsmatch = False
                
                if idmatch and keymatch and symbolsmatch:
                    break

            # Point to the first matching potential model
            if idmatch and keymatch and symbolsmatch:
                self.__potid = potinfo.id
                self.__potkey = potinfo.key
                self.__poturl = potinfo.url
                self.__dois = potinfo.dois
                self.__atoms = potinfo.atoms
            #else:
            #    raise ValueError('No potential info matching the given potkey, potid, symbolset found!')



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
        # Convert symbols to a list if needed
        symbols = aslist(symbols)

        # Check that all symbols are set
        for symbol in symbols:
            assert symbol is not None, 'symbols list incomplete: found None value'
        
        # Call select_potential if needed
        if self.potid is None:
            self.select_potential(symbols)

        return symbols

    def elements(self,
                 symbols: Union[str, list, None] = None) -> list:
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
        # Get full list of all symbols for the potential
        fullsymbols = self.symbols

        # Set default symbols to fullsymbols
        if symbols is None:
            symbols = fullsymbols

        # Normalize symbols
        symbols = self.normalize_symbols(symbols)

        # Get all matching elements
        elements = []
        for symbol in symbols:
            i = fullsymbols.index(symbol)
            elements.append(self.atoms[i].element)

        return elements

    def masses(self,
               symbols: Union[str, list, None] = None,
               prompt: bool = False) -> list:
        """
        Returns a list of atomic/ionic masses associated with atom-model
        symbols.
        
        Parameters
        ----------
        symbols : list of str, optional
            A list of atom-model symbols.  If None (default), will use all of
            the potential's symbols.
        prompt : bool, optional
            If True, then a screen prompt will appear for radioactive elements
            with no standard mass to ask for the isotope to use. If False
            (default), then the most stable isotope will be automatically used.
        
        Returns
        -------
        list of float
            The atomic/ionic masses corresponding to the atom-model symbols.
        """
        # Get full list of all symbols for the potential
        fullsymbols = self.symbols

        # Set default symbols to fullsymbols
        if symbols is None:
            symbols = fullsymbols

        # Normalize symbols
        symbols = self.normalize_symbols(symbols)

        # Get all matching masses
        masses = []
        for symbol in symbols:
            i = fullsymbols.index(symbol)
            atom = self.atoms[i]
            if atom.mass is None:
                masses.append(atomic_mass(atom.element, prompt=prompt))
            else:
                masses.append(atom.mass)

        return masses

    def charges(self,
                symbols: Union[str, list, None] = None) -> list:
        """
        Returns a list of atomic charges associated with atom-model symbols.
        Will have a None value if not assigned.
        
        Parameters
        ----------
        symbols : list of str, optional
            A list of atom-model symbols.  If None (default), will use all of
            the potential's symbols.
        
        Returns
        -------
        list of float
            The atomic charges corresponding to the atom-model symbols.
        """
        # Get full list of all symbols for the potential
        fullsymbols = self.symbols

        # Set default symbols to fullsymbols
        if symbols is None:
            symbols = fullsymbols

        # Normalize symbols
        symbols = self.normalize_symbols(symbols)

        # Get all matching charges
        charges = []
        for symbol in symbols:
            i = fullsymbols.index(symbol)
            atom = self.atoms[i]
            if atom.charge is None:
                charges.append(0.0)
            else:
                charges.append(atom.charge)

        return charges


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