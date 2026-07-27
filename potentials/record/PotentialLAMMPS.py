# Standard Python libraries
import io
from typing import Optional, Tuple, Union
from pathlib import Path
import datetime
import uuid

# https://numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_value, load_query
from yabadaba.tools import dict_insert

# local imports
from ..typing import lammps
from ..tools import aslist, atomic_mass, lammps_pair_styles
from .Artifact import Artifact
from .AtomInfo import AtomInfo
from .CommandLine import CommandLine, PairCoeffLine

class PotentialLAMMPS(Record):
    """
    Class for building LAMMPS input lines from a potential-LAMMPS data model.
    """

    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 pot_dir: Optional[str] = None,
                 **kwargs):
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
        pot_dir : str, optional
            The path to a directory containing any artifacts associated with
            the potential.  Default value is None, which assumes any required
            files will be in the working directory when LAMMPS is executed.
        """
        self.__pair_coeffs = []
        self.__commands = []
        self.__pair_style_terms = CommandLine()

        super().__init__(model=model, name=name, database=database, **kwargs)

        if pot_dir is not None:
            self.pot_dir = pot_dir
        else:
            self.pot_dir = ''
        
    @classmethod
    def paramfile(cls, paramfile, **kwargs):
        """
        Initializes a new PotentialsLAMMPS object for potentials that have
        pair_coeff lines of the format

            pair_coeff * * paramfile Sym1 Sym2
        
        Parameters
        ----------
        paramfile : str
            The name of the parameter file.
        **kwargs
            Any other PotentialLAMMPS initialization keyword parameters to set.
        """
        obj = cls(**kwargs)
        obj.pair_coeff_paramfile(paramfile)

        return obj

    @classmethod
    def eam(cls, paramfiles, **kwargs):
        """
        Initializes a new PotentialsLAMMPS object for potentials that have
        pair_coeff lines like the eam pair_style

            pair_coeff 1 1 paramfile1
            pair_coeff 2 2 paramfile2
        
        Parameters
        ----------
        paramfiles : list
            The names of the parameter files, one for each atomic model.
        **kwargs
            Any other PotentialLAMMPS initialization keyword parameters to set.
        """
        obj = cls(**kwargs)
        obj.pair_coeff_eam(paramfiles)

        return obj

    @classmethod
    def eim(cls, paramfile, **kwargs):
        """
        Initializes a new PotentialsLAMMPS object for potentials that have
        pair_coeff lines like the eim pair_style

            pair_coeff * * Sym1 Sym2 paramfile Sym1 Sym2

        Parameters
        ----------
        paramfile : str
            The name of the parameter file.
        **kwargs
            Any other PotentialLAMMPS initialization keyword parameters to set.
        """
        obj = cls(**kwargs)
        obj.pair_coeff_eim(paramfile)

        return obj

    @classmethod
    def meam(cls, libfile, paramfile=None, **kwargs):
        """
        Initializes a new PotentialsLAMMPS object for potentials that have
        pair_coeff lines like the meam pair_style

            pair_coeff * * libfile Sym1 Sym2 paramfile Sym1 Sym2

        Parameters
        ----------
        libfile : str
            The name of the primary library file.
        paramfile : str or None, optional
            The name of the additional parameter file, if there is one.
        **kwargs
            Any other PotentialLAMMPS initialization keyword parameters to set.
        """
        obj = cls(**kwargs)
        obj.pair_coeff_meam(libfile, paramfile=paramfile)

        return obj

    @classmethod
    def hybrid(cls, pots, scalars=None, **kwargs):
        """
        Initializes a new PotentialsLAMMPS object for potentials that have
        pair_styles hybrid. hybrid/overlay or hybrid/scaled.
        
        Parameters
        ----------
        pots : list
            A list of 2 or more PotentialLAMMPS objects to combine into a
            hybrid style.
        scalars : list or None
            The scalars to use with hybrid/scaled for each of the input
            potentials.  The values can be strings allowing for the
            specification of LAMMPS variables e.g. "v_scalar1"
        **kwargs
            Any other PotentialLAMMPS initialization keyword parameters to set.
            This method will try to detect values to use for those not given.
        """
        # Check pair_style and build list of incompatible component potentials
        pair_style = kwargs['pair_style']
        if pair_style == 'hybrid':
            unsupported_styles = ['hybrid/overlay', 'hybrid/scaled', 'hybrid/molecule', 'kim']
        elif pair_style == 'hybrid/overlay' or pair_style == 'hybrid/scaled':
            unsupported_styles = ['hybrid', 'hybrid/scaled', 'hybrid/molecule', 'kim']
        else:
            raise ValueError('this method only works for hybrid, hybrid/overlay and hybrid/scaled potentials')

        # Check number of pots
        if len(pots) < 2:
            raise ValueError('need at least 2 input potentials to build a hybrid potential')

        # Check scalars
        if pair_style == 'hybrid/scaled':
            if len(pots) != len(scalars):
                raise ValueError('hybrid/scaled requires a scalar for each potential')
        else:
            scalars = [None for i in range(len(pots))]
        
        # Initialize potential information
        units = kwargs.get('units', pots[0].units)
        atom_style = kwargs.get('atom_style', pots[0].atom_style)
        dois = []
        artifacts = []
        commentslist = []
        allsymbols = False
        pot_dir = ''

        # Check/combine each potential's information
        for pot in pots:
            if not isinstance(pot, cls):
                raise TypeError(f'hybrid only supports combining PotentialLAMMPS objects')
            if pot.pair_style in unsupported_styles:
                raise ValueError(f'cannot create {pair_style} from {", ".join(unsupported_styles)}')
            if pot.units != units:
                raise ValueError('input potentials have different units settings!')
            if 'atom_style' not in kwargs and pot.atom_style != atom_style:
                raise ValueError('input potentials have different atom_style settings!')
            if pot.dois is not None:
                dois.extend(pot.dois)
            if pot.artifacts is not None:
                artifacts.extend(pot.artifacts)
            if pot.comments is not None and pot.comments != '':
                commentslist.append(pot.comments)
            allsymbols = allsymbols or pot.allsymbols
            if 'pot_dir' not in kwargs and pot.pot_dir != '':
                if pot_dir != '' and pot_dir != pot.pot_dir:
                    raise ValueError('input potentials have different pot_dir settings!')
                pot_dir = pot.pot_dir
        
        # Build combined atoms list and search for hybrid styles
        symbols = []
        atoms = []
        #hybrid_index = None
        for i, pot in enumerate(pots):
            for atom in pot.atoms:
                if atom.symbol is not None:
                    symbol = atom.symbol
                elif atom.elemet is not None:
                    symbol = atom.element
                else:
                    raise ValueError('atom found without symbol or element!')
        
                if symbol not in symbols:
                    atoms.append(atom)
                    symbols.append(symbol)

        # Fill in missing kwarg values
        kwargs['dois'] = kwargs.get('dois', dois)
        kwargs['comments'] = kwargs.get('comments', '\n'.join(commentslist))
        kwargs['units'] = kwargs.get('units', units)
        kwargs['atom_style'] = kwargs.get('atom_style', atom_style)
        kwargs['allsymbols'] = kwargs.get('allsymbols', allsymbols)
        kwargs['atoms'] = kwargs.get('atoms', atoms)
        kwargs['artifacts'] = kwargs.get('artifacts', artifacts)
        kwargs['pot_dir'] = kwargs.get('pot_dir', pot_dir)

        # Initialize the hybrid potential
        newpot = cls(**kwargs)

        # Loop over pots to build pair_style and pair_coeff lines
        for pot, scalar in zip(pots, scalars):
            
            # For a non-hybrid component potential
            if not pot.pair_style.startswith('hybrid'):
                # Add scalar if hybrid/scalar
                if pair_style == 'hybrid/scaled':
                    newpot.pair_style_terms.add_term('option', scalar)

                # Add pair_style as a term
                newpot.pair_style_terms.add_term('option', pot.pair_style)
            
                # Copy any other pair_style terms from pot to newpot
                for term in pot.pair_style_terms.terms:
                    for k,v in term.items():
                        newpot.pair_style_terms.add_term(k, v)
            
            # For a hybrid component potential
            else:
                # Copy pair_style terms from pot to newpot
                for term in pot.pair_style_terms.terms:
                    for k,v in term.items():
                        # Insert scalar before any terms matching a known pair_style
                        if pair_style == 'hybrid/scaled' and v in lammps_pair_styles:
                            newpot.pair_style_terms.add_term('option', scalar)
                        newpot.pair_style_terms.add_term(k, v)

            # Loop over pot's pair_coeff lines.
            for pair_coeff in pot.pair_coeffs:
                
                # Identify the interaction symbols for the pair_coeff line
                interaction = pair_coeff.interaction
                if interaction is None and len(pot.symbols) != len(newpot.symbols):
                    interaction = pot.symbols
                    
                # Create new pair_coeff interaction
                newpot.add_pair_coeff(interaction=interaction)
                
                # Add pot's pair_style to newpot's pair_style terms
                if not pot.pair_style.startswith('hybrid'):
                    newpot.pair_coeffs[-1].add_term('option', pot.pair_style)
                
                # Copy any other pair_coeff terms from pot to newpot
                for term in pair_coeff.terms:
                    for k,v in term.items():
                        newpot.pair_coeffs[-1].add_term(k, v)

            # Loop over pot's extra commands
            for command in pot.commands:
                # Create new command interaction
                newpot.add_command()
                # Copy command terms from pot to newpot
                for term in command.terms:
                    for k,v in term.items():
                        newpot.commands[-1].add_term(k, v)

        return newpot

    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'potential_LAMMPS'

    @property
    def modelroot(self) -> str:
        """str : The root element for the associated data model"""
        return 'potential-LAMMPS'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'potential_LAMMPS.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'potential_LAMMPS.xsd')

    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'key')
        self._add_value('str', 'id')
        self._add_value('str', 'url', modelpath='URL')
        self._add_value('str', 'status', allowedvalues=('superseded', 'retracted'))
        self._add_value('str', 'potkey', modelpath='potential.key')
        self._add_value('str', 'potid', modelpath='potential.id')
        self._add_value('str', 'poturl', modelpath='potential.URL')
        self._add_value('strlist', 'dois', modelpath='potential.doi')
        self._add_value('longstr', 'comments')
        self._add_value('str', 'units', defaultvalue='metal')
        self._add_value('str', 'atom_style', defaultvalue='atomic')
        self._add_value('bool', 'allsymbols', metadatakey=False)
        self._add_value('record', 'atoms', recordclass=AtomInfo,
                        modelpath='atom', metadatakey=False)
        self._add_value('str', 'pair_style', modelpath='pair_style.type')
        self._add_value('record', 'artifacts', recordclass=Artifact,
                        modelpath='artifact')
        
        # Remove Artifact queries
        self.get_value('artifacts').queries.pop('url')
        self.get_value('artifacts').queries.pop('label')
        

    @property
    def defaultname(self) -> str:
        return self.id

    @property
    def pair_coeffs(self) -> list:
        return self.__pair_coeffs

    @property
    def commands(self) -> list:
        return self.__commands

    @property
    def pair_style_terms(self) -> CommandLine:
        """LAMMPSCommandLine : Any extra terms for the LAMMPS pair_style command line."""
        return self.__pair_style_terms
    
    @property
    def pot_dir(self):
        """str : The directory containing files associated with a given potential."""
        return self.__pot_dir

    @pot_dir.setter
    def pot_dir(self, value: str):
        self.__pot_dir = str(value)

    @property
    def fileurls(self) -> list:
        """list : The URLs where the associated files can be downloaded"""
        urls = []
        for artifact in self.artifacts:
            urls.append(artifact.url)
        return urls

    @property
    def symbols(self) -> list:
        """list of str : All atom-model symbols."""
        symbols = []
        for atom in self.atoms:
            symbols.append(atom.symbol)
        return symbols
    

    def set_values(self, **kwargs):
        """
        Set multiple object attributes at the same time.

        Parameters
        ----------
        **kwargs: any
            Any parameters for the record that you wish to set values for.
        """
        
        if 'artifacts' in kwargs:
            self.get_value('artifacts').value = []
            artifacts = kwargs.pop('artifacts')
            for artifact in aslist(artifacts):
                if isinstance(artifact, Artifact):
                    self.get_value('artifacts').value.append(artifact)
                else:
                    raise TypeError('artifacts must be Artifact objects')
        


        super().set_values(**kwargs)

        # Build atoms objects from symbols, elements, masses and charges fields
        if 'elements' in kwargs or 'symbols' in kwargs:

            # Handle elements            
            if 'elements' in kwargs:
                elements = aslist(kwargs['elements'])
            else:
                elements = [None] * len(aslist(kwargs['symbols']))

            # Handle symbols
            if 'symbols' in kwargs:
                symbols = aslist(kwargs['symbols'])
            else:
                # Assume symbols=elements if not given
                symbols = elements
            
            # Handle masses 
            if 'masses' in kwargs:
                masses = aslist(kwargs['masses'])
            elif 'elements' not in kwargs:
                raise ValueError('masses and/or elements must be given with symbols')
            else:
                masses = [None] * len(symbols)

            # Handle charges
            if 'charges' in kwargs:
                charges = aslist(kwargs['charges'])
            else:
                charges = [None] * len(symbols)

            # Check lengths of inputs
            if (len(elements) != len(symbols) or 
                len(elements) != len(masses) or 
                len(elements) != len(charges)):
                raise ValueError('Different number of values given for elements, symbols, masses, charges')

            # Add atoms
            for symbol, element, mass, charge in zip(symbols, elements, masses, charges):
                self.add_atom(symbol=symbol, element=element, mass=mass, charge=charge)

        # Throw error if masses or charges given without elements or symbols
        elif 'masses' in kwargs or 'charges' in kwargs:
            raise ValueError('masses and charges requires symbols and/or elements to be given')


    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        meta = super().metadata()

        meta['symbols'] = self.symbols
        meta['elements'] = self.elements()

        return meta


    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        queries = super().queries
        
        queries.update({
            'symbols': load_query(
                style='list_contains',
                name='symbols',
                path=f'{self.modelroot}.atom.symbol',
                description="search based on atomic model symbols"),
            'elements': load_query(
                style='list_contains',
                name='elements',
                path=f'{self.modelroot}.atom.element',
                description="search based on atomic model elements"),
        })

        return queries

    @property
    def print_comments(self) -> str:
        """str : LAMMPS print commands of the potential comments"""

        # Split defined comments
        if self.comments is None:
            lines = ['']
        else:
            lines = self.comments.split('\n')

        out = ''
        for line in lines:
            if line != '':
                out += f'print "{line}"\n'
        
        if self.dois is not None and len(self.dois) > 0:
            out += 'print "Publication(s) related to the potential:"\n'
            for doi in self.dois:
                out += f'print "https://doi.org/{doi}"\n'

        if self.fileurls is not None and len(self.fileurls) > 0:
            out += 'print "Parameter file(s) can be downloaded at:"\n'

            for url in self.fileurls:
                out += f'print "{url}"\n'
        return out
 
    def add_atom(self, **kwargs):
        """
        Initializes a new AtomInfo object and appends it to the atoms list.
        """
        newatom = AtomInfo(**kwargs)
        for atom in self.atoms:
            if atom.symbol == newatom.symbol:
                raise ValueError(f'AtomInfo with symbol {atom.symbol} already exists')
        self.atoms.append(newatom)

    def add_pair_coeff(self, **kwargs):
        """
        Initializes a new PairCoeffLine object and appends it to the pair_coeffs list.
        """
        self.pair_coeffs.append(PairCoeffLine(**kwargs))

    def add_command(self, **kwargs):
        """
        Initializes a new CommandLine object and appends it to the commands list.
        """
        self.commands.append(CommandLine(**kwargs))

    def build_model(self) -> DM:
        
        # Build primary model content
        model = super().build_model()
        

        # Insert pair_style terms content
        if len(self.pair_style_terms.terms) > 0:
            model[self.modelroot]['pair_style']['term'] = self.pair_style_terms.build_model()['term']

        # Insert pair_coeff content
        if len(self.pair_coeffs) > 0:
            pcmodel = DM()
            for pair_coeff in self.pair_coeffs:
                pcmodel.append('pair_coeff', pair_coeff.build_model())
            dict_insert(model[self.modelroot], 'pair_coeff', pcmodel['pair_coeff'],
                        after='pair_style')
        
        # Insert extra command line content
        if len(self.commands) > 0:
            cmodel = DM()
            for command in self.commands:
                cmodel.append('command', command.build_model())
            dict_insert(model[self.modelroot], 'command', cmodel['command'],
                        after='pair_coeff')
            
        return model


    def load_model(self,
                   model: Union[str, io.IOBase, DM],
                   name: Optional[str] = None,
                   pot_dir: Optional[str] = None):
        """
        Loads potential-LAMMPS data model info.
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict
            A JSON/XML data model for the content.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        pot_dir : str, optional
            The path to a directory containing any artifacts associated with
            the potential.  Default value is None, which assumes any required
            files will be in the working directory when LAMMPS is executed.
        """
        # Call parent load_model
        super().load_model(model, name=name)
        model = self.model

        # Set pot_dir if given
        if pot_dir is not None:
            self.pot_dir = pot_dir
        else:
            self.pot_dir = ''

        self.__pair_style_terms = CommandLine()
        if 'term' in model[self.modelroot]['pair_style']:
            self.pair_style_terms.load_model(model[self.modelroot]['pair_style'])

        self.__pair_coeffs = []
        for pair_coeff in model[self.modelroot].aslist('pair_coeff'):
            self.add_pair_coeff()
            line = self.pair_coeffs[-1]
            line.load_model(pair_coeff)

        self.__commands = []
        for command in model[self.modelroot].aslist('command'):
            commandline = CommandLine()
            commandline.load_model(command)
            self.commands.append(commandline)
   
    @property
    def symbolsets(self) -> list:
        """list : The sets of symbols that correspond to all related potentials"""
        return [self._symbols]
    
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
    
    def natypes(self,
                symbols: Union[str, list, None] = None,
                atypes: Optional[list] = None) -> int:
        """
        Returns the correct number of atom types to use when generating or
        reading in atoms in LAMMPS.

        Parameters
        ----------
        symbols : list of str, optional
            A list of atom-model symbols.  If None (default), will use all of
            the potential's symbols.
        atypes : list of int, optional
            The per-atom atom type numbers associated with a system.
            If not given, will only consider symbols.

        Returns
        -------
        int
            The number of atom types to use in LAMMPS.
        """
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = self.normalize_symbols(symbols)
        if atypes is None:
            atypes = [1]

        return max(max(atypes), len(symbols))

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
        
    def pair_info(self,
                  symbols: Union[str, list, None] = None,
                  masses: Union[float, list, None] = None,
                  prompt: bool = False,
                  comments: bool = True,
                  lammps_date: datetime.date = datetime.date(2020, 10, 29)
                  ) -> str:
        """
        Generates the LAMMPS input command lines associated with the Potential
        and a list of atom-model symbols.
        
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
        lammps_date : datetime, optional
            The LAMMPS version date that is to be used.  The generated commands
            may differ based on the version of LAMMPS used.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential.
        """

        # Use all symbols if symbols is None
        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)

        # Check length of given masses
        if masses is not None:
            masses = aslist(masses)
            assert len(masses) == len(symbols), 'supplied masses must be same length as symbols'
        else:
            masses = [None,]

        # Normalize symbols and masses
        symbols = self.normalize_symbols(symbols)
        for i in range(len(masses), len(symbols)):
            masses += [None,]
        
        # Change None mass values to default values
        for i in range(len(masses)):
            if masses[i] is None:
                masses[i] = self.masses(symbols[i], prompt=prompt)[0]

        info = ''
        
        # Add comment prints
        if comments:
            info += self.print_comments
            info += '\n'

        # Generate pair_style line
        info += f'pair_style {self.pair_style} {self.pair_style_terms.build_command(self.pot_dir)}'
        
        # Generate pair_coeff lines
        for pair_coeff in self.pair_coeffs:
            info += pair_coeff.build_command(self.pot_dir, symbols,
                                             is_eam = (self.pair_style == 'eam'))
        info += '\n'
            
        # Generate mass lines
        for i in range(len(masses)):
            info += f'mass {i+1} {masses[i]}\n'
        info +='\n'

        # Generate additional command lines
        for command_line in self.commands:
            info += command_line.build_command(self.pot_dir)
        
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
                       lammps_date: datetime.date = datetime.date(2020, 10, 29),
                       tilt_large: bool = False
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
        lammps_date : datetime, optional
            The LAMMPS version date that is to be used.  The generated commands
            may differ based on the version of LAMMPS used.
        tilt_large : bool, optional
            If True, then the box command will include the tilt large option for
            older LAMMPS versions to allow for larger tilt factors.  Default value
            is False.

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

        # Add box tilt large command
        if lammps_date < datetime.date(2022, 12, 22) and tilt_large:
            info += 'box tilt large\n\n'

        # Add units and atom_style values
        info += f'units {units}\n'
        info += f'atom_style {atom_style}\n\n'

        # Set boundary flags to p or m based on pbc values
        bflags = np.array(['m','m','m'])
        bflags[pbc] = 'p'
        info += f'boundary {bflags[0]} {bflags[1]} {bflags[2]}\n'
    
        # Set read_data command
        if isinstance(filename, str):
            info += f'read_data {filename}\n'

        # Set pair_info
        info += '\n'
        info += self.pair_info(symbols=symbols, masses=masses, prompt=prompt,
                               comments=comments)

        return info

    def pair_lib_info(self,
                      lmp: lammps.lammps,
                      pbc: npt.ArrayLike,
                      region_params: list,
                      atype: list,
                      x: list,
                      natypes: Optional[int] = None,
                      natoms: Optional[int] = None,
                      v: Optional[list] = None,
                      symbols: Union[str, list, None] = None,
                      masses: Union[float, list, None] = None,
                      atom_style: Optional[str] = None,
                      units: Optional[str] = None,
                      prompt: bool = False,
                      comments: bool = True,
                      lammps_date: Optional[datetime.date] = None,
                      tilt_large: bool = False,
                      clear: bool = True,
                      ):
        """
        For interactive LAMMPS sessions, generates the LAMMPS command lines
        associated with both a potential and system parameters.

        Parameters
        ----------
        lmp: lammps.lammps
            The lammps library object for the current session.
        pbc : array-like object
            The three boolean periodic boundary conditions, or three strings
            giving the specific LAMMPS boundary settings.
        region_params : list
            The parameters for the LAMMPS region command to define the system:
            [xlo, xhi, ylo, yhi, zlo, zhi, xy, xz, yz].
        atype : list
            The list of integer atom types for each atom in the system.
        x : list
            A flattened list of the positional coordinates for each atom in
            the system.
        natypes : int, optional
            The number of atom types in the system.  If not given, will be
            inferred from the atype list.
        natoms : int, optional
            The number of atoms in the system.  If not given, will be inferred
            from the atype list.
        v : list, optional
            A flattened list of the velocity components for each atom in the
            system.  If not given, then no velocity information will be
            included in the generated commands.
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
        lammps_date : datetime, optional
            The LAMMPS version date that is to be used.  If not given, will check
            the version date for the lmp object.
        tilt_large : bool, optional
            If True, then the box command will include the tilt large option for
            older LAMMPS versions to allow for larger tilt factors.  Default value
            is False.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential and a data
            file to read.
        """
        # Set default values
        if lammps_date is None:
            lammps_date = datetime.date.fromisoformat(str(lmp.version()))
        if units is None:
            units = self.units
        if atom_style is None:
            atom_style = self.atom_style
        if natoms is None:
            natoms = len(atype)
        if natypes is None:
            natypes = self.natypes(symbols=symbols, atypes=atype)

        # Change pbc booleans to LAMMPS boundary flags if needed
        pbc = np.asarray(pbc)
        if pbc.dtype == bool:
            bflags = np.array(['m','m','m'])
            bflags[pbc] = 'p'
            pbc = bflags

        # Base settings
        if clear:
            lmp.cmd.clear()
        if lammps_date < datetime.date(2022, 12, 22) and tilt_large:
            lmp.cmd.box('tilt', 'large')
        lmp.cmd.units(units)
        lmp.cmd.atom_style(atom_style)
        
        # Create box
        lmp.cmd.boundary(*pbc)
        lmp.cmd.region('box', 'prism', *region_params)
        lmp.cmd.create_box(natypes, 'box')

        # Create atoms
        if natoms > 0:
            lmp.create_atoms(natoms, atomid=None, atype=atype, x=x, v=v)

        # Set pair_info
        pair_info = self.pair_info(symbols=symbols, masses=masses, prompt=prompt,
                                    comments=comments)
        lmp.commands_string(pair_info)
       

    def pair_restart_info(self,
                          filename: Union[str, Path],
                          symbols: Union[str, list, None] = None,
                          masses: Union[float, list, None] = None,
                          units: Optional[str] = None,
                          prompt: bool = False,
                          comments: bool = True,
                          lammps_date: datetime.date = datetime.date(2020, 10, 29),
                          tilt_large: bool = False,
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
        lammps_date : datetime, optional
            The LAMMPS version date that is to be used.  The generated commands
            may differ based on the version of LAMMPS used.
        tilt_large : bool, optional
            If True, then the box command will include the tilt large option for
            older LAMMPS versions to allow for larger tilt factors.  Default value
            is False.

        Returns
        -------
        str
            The LAMMPS input command lines that specifies the potential and a restart
            file to read.
        """
        # Add comment line
        info = '# Script prepared using atomman Python package\n\n'
    
        # Add box tilt large command
        if lammps_date < datetime.date(2022, 12, 22) and tilt_large:
            info += 'box tilt large\n\n'

        # Set read_data command 
        info += f'read_restart {filename}\n'

        # Set pair_info
        info += '\n'
        info += self.pair_info(symbols=symbols, masses=masses, prompt=prompt,
                               comments=comments)

        return info

    def get_file(self,
                 filename: Union[str, Path],
                 localroot: Union[str, Path, None] = None):
        """
        Retrieves a file either locally or from the record's tar archive.

        Parameters
        ----------
        filename : str or Path
            The name/path for the file.  For local files, this is taken
            relative to localroot.  For files in the tar archive, this is taken
            relative to the tar's root directory which is always named for the
            record, i.e., {self.name}/{filename}.
        localroot : str, Path or None, optional
            The local root directory that filename (if it exists) is relative
            to.  The default value of None will use the pot_dir directory.
        
        Raises
        ------
        ValueError
            If filename exists in the tar but is not a file.

        Returns
        -------
        io.IOBase
            A file-like object in binary read mode that allows for the file
            contents to be read.
        """
        # Set default root path
        if localroot is None:
            localroot = self.pot_dir

        return super().get_file(filename, localroot)








    def pair_coeff_paramfile(self,
                             paramfile: Union[str, Path]):
        """
        Defines the LAMMPS pair_coeff lines for a potential that relies on a
        single parameter file with the pair_coeff format:

            pair_coeff * * paramfile Sym1 Sym2     
        
        Note that this is the most common pair_coeff format for potentials that
        rely on a single parameter file.

        Parameters
        ----------
        paramfile : str or Path
            The file name or path to the potential's parameter file.  If a full path
            is given, then the pot_dir will be set to the paramfile's parent directory.
            If only the file name is given, then the pot_dir can be set separately.
        """
        if len(self.pair_coeffs) > 0:
            raise ValueError('pair coeffs already set for this potential!')

        pair_coeff = PairCoeffLine()

        paramfile = Path(paramfile)
        if paramfile.name != str(paramfile):
            self.pot_dir = paramfile.parent
            paramfile = paramfile.name
        
        pair_coeff.add_term('file', paramfile)
        pair_coeff.add_term('symbols', True)

        self.pair_coeffs.append(pair_coeff)

    def pair_coeff_eam(self,
                       paramfiles: Union[str, Path, list],
                       symbols: Union[str, list, None] = None):
        """
        Defines the LAMMPS pair_coeff lines for potentials of the classic eam
        pair_style only, which uses pair_coeff lines of the form:
        
            pair_coeff 1 1 paramfile1
            pair_coeff 2 2 paramfile2

        Note: This is only for pair_style eam!  Use pair_coeff_paramfile for
        eam/alloy, eam/fs, eam/cd, etc.

        Parameters
        ----------
        paramfiles : str, Path or list
            The file name(s) or path(s) to the potential's parameter file(s).
            There should be one parameter file for each symbol/element model.
            If full paths are given, then the files should have the same parent
            directory as it will be used to set the pot_dir.
        symbols : str, list or None, optional
            The list of symbol models to correspond to the parameter files.  If
            None, then the symbols already set to the object will be used.
        """
        if len(self.pair_coeffs) > 0:
            raise ValueError('pair coeffs already set for this potential!')
        
        paramfiles = aslist(paramfiles)

        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)

        if len(symbols) != len(paramfiles):
            raise ValueError('Number of paramfiles != number of symbols')

        parent = None
        for paramfile in paramfiles:
            paramfile = Path(paramfile)
            if paramfile.name != str(paramfile):
                if parent is not None:
                    if str(parent) != str(paramfile.parent):
                        raise ValueError('Different paramfile parent directories!')
                    parent = paramfile.parent
                paramfile = paramfile.name
        if parent is not None:
            self.pot_dir = parent
        
        for symbol, paramfile in zip(symbols, paramfiles):
            pair_coeff = PairCoeffLine()
            pair_coeff.interaction = (symbol, symbol)
            pair_coeff.add_term('file', paramfile)
            self.pair_coeffs.append(pair_coeff)



    def pair_coeff_eim(self,
                       paramfile,
                       symbols: Union[str, list, None] = None):
        """
        Defines the LAMMPS pair_coeff lines for the eim pair_style which has the
        form:
        
            pair_coeff * * Sym1 Sym2 paramfile Sym1 Sym2
        
        Where the first Sym list maps the symbols to the paramfile model types and
        the second maps the symbols to the system's atom types.
        
        Parameters
        ----------
        paramfile : str or Path
            The file name or path to the potential's parameter file.  If a full path
            is given, then the pot_dir will be set to the paramfile's parent directory.
            If only the file name is given, then the pot_dir can be set separately.
        symbols : str, list or None, optional
            The list of symbol models to map to the parameter file's models, i.e. the
            first Sym list in the pair_coeff line.  If None, then it is assumed to
            match the list of symbols already set to the object. Note that order matters! 
        """
        if len(self.pair_coeffs) > 0:
            raise ValueError('pair coeffs already set for this potential!')

        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)
        symbolslist = ' '.join(symbols)

        pair_coeff = PairCoeffLine()

        paramfile = Path(paramfile)
        if paramfile.name != str(paramfile):
            self.pot_dir = paramfile.parent
            paramfile = paramfile.name
        
        pair_coeff.add_term('option', symbolslist)
        pair_coeff.add_term('file', paramfile)
        pair_coeff.add_term('symbols', True)

        self.pair_coeffs.append(pair_coeff)


    def pair_coeff_meam(self,
                        libfile : Union[str, Path],
                        paramfile: Union[str, Path, None] = None,
                        symbols: Union[str, list, None] = None):
        """
        Defines the LAMMPS pair_coeff lines for the meam pair_style which has the
        form:
        
            pair_coeff * * libfile Sym1 Sym2 paramfile Sym1 Sym2
        
        Where the first Sym list maps the symbols to the paramfile model types and
        the second maps the symbols to the system's atom types.
        
        Parameters
        ----------
        libfile : str or Path
            The file name or path to the potential's library file.  If a full path
            is given, then the pot_dir will be set to the libfile's parent directory.
            If only the file name is given, then the pot_dir can be set separately.
        paramfile : str, Path or None
            The file name or path to the potential's parameter file, if it has one.
            If a full path is given, then the pot_dir will be set to the paramfile's
            parent directory.  If only the file name is given, then the pot_dir can
            be set separately. If None (default), then only the libfile will be used.
        symbols : str, list or None, optional
            The list of symbol models to map to the parameter file's models, i.e. the
            first Sym list in the pair_coeff line.  If None, then it is assumed to
            match the list of symbols already set to the object. Note that order matters! 
        """
        if len(self.pair_coeffs) > 0:
            raise ValueError('pair coeffs already set for this potential!')

        if symbols is None:
            symbols = self.symbols
        else:
            symbols = aslist(symbols)
        symbolslist = ' '.join(symbols)

        pair_coeff = PairCoeffLine()

        parent = None
        libfile = Path(libfile)
        if libfile.name != str(libfile):
            parent = libfile.parent
            libfile = libfile.name

        if paramfile is not None:
            paramfile = Path(paramfile)
            if paramfile.name != str(paramfile):
                if parent != paramfile.name:
                    raise ValueError('differet parent directories for libfile and paramfile')
                paramfile = paramfile.name
        
        if parent is not None:
            self.pot_dir = parent
        
        pair_coeff.add_term('file', libfile)
        pair_coeff.add_term('option', symbolslist)
        if paramfile is None:
            pair_coeff.add_term('option', 'NULL')
        else:
            pair_coeff.add_term('file', paramfile)
        pair_coeff.add_term('symbols', True)

        self.pair_coeffs.append(pair_coeff)
