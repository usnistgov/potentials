# coding: utf-8
# Standard Python libraries
from typing import Tuple

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

class Link(Record):
    """
    Class for describing website link
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'implementation_link'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'link'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'link.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'link.xsd')

    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'url', modelpath='web-link.URL')
        self._add_value('longstr', 'label', modelpath='web-link.label')
        self._add_value('longstr', 'linktext', modelpath='web-link.link-text')
