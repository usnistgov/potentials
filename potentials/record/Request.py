# coding: utf-8
# Standard Python libraries
import io
from typing import Optional, Tuple, Union
import datetime

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_query, load_value

# local imports
from ..tools import aslist

class ElementSystem(Record):
    """
    Component class for representing an elemental system being requested.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'elementsystem'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'system'
    
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
        
        self.__formula = load_value('str', 'formula', self,
                                    modelpath='chemical-formula')
        self.__elements = load_value('strlist', 'elements', self,
                                    modelpath='element')
        
        value_objects.extend([self.__formula, self.__elements])

        return value_objects

    @property
    def formula(self) -> Optional[str]:
        """str : A specific chemical formula being requested."""
        return self.__formula.value

    @formula.setter
    def formula(self, val: Optional[str]):
        self.__formula.value = val

    @property
    def elements(self) -> Optional[list]:
        """list : A combination of elements being requested."""
        return self.__elements.value

    @elements.setter
    def elements(self, val: Union[str, list, None]):
        self.__elements.value = val




class Request(Record):
    """
    Class for representing Request records that are associated with user
    requests to the NIST Interatomic Potentials Repository for new potentials.
    """

    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'Request'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'request'
    
    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'Request.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'Request.xsd')

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
        
        self.__date = load_value('date', 'date', self, valuerequired=True)
        self.__comment = load_value('longstr', 'comment', self)
        self.__systems = load_value('record', 'systems', self, recordclass=ElementSystem,
                                    modelpath='system')
        
        value_objects.extend([self.__date, self.__comment, self.__systems])

        return value_objects

    @property
    def date(self) -> datetime.date:
        """datetime.date : The date that the request was submitted."""
        return self.__date.value

    @date.setter
    def date(self, val: Union[str, datetime.date]):
        self.__date.value = val

    @property
    def comment(self) -> Optional[str]:
        """str: Any additional comments associated with the request."""
        return self.__comment.value

    @comment.setter
    def comment(self, val: Optional[str]):
        self.__comment.value = val

    @property
    def systems(self) -> list:
        """list: The System component objects associated with the request."""
        return self.__systems.value

    @systems.setter
    def systems(self, val: Union[Record, list]):
        self.__systems.value = val

    def add_system(self,
                   model: Union[str, io.IOBase, DM, None] = None,
                   formula: Optional[str] = None,
                   elements: Union[str, list, None] = None):
        """
        Initializes a System component class and appends it to the systems list.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            The contents of the record associated with the system info.
        formula : str, optional
            A specific chemical formula being requested.
        elements : str or list, optional
            A set of elements for the elemental system being requested.
        """
        self.__systems.append(model=model, formula=formula, elements=elements)
