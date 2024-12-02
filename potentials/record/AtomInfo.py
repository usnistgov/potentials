# coding: utf-8
# Standard Python libraries
from typing import Optional, Union

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_value

class AtomInfo(Record):
    """
    Component class for representing an elemental system being requested.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'atominfo'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'atom'
    
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
        
        self.__symbol = load_value('str', 'symbol', self)
        self.__element = load_value('str', 'element', self)
        self.__mass = load_value('float', 'mass', self)
        self.__charge = load_value('float', 'charge', self)
        
        value_objects.extend([self.__symbol, self.__element, self.__mass,
                              self.__charge])

        return value_objects

    @property
    def symbol(self) -> Optional[str]:
        """str : The interaction model symbol."""
        return self.__symbol.value

    @symbol.setter
    def symbol(self, val: Optional[str]):
        self.__symbol.value = val

    @property
    def element(self) -> Optional[str]:
        """list : The element associated with the element model symbol."""
        return self.__element.value

    @element.setter
    def element(self, val: Union[str, list, None]):
        self.__element.value = val

    @property
    def mass(self) -> Optional[str]:
        """list : The atomic mass associated with the element model symbol."""
        return self.__mass.value

    @mass.setter
    def mass(self, val: Union[str, list, None]):
        self.__mass.value = val

    @property
    def charge(self) -> Optional[str]:
        """list : The constant atomic charge associated with the element model symbol."""
        return self.__charge.value

    @charge.setter
    def charge(self, val: Union[str, list, None]):
        self.__charge.value = val