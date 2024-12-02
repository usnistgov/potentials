# coding: utf-8
# Standard Python libraries
from typing import Optional, Union

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_value

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

    def _init_value_objects(self) -> list:
        """
        Method that defines the value objects for the Record.  This should
        1. Call the method's super() to get default Value objects.
        2. Use yabadaba.load_value() to build Value objects that are set to
           private attributes of self.
        3. Append the list returned by the super() with the new Value objects.

        Returns
        -------
        value_objects: A list of all value objects.
        """
        value_objects = super()._init_value_objects()
        
        self.__key = load_value('str', 'key', self)
        self.__id = load_value('str', 'id', self)
        self.__url = load_value('str', 'url', self,
                                modelpath='URL')
        self.__dois = load_value('strlist', 'dois', self,
                                 modelpath='doi')
        self.__atoms = load_value('record', 'atoms', self,
                                  recordclass=AtomInfo,
                                  modelpath='atom')
        
        value_objects.extend([self.__key, self.__id, self.__url,
                              self.__dois, self.__atoms])

        return value_objects

    @property
    def key(self) -> Optional[str]:
        """str : The potential model UUID key."""
        return self.__key.value

    @key.setter
    def key(self, val: Optional[str]):
        self.__key.value = val

    @property
    def id(self) -> Optional[str]:
        """id : The potential model human readable id."""
        return self.__id.value

    @id.setter
    def id(self, val: Union[str, None]):
        self.__id.value = val

    @property
    def url(self) -> Optional[str]:
        """str : URL for an online copy of the potential model record."""
        return self.__url.value

    @url.setter
    def url(self, val: Union[str, list, None]):
        self.__url.value = val

    @property
    def dois(self) -> list:
        """list: DOIs associated with the potential model."""
        return self.__dois.value

    @property
    def atoms(self) -> list:
        """list : The list of atomic models represented by the potential model."""
        return self.__atoms.value

    def add_atom(self, **kwargs):
        """
        Initializes a new AtomInfo object and appends it to the atoms list.
        """
        newatom = AtomInfo(**kwargs)
        for atom in self.atoms:
            if atom.symbol == newatom.symbol:
                raise ValueError(f'AtomInfo with symbol {atom.symbol} already exists')
        self.__atoms.append(newatom)