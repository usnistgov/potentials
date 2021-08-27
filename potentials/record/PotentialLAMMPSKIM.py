# coding: utf-8
# Standard Python libraries
import warnings

import numpy as np

# atomman imports
from ..tools import atomic_mass, aslist
from .BasePotentalLAMMPS import BasePotentialLAMMPS

from datamodelbase import query 

class PotentialLAMMPSKIM(BasePotentialLAMMPS):
    """
    Class for building LAMMPS input lines from a potential-LAMMPS-KIM data model.
    """
    
    def __init__(self, model=None, name=None, id=None):
        """
        Initializes an instance and loads content from a data model.
        
        Parameters
        ----------
        model : str or file-like object, optional
            A JSON/XML data model containing a potential-LAMMPS-KIM branch.
        name : str, optional
            The record name to use.  If not given, this will be set to the
            potential's id.
        id : str, optional
            The full KIM model id indicating the version to use.  If not given,
            then the newest known version will be used.
        """
        super().__init__(model=model, name=name, id=id)
        if model is None and id is not None:
            self.id = id
    
    @property
    def style(self):
        """str: The record style"""
        return 'potential_LAMMPS_KIM'

    @property
    def id(self):
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._id

    @id.setter
    def id(self, value):
        if self.shortcode in value:
            self._id = value
        else:
            raise ValueError('id must contain the correct model shortcode')

    @property
    def shortcode(self):
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self.__shortcode

    @property
    def modelroot(self):
        """str : The root element for the associated data model"""
        return 'potential-LAMMPS-KIM'

    def download_files(self, *args, **kwargs):
        """
        Downloads artifact files associated with the potential.  Note that
        no files exist to download for openKIM models

        Parameters
        ----------
        *args, **kwargs : any
            Allows any parameters in - all are ignored.
        
        Returns
        -------
        count : int
            The number of files downloaded - always 0
        """
        return 0

    def load_model(self, model, name=None, id=None):
        """
        Loads data model info associated with a LAMMPS potential.
        
        Parameters
        ----------
        model : str or file-like object
            A JSON/XML data model for the content.
        id : str, optional
            The full KIM model id indicating the version to use.  If not given,
            then the newest known version will be used.
        """
        # Call parent load to read model and some parameters
        super().load_model(model, name=name)
        kimpot = self.model[self.modelroot]
        
        # Handle shortcode, id and name identifiers
        self.__shortcode = kimpot['id']
        if id is not None:
            self.id = id
        else:
            # Get last known id
            self.id = kimpot.aslist('full-kim-id')[-1]
        if self.name is None:
            self.name = self.shortcode
        
        # Explicitly set pair_style
        self._pair_style = 'kim'
        
        # Initialize fields for atomic info
        self._potkeys = []
        self._potids = []
        self._symbolsets = []
        self._fullsymbols = []
        self._fullelements = []
        self._fullmasses = []
        self._fullcharges = []
        
        # Loop over associated potentials
        for pot in kimpot.aslist('potential'):
            self._potkeys.append(pot['key'])
            self._potids.append(pot['id'])
            
            # Loop over atomic info
            symbolset = []
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
                
                # Add values to the lists
                symbolset.append(symbol)
                if symbol not in self._fullsymbols:
                    self._fullsymbols.append(symbol)
                    self._fullelements.append(element)
                    self._fullmasses.append(mass)
                    self._fullcharges.append(charge)
            self._symbolsets.append(symbolset)

        # Set initial atomic infos to all values
        self._symbols = self._fullsymbols
        self._elements = self._fullelements
        self._masses = self._fullmasses
        self._charges = self._fullcharges

        # Set potkey and potid if unique
        if len(self.potkeys) == 1:
            self._potkey = self.potkeys[0]
            self._potid = self.potids[0]
        else:
            self._potkey = None
            self._potid = None

    def mongoquery(self, name=None, key=None, id=None,
                     potid=None, potkey=None, units=None,
                     atom_style=None, pair_style=None, status=None,
                     symbols=None, elements=None):
        
        # Return bad query if pair_style kim not included
        if pair_style is not None and 'kim' not in aslist(pair_style):
            return {"not.kim.pair_style":"get nothing"}
        
        mquery = {}
        query.str_match.mongo(mquery, f'name', name)

        root = f'content.{self.modelroot}'
        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_match.mongo(mquery, f'{root}.potential.id', potid)
        query.str_match.mongo(mquery, f'{root}.potential.key', potkey)
        query.str_match.mongo(mquery, f'{root}.potential.atom.symbol', symbols)
        query.str_match.mongo(mquery, f'{root}.potential.atom.element', elements)
        
        if status is not None:
            status = aslist(status)
            if 'active' in status:
                status.append(None)

        query.str_match.mongo(mquery, f'{root}.status', status)
        
        return mquery

    def cdcsquery(self, key=None, id=None, potid=None, potkey=None,
                  units=None, atom_style=None, pair_style=None, status=None,
                  symbols=None, elements=None):
        
        #  Return bad query if pair_style kim not included
        if pair_style is not None and 'kim' not in aslist(pair_style):
            return {"not.kim.pair_style":"get nothing"}

        mquery = {}
        root = self.modelroot

        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_match.mongo(mquery, f'{root}.potential.id', potid)
        query.str_match.mongo(mquery, f'{root}.potential.key', potkey)
        query.str_match.mongo(mquery, f'{root}.potential.atom.symbol', symbols)
        query.str_match.mongo(mquery, f'{root}.potential.atom.element', elements)

        if status is not None:
            status = aslist(status)
            if 'active' in status:
                status.append(None)

        query.str_match.mongo(mquery, f'{root}.status', status)

        return mquery


    @property
    def symbolsets(self):
        """list : The sets of symbols that correspond to all related potentials"""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._symbolsets

    @property
    def potids(self):
        """list : The ids of all related potentials"""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._potids
    
    @property
    def potkeys(self):
        """list : The keys of all related potentials"""
        if self.model is None:
            raise AttributeError('No model information loaded')
        return self._potkeys

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
        # Call parent method
        symbols = super().normalize_symbols(symbols)
        
        # Check if all symbols are in the same potential set
        if len(self.symbolsets) > 1:
            for i, symbolset in enumerate(self.symbolsets):
                match = True
                for symbol in symbols:
                    if symbol not in symbolset:
                        match = False
                        break
                if match:
                    break
            
            if match:
                self._potkey = self.potkeys[i]
                self._potid = self.potids[i]
                self._symbols = self.symbolsets[i]
            else:
                warnings.warn('No single entry for all symbols - cross interactions not recommended')
                self._potkey = None
                self._potid = None
                self._symbols = self._fullsymbols

        return symbols
        
    def masses(self, symbols=None, prompt=True):
        """
        Returns a list of atomic/ionic masses associated with atom-model
        symbols.
        
        Parameters
        ----------
        symbols : list of str, optional
            A list of atom-model symbols.  If None (default), will use all of
            the potential's symbols.
        prompt : bool, optional
            If True (default), then a screen prompt will appear asking for the isotope
            number if no mass is pre-defined for a symbol and the associated element 
            lacks a single standard atomic/ionic mass.  If False, then an error will
            be raised for these cases instead.
        
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
            i = self._fullsymbols.index(symbol)
            if self._fullmasses[i] is None:
                masses.append(atomic_mass(self._fullelements[i], prompt=prompt))
            else:
                masses.append(self._fullmasses[i])
        
        return masses

    def charges(self, symbols=None):
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
        # Return all charges if symbols is None
        if symbols is None:
            symbols = self._symbols
        else:
            # Normalize symbols
            symbols = self.normalize_symbols(symbols)
        
        # Get all matching charges
        charges = []
        for symbol in symbols:
            i = self._fullsymbols.index(symbol)
            charges.append(self._fullcharges[i])
        
        return charges

    def pair_info(self, symbols=None, masses=None, units=None, prompt=True):
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
        info = f'kim_init {self.id} {units}\n'

        # Generate kim_interactions  line
        info += f'kim_interactions {" ".join(symbols)}\n'
        
        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        return info

    def pair_data_info(self, filename, pbc, symbols=None, masses=None,
                       atom_style=None, units=None, prompt=True,
                       comments=True):
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
        comments : bool, optional
            Indicates if print command lines detailing information on the potential
            are to be included.  Default value is True.
        
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
        info += f'kim_init {self.id} {units}\n'

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
        info += f'kim_interactions {" ".join(symbols)}\n'
        
        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        return info

    def pair_restart_info(self, filename, symbols=None, masses=None,
                          units=None, prompt=True, comments=True):
        """
        Generates the LAMMPS command lines associated with both a potential
        and reading an atom data file.

        Parameters
        ----------
        filename : path-like object
            The file path to the restart file for LAMMPS to read in.
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
        comments : bool, optional
            Indicates if print command lines detailing information on the potential
            are to be included.  Default value is True.

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
        info += f'kim_init {self.id} {units}\n'

        # Set read_data command 
        info += f'read_restart {filename}\n'

        # Generate kim_interactions  line
        info += f'kim_interactions {" ".join(symbols)}\n'

        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        return info