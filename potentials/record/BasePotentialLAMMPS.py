# coding: utf-8
# Standard Python libraries
import io
from pathlib import Path
from typing import Optional, Tuple, Union
import datetime

# https://numpy.org/
import numpy.typing as npt

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

# atomman imports
from ..tools import aslist, atomic_mass

class BasePotentialLAMMPS(Record):
    """
    Base parent class for PotentialLAMMPS objects
    """
    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None):
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
        **kwargs : any, optional
            Any other keyword parameters supported by the child class.
        """
        # Check if base class is initialized directly
        if self.__module__ == __name__:
            raise TypeError("don't use base class")

        # Set default values
        self.pot_dir = ''
        self.__artifacts = []
        self._id = None
        self._key = None
        self._url = None
        self._potid = None
        self._potkey = None
        self._poturl = None
        self._units = None
        self._atom_style = None
        self._elements = []
        self._symbols = []
        self._masses = []
        self._charges = []
        self._pair_style = None
        self._allsymbols = False
        self._status = None

        # Pass parameters to load
        super().__init__(model, name=name, database=database)

    @property
    def id(self) -> str:
        """str : Human-readable identifier for the LAMMPS implementation."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._id

    @property
    def key(self) -> str:
        """str : uuid hash-key for the LAMMPS implementation."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._key

    @property
    def url(self):
        """str : URL for an online copy of the record."""
        return self._url

    @property
    def potid(self) -> str:
        """str : Human-readable identifier for the potential model."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._potid

    @property
    def potkey(self) -> str:
        """str : uuid hash-key for the potential model."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._potkey

    @property
    def poturl(self):
        """str : URL for an online copy of the potential model record."""
        return self._poturl

    @property
    def units(self) -> str:
        """str : LAMMPS units option."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._units

    @property
    def atom_style(self) -> str:
        """str : LAMMPS atom_style option."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._atom_style

    @property
    def symbols(self) -> list:
        """list of str : All atom-model symbols."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._symbols

    @property
    def pair_style(self) -> str:
        """str : LAMMPS pair_style option."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._pair_style

    @property
    def allsymbols(self) -> bool:
        """bool : indicates if all model symbols must be listed."""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._allsymbols

    @property
    def status(self) -> str:
        """str : Indicates the status of the implementation (active, superseded, retracted)"""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._status

    @property
    def pot_dir(self):
        """str : The directory containing files associated with a given potential."""
        return self.__pot_dir

    @pot_dir.setter
    def pot_dir(self, value: str):
        self.__pot_dir = str(value)

    @property
    def artifacts(self) -> list:
        """list : The list of file artifacts for the potential including download URLs."""
        return self.__artifacts

    def download_files(self,
                       pot_dir: Optional[str] = None,
                       overwrite: bool = False,
                       verbose: bool = False) -> Tuple[int, int]:
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

    def load_model(self,
                   model: Union[str, io.IOBase, DM],
                   name: Optional[str] = None):
        """
        Loads data model info associated with a LAMMPS potential.
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict
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
        except AttributeError:
            self.name = self.id

        self._key = pot['key']
        self._url = pot.get('URL', None)
        try:
            self._potid = pot['potential']['id']
        except (KeyError, TypeError):
            self._potid = None
        try:
            self._potkey = pot['potential']['key']
        except (KeyError, TypeError):
            self._potkey = None
        try:
            self._poturl = pot['potential']['URL']
        except (KeyError, TypeError):
            self._poturl = None
        self._units = pot.get('units', 'metal')
        self._atom_style = pot.get('atom_style', 'atomic')
        try:
            self._pair_style = pot['pair_style']['type']
        except (KeyError, TypeError):
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
        self._masses = []
        self._charges = []

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

        # Add missing symbols if potential's allsymbols is True
        if self.allsymbols:
            for symbol in self.symbols:
                if symbol not in symbols:
                    symbols.append(symbol)

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

        # Use all symbols if symbols is None
        if symbols is None:
            symbols = self.symbols
        else:
            # Normalize symbols
            symbols = self.normalize_symbols(symbols)

        # Get all matching masses
        masses = []
        for symbol in symbols:
            i = self.symbols.index(symbol)
            if self._masses[i] is None:
                masses.append(atomic_mass(self._elements[i], prompt=prompt))
            else:
                masses.append(self._masses[i])

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
        # Use all symbols if symbols is None
        if symbols is None:
            symbols = self.symbols
        else:
            # Normalize symbols
            symbols = self.normalize_symbols(symbols)

        # Get all matching charges
        charges = []
        for symbol in symbols:
            i = self.symbols.index(symbol)
            charges.append(self._charges[i])

        return charges

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        if self.model is None:
            raise AttributeError('No model information loaded')

        d = {}
        d['name'] = self.name
        d['id'] = self.id
        d['key'] = self.key
        d['url'] = self.url
        d['potid'] = self.potid
        d['potkey'] = self.potkey
        d['poturl'] = self.poturl
        d['units'] = self.units
        d['atom_style'] = self.atom_style
        d['allsymbols'] = self.allsymbols
        d['pair_style'] = self.pair_style
        d['status'] = self.status
        d['symbols'] = self.symbols
        d['elements'] = self.elements()

        return d

    def build_model(self) -> DM:
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self.model

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
        raise NotImplementedError('Needs to be defined by the child class')

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
        raise NotImplementedError('Needs to be defined by the child class')

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
        raise NotImplementedError('Needs to be defined by the child class')
