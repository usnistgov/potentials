# coding: utf-8
# Standard Python libraries
import io
from typing import Tuple

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

class Parameter(Record):
    """
    Class for describing parameter values. Note that this is
    meant as a component class for other record objects.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'implementation_parameter'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'parameter'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'parameter.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'parameter.xsd')

    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'value', modelpath='value')
        self._add_value('str', 'unit', modelpath='unit')
        self._add_value('str', 'paramname', modelpath='name')
        