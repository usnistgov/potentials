# Standard Python libraries

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

# local imports
from .AtomInfo import AtomInfo

class PotentialInfo(Record):
    """
    Component class for representing info about a potential listing and atom
    info.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'potentialinfo'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'potential'
    
    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'key',
                        description = 'the UUID4 key associated with a potential entry')

        self._add_value('str', 'id',
                        description = 'the unique id associated with a potential entry')

        self._add_value('str', 'url',
                        modelpath = 'URL',
                        description = 'a URL where the potential entry can be found')
        
        self._add_value('strlist', 'dois',
                        modelpath = 'doi',
                        description = 'citation DOIs associated with the potential entry')
        
        self._add_value('record', 'atoms',
                        recordclass = AtomInfo,
                        modelpath = 'atom',
                        description = 'the atomic models included in the potential entry')
        
    def add_atom(self, **kwargs):
        """
        Initializes a new AtomInfo object and appends it to the atoms list.
        """
        newatom = AtomInfo(**kwargs)
        for atom in self.atoms:
            if atom.symbol == newatom.symbol:
                raise ValueError(f'AtomInfo with symbol {atom.symbol} already exists')
        self.atoms.append(newatom)