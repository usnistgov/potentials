# coding: utf-8
# Standard Python libraries
from pathlib import Path

import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://requests.readthedocs.io/en/master/
import requests

# atomman imports
from .tools import atomic_mass, aslist
from .BasePotentalLAMMPS import BasePotentialLAMMPS
from . import Artifact

class PotentialLAMMPS(BasePotentialLAMMPS):
    """
    Class for building LAMMPS input lines from a potential-LAMMPS data model.
    """
    
    def __init__(self, model, pot_dir=None):
        """
        Initializes an instance and loads content from a data model.
        
        Parameters
        ----------
        model : str or file-like object
            A JSON/XML data model containing a potential-LAMMPS branch.
        pot_dir : str, optional
            The path to a directory containing any artifacts associated with
            the potential.  Default value is None, which assumes any required
            files will be in the working directory when LAMMPS is executed.
        """
        super().__init__(model, pot_dir=pot_dir)
    
    @property
    def modelroot(self):
        """str : The root element for the associated data model"""
        return 'potential-LAMMPS'

    @property
    def fileurls(self):
        """list : The URLs where the associated files can be downloaded"""
        urls = []
        for artifact in self.artifacts:
            urls.append(artifact.url)
        return urls
    
    @property
    def dois(self):
        """list : The publication DOIs associated with the potential"""
        return self.__dois

    @property
    def comments(self):
        """str : Descriptive comments detailing the potential information"""
        return self.__comments

    @property
    def print_comments(self):
        """str : LAMMPS print commands of the potential comments"""
        
        # Split defined comments
        lines = self.comments.split('\n')

        out = ''
        for line in lines:
            if line != '':
                out += f'print "{line}"\n'
        
        if len(self.dois) > 0:
            out += 'print "Publication(s) related to the potential:"\n'
            for doi in self.dois:
                out += f'print "https://doi.org/{doi}"\n'

        if len(self.fileurls) > 0:
            out += 'print "Parameter file(s) can be downloaded at:"\n'

            for url in self.fileurls:
                out += f'print "{url}"\n'
        return out

    def load(self, model, pot_dir=None):
        """
        Loads potential-LAMMPS data model info.
        
        Parameters
        ----------
        model : str or file-like object
            A JSON/XML data model containing a potential-LAMMPS branch.
        pot_dir : str, optional
            The path to a directory containing any artifacts associated with
            the potential.  Default value is None, which assumes any required
            files will be in the working directory when LAMMPS is executed.
        """
        # Call parent load to read model and some parameters
        super().load(model)
        
        if pot_dir is not None:
            self.pot_dir = pot_dir
        else:
            self.pot_dir = ''
        
        # Add artifacts
        self.__artifacts = []
        for artifact in self.model.aslist('artifact'):
            self.__artifacts.append(Artifact(model=DM([('artifact', artifact)])))

        # Read comments, if present
        self.__comments = self.model.get('comments', '')
        try:
            self.__dois = self.model['potential'].aslist('doi')
        except:
            print(self.model)
            raise ValueError('asdf')
        
        # Build lists of symbols, elements and masses
        self._elements = []
        self._symbols = []
        self._masses = []
        self._charges = []
        for atom in self.model.iteraslist('atom'):
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
            self._elements.append(element)
            self._symbols.append(symbol)
            self._masses.append(mass)
            self._charges.append(charge)
    
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
            i = self.symbols.index(symbol)
            if self._masses[i] is None:
                masses.append(atomic_mass(self._elements[i], prompt=prompt))
            else:
                masses.append(self._masses[i])
        
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

    def asdict(self):
        """Returns a flat dict of the metadata fields"""
        d = super().asdict()
        d['artifacts'] = self.artifacts

        return d

    def pair_info(self, symbols=None, masses=None, prompt=True, include_comments=True):
        """
        Generates the LAMMPS input command lines associated with the Potential
        and a list of atom-model symbols.
        
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
        include_comments : bool, optional
            Indicates if print command lines detailing information on the potential
            are to be included.  Default value is True.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential.
        """
        # Use all symbols if symbols is None
        if symbols is None:
            symbols = self.symbols
        else:
            # Normalize symbols
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

        info = ''
        
        # Add comment prints
        if include_comments:
            info += self.print_comments

        # Generate pair_style line
        terms = self.model['pair_style'].aslist('term')
        style_terms = self.__pair_terms(terms)
        
        info += f'pair_style {self.pair_style}{style_terms}\n'
        
        # Generate pair_coeff lines
        for coeff_line in self.model.iteraslist('pair_coeff'):
            if 'interaction' in coeff_line:
                interaction = coeff_line['interaction'].get('symbol', ['*', '*'])
            else:
                interaction = ['*', '*']
            
            # Always include coeff lines that act on all atoms in the system
            if interaction == ['*', '*']:
                coeff_symbols = self.symbols
                coeff_terms = self.__pair_terms(coeff_line.iteraslist('term'),
                                                symbols, coeff_symbols)
                
                info += f'pair_coeff * *{coeff_terms}\n'
                continue
            
            # Many-body potentials will contain a symbols term
            if len(coeff_line.finds('symbols')) > 0:
                many = True
            else:
                many = False
            
            # Treat as a many-body potential
            if many:
                coeff_symbols = interaction
                coeff_terms = self.__pair_terms(coeff_line.iteraslist('term'),
                                           symbols, coeff_symbols) + '\n'
                
                info += f'pair_coeff * *{coeff_terms}\n' 
            
            # Treat as pair potential
            else:
                coeff_symbols = interaction
                if len(coeff_symbols) != 2:
                    raise ValueError('Pair potential interactions need two listed elements')
                
                # Classic eam style is a special case
                if self.pair_style == 'eam':
                    if coeff_symbols[0] != coeff_symbols[1]:
                        raise ValueError('Only i==j interactions allowed for eam style')
                    for i in range(len(symbols)):
                        if symbols[i] == coeff_symbols[0]:
                            coeff_terms = self.__pair_terms(coeff_line.iteraslist('term'),
                                                           symbols, coeff_symbols)
                            
                            info += f'pair_coeff {i+1} {i+1}{coeff_terms}\n'
                
                # All other pair potentials
                else:
                    for i in range(len(symbols)):
                        for j in range(i, len(symbols)):
                            if ((symbols[i] == coeff_symbols[0] and symbols[j] == coeff_symbols[1])
                             or (symbols[i] == coeff_symbols[1] and symbols[j] == coeff_symbols[0])):
                                coeff_terms = self.__pair_terms(coeff_line.iteraslist('term'),
                                                                symbols, coeff_symbols)
                                
                                info += f'pair_coeff {i+1} {j+1}{coeff_terms}\n'
        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        # Generate additional command lines
        for command_line in self.model.iteraslist('command'):
            info += self.__pair_terms(command_line.iteraslist('term'),
                                         symbols, self.symbols).strip() + '\n'
        
        return info
    
    def __pair_terms(self, terms, system_symbols=None, coeff_symbols=None):
        """utility function used by self.pair_info() for composing lines from terms"""
        if system_symbols is None:
            system_symbols = []
        if coeff_symbols is None:
            coeff_symbols = []
        
        line = ''
        
        for term in terms:
            for ttype, tval in term.items():
                
                # Print options and parameters as strings
                if ttype == 'option' or ttype == 'parameter':
                    line += ' ' + str(tval)
                
                # Print files with pot_dir prefixes
                elif ttype == 'file':
                    line += ' ' + str(Path(self.pot_dir, tval))
                
                # Print all symbols being used for symbolsList
                elif ttype == 'symbolsList' and (tval is True or tval.lower() == 'true'):
                    for coeff_symbol in coeff_symbols:
                        if coeff_symbol in system_symbols:
                            line += ' ' + coeff_symbol
                
                # Print symbols being used with model in appropriate order for symbols
                elif ttype == 'symbols' and (tval is True or tval.lower() == 'true'):
                    for system_symbol in system_symbols:
                        if system_symbol in coeff_symbols:
                            line += ' ' + system_symbol
                        else:
                            line += ' NULL'
        
        return line
    
    def pair_data_info(self, filename, pbc, symbols=None, masses=None,
                       atom_style=None, units=None, prompt=True,
                       include_comments=True):
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
        include_comments : bool, optional
            Indicates if print command lines detailing information on the potential
            are to be included.  Default value is True.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential and a data
            file to read.
        """
        if units is None:
            units = self.units
        if atom_style is None:
            atom_style = self.atom_style

        # Initialize comment
        info = ''

        # Add units and atom_style values
        info += f'units {units}\n'
        info += f'atom_style {atom_style}\n\n'

        # Set boundary flags to p or m based on pbc values
        bflags = np.array(['m','m','m'])
        bflags[pbc] = 'p'
        info += f'boundary {bflags[0]} {bflags[1]} {bflags[2]}\n'
    
        # Set read_data command 
        info += f'read_data {filename}\n'

        # Set pair_info
        info += '\n'
        info += self.pair_info(symbols=symbols, masses=masses, prompt=prompt,
                               include_comments=include_comments)

        return info

    def pair_restart_info(self, filename, symbols=None, masses=None,
                          prompt=True, include_comments=True):
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
        include_comments : bool, optional
            Indicates if print command lines detailing information on the potential
            are to be included.  Default value is True.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential and a restart
            file to read.
        """
        # Add comment line
        info = '# Script prepared using atomman Python package\n\n'
    
        # Set read_data command 
        info += f'read_restart {filename}\n'

        # Set pair_info
        info += '\n'
        info += self.pair_info(symbols=symbols, masses=masses, prompt=prompt,
                               include_comments=include_comments)

        return info

    def download_files(self, pot_dir=None, verbose=False):
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
        verbose : bool, optional
            If True, will print the names of the files downloaded.
        
        Returns
        -------
        count : int
            The number of files downloaded.
        """

        count = 0
        if pot_dir is not None:
            self.pot_dir = pot_dir

        if verbose:
            print(len(self.artifacts), 'files to download')
        
        if len(self.artifacts) and not Path(self.pot_dir).is_dir():
            Path(self.pot_dir).mkdir(parents=True)

        for artifact in self.artifacts:
            r = requests.get(artifact.url)
            with open(Path(self.pot_dir, artifact.filename), 'wb') as f:
                f.write(r.content)
            if verbose:
                print('  -', artifact.filename, 'downloaded')
            count += 1
        
        return count
