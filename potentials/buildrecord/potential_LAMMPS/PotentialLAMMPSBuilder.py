# coding: utf-8
# Standard libraries
import uuid
from typing import Generator, Optional, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# Local imports
from ...tools import aslist
from ... import load_record
from ...record.Artifact import Artifact
from ...record.PotentialLAMMPS import PotentialLAMMPS

class PotentialLAMMPSBuilder(object):
    """
    Template class for generating potential_LAMMPS records for different pair styles.

    Note: terms for pair_coeff lines are not included as they are style-specific.
    """

    def __init__(self, **kwargs):
        """
        Builder class initializer.
        
        Parameters
        ----------
        id : str, optional
            A human-readable identifier to name the LAMMPS potential
            implementation.  Must be set in order to save to the database as
            the id is used as the potential's file name.
        key : str, optional
            A UUID4 code to uniquely identify the LAMMPS potential
            implementation.  If not specified, a new UUID4 code is
            automatically generated.
        url : str, optional
            A URL where an online copy of the record can be found.
        potid : str, optional
            A human-readable identifier to refer to the conceptual potential
            model that the potential is based on.  This should be shared by
            alternate implementations of the same potential.
        potkey : str, optional
            A UUID4 code to uniquely identify the conceptual potential model.
            This should be shared by alternate implementations of the same
            potential. If not specified, a new UUID4 code is automatically
            generated.
        poturl : str, optional
            A URL where an online copy of the potential model record can be
            found.
        units : str, optional
            The LAMMPS units option to use.
        atom_style : str, optional
            The LAMMPS atom_style option to use.
        pair_style : str, optional
            The LAMMPS pair_style option to use.
        pair_style_terms :  list, optional
            Any other terms that appear on the pair_style line (like cutoff)
            if needed.
        status : str, optional
            Indicates if the implementation is 'active' (valid and current),
            'superseded' (valid, but better ones exist), or 'retracted'
            (invalid). Default value is 'active'.
        comments : str, optional
            Descriptive information about the potential.
        dois : str or list, optional
            Any DOIs associated with the potential.
        allsymbols : bool, optional
            Flag indicating if the coefficient lines must be defined for every
            particle model in the potential even if those particles are not
            used.  Default value is False as most pair_styles do not require
            this.
        elements : str or list, optional
            The elemental symbols associated with each particle model if the
            particles represent atoms.
        masses : float or list, optional
            The masses of each particle.  Optional if elements is given as
            standard values can be used.
        charges : float or list, optional
            The static charges to assign to each particle, if the model calls
            for it.
        symbols : str or list, optional
            The symbols used to identify each unique particle model. Optional
            if elements is given and the particle symbols are the same as the
            elemental symbols.
        command_terms : list, optional
            Allows any other LAMMPS command lines that must be set for the
            potential to work properly to be set.  Each command line should be
            given as a list of terms, and multiple command lines given as a
            list of lists.
        artifacts : potential.Artifact or list, optional
            Artifact objects detailing any associated parameter or data files
            and the URLs where they can be downloaded from.
        """
        self.id = kwargs.pop('id', None)
        self.key = kwargs.pop('key', None)
        self.url = kwargs.pop('url', None)

        self.potid = kwargs.pop('potid', None)
        self.potkey = kwargs.pop('potkey', None)
        self.poturl = kwargs.pop('poturl', None)
        
        self.units = kwargs.pop('units', None)
        self.atom_style = kwargs.pop('atom_style', None)
        self.pair_style = kwargs.pop('pair_style', None)
        
        self.allsymbols = kwargs.pop('allsymbols', False)
        self.status = kwargs.pop('status', 'active')
        self.comments = kwargs.pop('comments', None)
        self.dois = kwargs.pop('dois', None)

        self.symbols = kwargs.pop('symbols', None)
        self.elements = kwargs.pop('elements', None)
        self.masses = kwargs.pop('masses', None)
        self.charges = kwargs.pop('charges', None)
        
        self.pair_style_terms = kwargs.pop('pair_style_terms', None)
        self.command_terms = kwargs.pop('command_terms', None)

        self.artifacts = kwargs.pop('artifacts', None)

        if len(kwargs) > 0:
            raise ValueError(f'Unrecognized kwargs found: {kwargs.keys()}')

    @property
    def id(self) -> Optional[str]:
        """str: Human-readable id for LAMMPS implementation of the potential."""
        return self.__id

    @id.setter
    def id(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__id = value

    @property
    def key(self) -> str:
        """Unique UUID4 key for the LAMMPS implementation."""
        return self.__key

    @key.setter
    def key(self, value: Optional[str]):
        if value is None:
            value = uuid.uuid4()
        self.__key = str(value)

    @property
    def url(self) -> Optional[str]:
        """str: URL for an online copy of the record."""
        return self.__url

    @url.setter
    def url(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__url = value

    @property
    def potid(self) -> Optional[str]:
        """Human-readable id for the potential model."""
        return self.__potid

    @potid.setter
    def potid(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__potid = value

    @property
    def potkey(self) -> str:
        """Unique UUID4 key for the potential model."""
        return self.__potkey

    @potkey.setter
    def potkey(self, value: Optional[str]):
        if value is None:
            value = uuid.uuid4()
        self.__potkey = str(value)

    @property
    def poturl(self) -> Optional[str]:
        """str: URL for an online copy of the potential model record."""
        return self.__poturl

    @poturl.setter
    def poturl(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__poturl = value

    @property
    def units(self) -> Optional[str]:
        """str : LAMMPS units option."""
        return self.__units

    @units.setter
    def units(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__units = value

    @property
    def atom_style(self) -> Optional[str]:
        """str : LAMMPS atom_style option."""
        return self.__atom_style

    @atom_style.setter
    def atom_style(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__atom_style = value

    @property
    def pair_style(self) -> Optional[str]:
        """str : LAMMPS pair_style option."""
        return self.__pair_style

    @pair_style.setter
    def pair_style(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__pair_style = value

    @property
    def allsymbols(self) -> bool:
        """bool : Flag indicating if the coefficient lines must be defined for every particle model in the potential even if those particles are not used."""
        return self.__allsymbols

    @allsymbols.setter
    def allsymbols(self, value: Union[str, bool]):
        if isinstance(value, bool):
            self.__allsymbols = value
        elif isinstance(value, str):
            if value.lower() == 'true':
                self.__allsymbols = True
            elif value.lower() == 'false':
                self.__allsymbols = False
            else:
                raise ValueError(f'Invalid allsymbols value "{value}"')
        else:
            raise TypeError('allsymbols must be bool or bool string.')   

    @property
    def status(self) -> str:
        """str : The status of the LAMMPS potential: active, superseded or retracted"""
        return self.__status

    @status.setter
    def status(self, value: str):
        if value not in ['active', 'superseded', 'retracted']:
            raise ValueError('Invalid status: allowed values are active, superseded, and retracted')
        self.__status = value

    @property
    def comments(self) -> Optional[str]:
        """str : Descriptive information about the potential"""
        return self.__comments

    @comments.setter
    def comments(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__comments = value

    @property
    def dois(self) -> list:
        """list : Any DOIs associated with the potential"""
        return self.__dois

    @dois.setter
    def dois(self, value: Union[str, list, None]):
        if value is not None:
            self.__dois = aslist(value)
        else:
            self.__dois = []

    @property
    def symbols(self) -> Optional[list]:
        """list : The interaction models defined by the potential"""
        return self.__symbols

    @symbols.setter
    def symbols(self, value: Union[str, list, None]):
        if value is not None:
            value = aslist(value)
        self.__symbols = value

    @property
    def elements(self) -> Optional[list]:
        """list : The elements associated with each interaction model"""
        return self.__elements

    @elements.setter
    def elements(self, value: Union[str, list, None]):
        if value is not None:
            value = aslist(value)
        self.__elements = value

    @property
    def masses(self) -> Optional[list]:
        """list : The atomic or particle mass associated with each interaction model"""
        return self.__masses

    @masses.setter
    def masses(self, value: Union[float, list, None]):
        if value is not None:
            value = aslist(value)
        self.__masses = value

    @property
    def charges(self) -> Optional[list]:
        """list : The atomic or particle charge associated with each interaction model"""
        return self.__charges

    @charges.setter
    def charges(self, value: Union[float, list, None]):
        if value is not None:
            value = aslist(value)
        self.__charges = value

    @property
    def pair_style_terms(self) -> list:
        """list : All extra terms to include in the pair_style command line"""
        return self.__pair_style_terms

    @pair_style_terms.setter
    def pair_style_terms(self, value: Union[str, list, None]):
        if value is not None:
            self.__pair_style_terms = aslist(value)
        else:
            self.__pair_style_terms = []

    @property
    def command_terms(self) -> list:
        """list : All extra command lines to include"""
        return self.__command_terms

    @command_terms.setter
    def command_terms(self, value: Union[str, list, None]):
        if value is not None:
            value = aslist(value)
            if not isinstance(value[0], list):
                value = [value]
            self.__command_terms = value
        else:
            self.__command_terms = []

    @property
    def artifacts(self) -> list:
        return self.__artifacts

    @artifacts.setter
    def artifacts(self, value: Union[Artifact, list, dict, None]):
        self.__artifacts = []
        if value is not None:
            value = aslist(value)
            for v in value:
                if isinstance(v, Artifact):
                    self.__artifacts.append(v)
                elif isinstance(v, dict):
                    self.add_artifact(**v)
                else:
                    raise TypeError('Invalid artifact object: must be an Artifact or dict')

    def build(self) -> DM:
        """
        Generates a PotentialLAMMPS data model using the given parameters.

        Returns
        -------
        DataModelDict.DataModelDict
            The PotentialLAMMPS data model.
            
        Raises
        ------
        ValueError
            If elements and/or symbols not set, if masses not set when elements
            are not given, or if pair_style is not set.
        """
        # Check that required values have been set
        if self.symbols is None and self.elements is None:
            raise ValueError('elements and/or symbols must be set')
        if self.elements is None and self.masses is None:
            raise ValueError('masses must be set if elements are not given')
        if self.pair_style is None:
            raise ValueError('pair_style must be set')

        # Initialize model
        model = DM()
        model['potential-LAMMPS'] = DM()
        model['potential-LAMMPS']['key'] = self.key
        model['potential-LAMMPS']['id'] = self.id
        if self.url is not None:
            model['potential-LAMMPS']['URL'] = self.url
        if self.status != 'active':
            model['potential-LAMMPS']['status'] = self.status
        
        model['potential-LAMMPS']['potential'] = DM()
        model['potential-LAMMPS']['potential']['key'] = self.potkey
        model['potential-LAMMPS']['potential']['id'] = self.potid
        if self.poturl is not None:
            model['potential-LAMMPS']['potential']['URL'] = self.poturl
        for doi in self.dois:
            model['potential-LAMMPS']['potential'].append('doi', doi)

        if self.comments is not None:
            model['potential-LAMMPS']['comments'] = self.comments
        model['potential-LAMMPS']['units'] = self.units
        model['potential-LAMMPS']['atom_style'] = self.atom_style
        if self.allsymbols is True:
            model['potential-LAMMPS']['allsymbols'] = True

        # Add list of atoms
        for atom in self.iteratoms():
            model['potential-LAMMPS'].append('atom', atom)
        
        # Add pair style and coeff terms
        model['potential-LAMMPS']['pair_style'] = self.buildpairstyle()
        model['potential-LAMMPS']['pair_coeff'] = self.buildpaircoeff()
        
        # Add any extra command lines
        for command in self.buildcommands():
            model['potential-LAMMPS'].append('command', command)

        # Add artifacts
        for artifact in self.artifacts:
            model['potential-LAMMPS'].append('artifact',
                                              artifact.build_model()['artifact'])

        return model

    def potential(self, pot_dir: Optional[str] = None) -> PotentialLAMMPS:
        return load_record('potential_LAMMPS', model=self.build(),
                           pot_dir=pot_dir)

    @property
    def supported_pair_styles(self) -> tuple:
        """tuple : The list of known pair styles that use this format."""
        return ()

    @property
    def symbollist(self) -> str:
        """str: The list of all of the model symbols defined by the potential"""
        if self.symbols is not None:
            return ' '.join(self.symbols)
        else:
            return ' '.join(self.elements)

    def iteratoms(self) -> Generator[dict, None, None]:
        """
        Iterates through the list of defined atoms and returns the atom model
        information.

        Yields
        ------
        dict
            The per-atom type info consisting of element, symbol, mass and
            charge values.
        """
        if self.symbols is not None:
            symbols = self.symbols
        else:
            symbols = [None for i in range(len(self.elements))]
        
        if self.elements is not None:
            elements = self.elements
        else:
            elements = [None for i in range(len(self.symbols))]
        
        if self.masses is not None:
            masses = self.masses
        else:
            masses = [None for i in range(len(elements))]

        if self.charges is not None:
            charges = self.charges
        else:
            charges = [None for i in range(len(elements))]

        assert len(symbols) == len(elements), 'incompatible symbols, elements lengths'
        assert len(symbols) == len(masses), 'incompatible symbols, masses lengths'
        assert len(symbols) == len(charges), 'incompatible symbols, charges lengths'

        for element, symbol, mass, charge in zip(elements, symbols, masses, charges):
            atom = DM()
            if symbol is not None:
                atom['symbol'] = symbol
            if element is not None:
                atom['element'] = element
            if mass is not None:
                atom['mass'] = mass
            if charge is not None:
                atom['charge'] = charge
            yield atom

    def buildpairstyle(self) -> str:
        """
        Builds the LAMMPS pair_style command line.
        
        Returns
        -------
        str
            The LAMMPS pair_style command line.
        """
        pairstyle = DM()
        pairstyle['type'] = self.pair_style
        
        for term in self.pair_style_terms:
            if isinstance(term, (int, float)):
                pairstyle.append('term', DM([('parameter', term)]))
            else:
                pairstyle.append('term', DM([('option', str(term))]))
        return pairstyle

    def buildpaircoeff(self) -> str:
        """
        Builds the LAMMPS pair_coeff command lines.
        
        Returns
        -------
        str
            The LAMMPS pair_coeff command line.
        """
        paircoeff = None

        return paircoeff

    def buildcommands(self) -> str:
        """
        Builds extra LAMMPS command lines from command_terms.

        Returns
        -------
        str
            Any extra LAMMPS command lines.        
        """
        commands = []
        for line in self.command_terms:
            if len(line) == 0:
                continue
            command = DM()
            for term in line:
                if isinstance(term, (int, float)):
                    command.append('term', DM([('parameter', term)]))
                else:
                    command.append('term', DM([('option', str(term))]))
            commands.append(command)
        return commands

    def add_artifact(self,
                     model: Union[DM, str, None] = None,
                     filename: Optional[str] = None,
                     label: Optional[str] = None,
                     url: Optional[str] = None):
        """
        Initializes a new Artifact object and appends it to the artifacts
        attribute.

        Parameters
        ----------
        model : str or DataModelDict, optional
            Model content or file path to model content.
        filename : str, optional
            The name of the file without path information.
        label : str, optional
            A short description label.
        url : str, optional
            URL for file where downloaded, if available.
        """
        self.artifacts.append(Artifact(model=model, filename=filename,
                                       label=label, url=url))