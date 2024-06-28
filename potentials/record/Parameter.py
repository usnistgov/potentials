# coding: utf-8
# Standard Python libraries
import io
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_value

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
        
        
        self.__value = load_value('str', 'value', self,
                                  modelpath='value')
        self.__unit = load_value('str', 'unit', self,
                                     modelpath='unit')
        self.__paramname = load_value('str', 'paramname', self,
                                      modelpath='name')
        
        value_objects.extend([self.__value, self.__unit, self.__paramname])

        return value_objects
    
    @property
    def value(self) -> Optional[str]:
        """str or None: The value of the parameter"""
        return self.__value.value
    
    @value.setter
    def value(self, val: Optional[str]):
        self.__value.value = val

    @property
    def unit(self) -> Optional[str]:
        """str or None: The unit that the value is in"""
        return self.__unit.value
    
    @unit.setter
    def unit(self, val: Optional[str]):
        self.__unit.value = val

    @property
    def paramname(self) -> Optional[str]:
        """str or None: The name of the parameter, or a string parameter line"""
        return self.__paramname.value
    
    @paramname.setter
    def paramname(self, val: Optional[str]):
        self.__paramname.value = val
