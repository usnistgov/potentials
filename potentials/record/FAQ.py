# coding: utf-8
# Standard Python libraries
import io
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_query, load_value

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
        return 'faq'

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
        
        self.__question = load_value('longstr', 'question', self)
        value_objects.append(self.__question)

        self.__answer = load_value('longstr', 'answer', self)
        value_objects.append(self.__answer)

        return value_objects

    @property
    def question(self):
        """str: The frequently asked question."""
        return self.__question.value

    @question.setter
    def question(self, val):
        self.__question.value = val

    @property
    def answer(self):
        """str: The answer to the frequently asked question."""
        return self.__answer.value

    @answer.setter
    def answer(self, val):
        self.__answer.value = val
