# coding: utf-8
# Standard Python libraries
from typing import Optional,  Union
from pathlib import Path

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.tools import dict_insert

# local imports
from ..tools import aslist

class CommandLine():
    """Class for representing the terms of a LAMMPS command line"""

    def __init__(self):
        self.__terms = []

    @property
    def terms(self) -> list:
        """list: The terms found in the LAMMPS command"""
        return self.__terms

    def add_term(self,
                 type: str,
                 value: Union[str, float, bool]):
        """
        Adds a term to the command line.
        
        Parameters
        ----------
        type : str
            The type of term: option, file, parameter, symbols or symbolsList
        value : str, float or bool
            The value of the term, with the data type depending on the term type:
            option and file should be str, parameter should be float, and symbols
            and symbolsList should be bool.
        """
        if type in ['option', 'file']:
            value = str(value)
        elif type == 'parameter':
            value = float(value)
        elif type in ['symbols', 'symbolsList']:
            if isinstance(value, str):
                # Convert strings
                if value.lower() in ['true', 't']:
                    value = True
                elif value.lower() in ['false', 'f']:
                    value = False
                else:
                    raise ValueError(f'String value for {type} not recognized as a Boolean value.')
            elif not isinstance(value, bool):
                raise TypeError(f'{type} value must be bool or a str representation of a bool')
        else:
            raise ValueError('Invalid term type')

        self.terms.append({type: value})

    def build_command(self, 
                      pot_dir: Optional[Path] = None) -> str:
        """
        Constructs the full command line from the terms.

        Parameters
        ----------
        pot_dir : path-like object, optional
            The directory where any potential parameter files are located.
            Used to prefix the path to the file terms.       
        """
        if pot_dir is None:
            pot_dir = Path()
        
        line = ''
        
        for term in self.terms:
            for ttype, tval in term.items():
                
                # Print options and parameters as strings
                if ttype == 'option' or ttype == 'parameter':
                    line += f'{tval} '
                
                # Print files with pot_dir prefixes
                elif ttype == 'file':
                    line += f'{Path(pot_dir, tval)} '
                
        return line.strip() + '\n'

    def build_model(self):
        model = DM()
        for term in self.terms:
            model.append('term', DM(term))
        return model
        
    def load_model(self, model):
        for term in model.aslist('term'):
            for ttype, tval in term.items():
                self.add_term(ttype, tval)

class PairCoeffLine(CommandLine):

    """Class for representing the terms of a LAMMPS pair_coeff command line"""

    def __init__(self, 
                 interaction: Optional[list] = None):
        super().__init__()
        self.interaction = interaction

    @property
    def interaction(self) -> Optional[tuple]:
        """tuple or None: The atomic species associated with the pair_coeff line."""
        return self.__interaction
    
    @interaction.setter
    def interaction(self, val: Optional[list] = None):
        if val is not None:
            val = aslist(val)
            val = tuple(str(v) for v in val)
            
        self.__interaction = val

    def build_command(self, 
                      pot_dir: Path,
                      symbols: list,
                      is_eam: bool = False) -> str:
        """
        Constructs the full command line from the terms.

        Parameters
        ----------
        pot_dir : path-like object
            The directory where any potential parameter files are located.
            Used to prefix the path to the file terms.
        symbols : list
            The list of the symbols that correspond to the atom types of the
            atomic system. 
        is_eam : bool, optional
            Flag indicating if the pair_style is the original eam as it is a
            unique case.
        """
        
        # Build universal form if no interaction species are specified
        if self.interaction is None:
            return self._build_command_universal(pot_dir, symbols)
        
        # Check if potential is of the manybody variation
        for term in self.terms:
            for key in term.keys():
                if key == 'symbols':
                    return self._build_command_manybody(pot_dir, symbols)

        # Use pair or eam variations
        if is_eam:
            return self._build_command_eam(pot_dir, symbols)
        else:
            return self._build_command_pair(pot_dir, symbols)
        

    def _build_command_universal(self, 
                                 pot_dir: Path,
                                 symbols: list) -> str:
        """
        Builds the pair_coeff variation for when the command is universally
        applied to all species.  Note that this representation is consistent
        across all pair_styles.
        """
        # Build line with * * wildcard types and all symbols (if needed)
        return f'pair_coeff * * {self._build_terms(pot_dir, symbols, symbols)}'

    def _build_command_manybody(self,
                                pot_dir: Path,
                                symbols: list) -> str:
        """
        Builds the pair_coeff manybody variation associated with a subset of
        simulated species.
        """
        # Build line with * * wildcard types and only the used symbols
        return f'pair_coeff * * {self._build_terms(pot_dir, symbols, self.interaction)}'
    
    def _build_command_pair(self,
                            pot_dir: Path,
                            symbols: list) -> str:
        """
        Builds the pair_coeff pair variation associated with a specific two
        elemental interaction.  Note that this will build all necessary pair_coeff
        lines for all atom types that correspond to the interaction.
        """
        # Check that the interaction is two symbols
        if len(self.interaction) != 2:
            raise ValueError('Pair potential interactions need two listed elements')
        
        # Build a pair_coeff line for all atom type pairs of the matching symbols
        coeff_lines = ''
        coeff_terms = self._build_terms(pot_dir, symbols, self.interaction)
        for i in range(len(symbols)):
            for j in range(i, len(symbols)):
                if ((symbols[i] == self.interaction[0] and symbols[j] == self.interaction[1]) or
                    (symbols[i] == self.interaction[1] and symbols[j] == self.interaction[0])):
                    coeff_lines += f'pair_coeff {i+1} {j+1} {coeff_terms}'

        return coeff_lines

    def _build_command_eam(self,
                           pot_dir: Path,
                           symbols: list) -> str:
        """
        Builds the pair_coeff eam variation as used by the original eam
        pair_style.  Note that this will build all necessary pair_coeff
        lines for all atom types that correspond to the interaction.
        """
        # Check that the interaction is two matching symbols
        if len(self.interaction) != 2:
            raise ValueError('Pair potential interactions need two listed elements')
        if self.interaction[0] != self.interaction[1]:
            raise ValueError('Only i==j interactions allowed for eam style')

        # Build a pair_coeff line for each atom type of the matching symbol
        coeff_lines = ''
        coeff_terms = self._build_terms(pot_dir, symbols, self.interaction)

        for i in range(len(symbols)):
            if symbols[i] == self.interaction[0]:
                coeff_lines += f'pair_coeff {i+1} {i+1} {coeff_terms}'
        
        return coeff_lines


    def _build_terms(self,
                     pot_dir: Path,
                     system_symbols: list,
                     coeff_symbols: list):
        """
        Builds the portion of the pair_coeff line associated with the terms.
        """
        line = ''
        for term in self.terms:
            for ttype, tval in term.items():
                
                # Print options and parameters as strings
                if ttype == 'option' or ttype == 'parameter':
                    line += f'{tval} '
                
                # Print files with pot_dir prefixes
                elif ttype == 'file':
                    line += f'{Path(pot_dir, tval)} '
                
                # Print all symbols being used for symbolsList
                elif ttype == 'symbolsList' and tval is True:
                    for coeff_symbol in coeff_symbols:
                        if coeff_symbol in system_symbols:
                            line += f'{coeff_symbol} '
                
                # Print symbols being used with model in appropriate order for symbols
                elif ttype == 'symbols' and tval is True:
                    for system_symbol in system_symbols:
                        if system_symbol in coeff_symbols:
                            line += f'{system_symbol} '
                        else:
                            line += 'NULL '
        return line.strip() + '\n'

    def build_model(self):
        model = super().build_model()
        if self.interaction is not None:
            imodel = DM()
            imodel['symbol'] = list(self.interaction)
            dict_insert(model, 'interaction', imodel, before='term')
        return model
        
    def load_model(self, model):
        super().load_model(model)
        if 'interaction' in model:
            self.interaction = model['interaction']['symbol']
        else:
            self.interaction = None