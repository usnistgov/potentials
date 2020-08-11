# Standard libraries
import uuid

from DataModelDict import DataModelDict as DM

from ..tools import aslist
from .. import PotentialLAMMPS

class PotentialLAMMPSBuilder(object):
    """
    Template class for generating potential_LAMMPS records for different pair styles.

    Note: terms for pair_coeff lines are not included as they are style-specific.
    """

    def __init__(self, id=None, key=None, potid=None, potkey=None,
                 units=None, atom_style=None, pair_style=None,
                 pair_style_terms=None, status='active', allsymbols=False,
                 elements=None, masses=None, charges=None, symbols=None,
                 command_terms=None):
        
        self.id = id
        self.key = key
        self.potid = potid
        self.potkey = potkey
        
        self.units = units
        self.atom_style = atom_style
        self.pair_style = pair_style
        
        self.allsymbols = allsymbols
        self.status = status

        self.symbols = symbols
        self.elements = elements
        self.masses = masses
        self.charges = charges
        
        self.pair_style_terms = pair_style_terms
        self.command_terms = command_terms

    @property
    def id(self):
        """Human-readable id for LAMMPS implementation of the potential."""
        return self.__id

    @id.setter
    def id(self, value):
        if value is not None:
            value = str(value)
        self.__id = value

    @property
    def key(self):
        """Unique UUID4 key for the LAMMPS implementation."""
        return self.__key

    @key.setter
    def key(self, value):
        if value is None:
            value = uuid.uuid4()
        self.__key = str(value)

    @property
    def potid(self):
        """Human-readable id for the potential model."""
        return self.__potid

    @potid.setter
    def potid(self, value):
        if value is not None:
            value = str(value)
        self.__potid = value

    @property
    def potkey(self):
        """Unique UUID4 key for the potential model."""
        return self.__potkey

    @potkey.setter
    def potkey(self, value):
        if value is None:
            value = uuid.uuid4()
        self.__potkey = str(value)

    @property
    def units(self):
        """LAMMPS units style."""
        return self.__units

    @units.setter
    def units(self, value):
        if value is not None:
            value = str(value)
        self.__units = value

    @property
    def atom_style(self):
        """LAMMPS atom_style."""
        return self.__atom_style

    @atom_style.setter
    def atom_style(self, value):
        if value is not None:
            value = str(value)
        self.__atom_style = value

    @property
    def pair_style(self):
        """LAMMPS pair_style."""
        return self.__pair_style

    @pair_style.setter
    def pair_style(self, value):
        if value is not None:
            value = str(value)
        self.__pair_style = value

    @property
    def allsymbols(self):
        return self.__allsymbols

    @allsymbols.setter
    def allsymbols(self, value):
        if isinstance(value, bool):
            self.__allsymbols = value
        elif value.lower() == 'true':
            self.__allsymbols = True
        elif value.lower() == 'false':
            self.__allsymbols = False
        else:
            raise ValueError(f'Invalid allsymbols value "{value}"')

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if value not in ['active', 'superseded', 'retracted']:
            raise ValueError('Invalid status: allowed values are active, superseded, and retracted')
        self.__status = value

    @property
    def symbols(self):
        return self.__symbols

    @symbols.setter
    def symbols(self, value):
        if value is not None:
            value = aslist(value)
        self.__symbols = value

    @property
    def elements(self):
        return self.__elements

    @elements.setter
    def elements(self, value):
        if value is not None:
            value = aslist(value)
        self.__elements = value

    @property
    def masses(self):
        return self.__masses

    @masses.setter
    def masses(self, value):
        if value is not None:
            value = aslist(value)
        self.__masses = value

    @property
    def charges(self):
        return self.__charges

    @charges.setter
    def charges(self, value):
        if value is not None:
            value = aslist(value)
        self.__charges = value

    @property
    def pair_style_terms(self):
        return self.__pair_style_terms

    @pair_style_terms.setter
    def pair_style_terms(self, value):
        if value is not None:
            self.__pair_style_terms = aslist(value)
        else:
            self.__pair_style_terms = []

    @property
    def command_terms(self):
        return self.__command_terms

    @command_terms.setter
    def command_terms(self, value):
        if value is not None:
            value = aslist(value)
            if not isinstance(value[0], list):
                value = [value]
            self.__command_terms = value
        else:
            self.__command_terms = []

    def build(self):
        """
        Generates a PotentialLAMMPS data model using the given parameters.

        Returns
        -------
        DataModelDict
            The PotentialLAMMPS data model.
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
        if self.status != 'active':
            model['potential-LAMMPS']['status'] = self.status
        model['potential-LAMMPS']['potential'] = DM()
        model['potential-LAMMPS']['potential']['key'] = self.potkey
        model['potential-LAMMPS']['potential']['id'] = self.potid
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

        return model

    def potential(self, pot_dir=None):
        return PotentialLAMMPS(self.build(), pot_dir=pot_dir)

    @property
    def supported_pair_styles(self):
        """tuple : The list of known pair styles that use this format."""
        return ()

    @property
    def symbollist(self):
        if self.symbols is not None:
            return ' '.join(self.symbols)
        else:
            return ' '.join(self.elements)

    def iteratoms(self):
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

    def buildpairstyle(self):
        pairstyle = DM()
        pairstyle['type'] = self.pair_style
        
        for term in self.pair_style_terms:
            if isinstance(term, (int, float)):
                pairstyle.append('term', DM([('parameter', term)]))
            else:
                pairstyle.append('term', DM([('option', str(term))]))
        return pairstyle

    def buildpaircoeff(self):
        paircoeff = None

        return paircoeff

    def buildcommands(self):
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
