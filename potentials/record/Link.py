# coding: utf-8
# Standard Python libraries
import io
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_value

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
        
        self.__url = load_value('str', 'url', self,
                                modelpath='web-link.URL')
        self.__label = load_value('longstr', 'label', self,
                                  modelpath='web-link.label')
        self.__linktext = load_value('longstr', 'linktext', self,
                                     modelpath='web-link.link-text')
        
        value_objects.extend([self.__url, self.__label, self.__linktext])

        return value_objects

    @property
    def url(self) -> Optional[str]:
        """str or None: URL for the link"""
        return self.__url.value
    
    @url.setter
    def url(self, val: Optional[str]):
        self.__url.value = val

    @property
    def label(self) -> Optional[str]:
        """str or None: short descriptive label"""
        return self.__label.value
    
    @label.setter
    def label(self, val: Optional[str]):
        self.__label.value = val
    
    @property
    def linktext(self) -> Optional[str]:
        """str or None: text to show for the link"""
        return self.__linktext.value
    
    @linktext.setter
    def linktext(self, val: Optional[str]):
        self.__linktext.value = val
