# coding: utf-8
# Standard Python libraries
from typing import Tuple

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

__all__ = ['FAQ']

class FAQ(Record):
    """
    Class for representing FAQ records that document the FAQs for the NIST
    Interatomic Potentials Repository.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'FAQ'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'faq'
    
    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'FAQ.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'FAQ.xsd')

    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('longstr', 'question')
        self._add_value('longstr', 'answer')
