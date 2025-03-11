# coding: utf-8
# Standard Python libraries

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

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

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'symbol')
        self._add_value('str', 'element')
        self._add_value('float', 'mass')
        self._add_value('float', 'charge')
        