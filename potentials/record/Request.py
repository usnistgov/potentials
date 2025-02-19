# coding: utf-8
# Standard Python libraries
import io
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

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

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'formula', modelpath='chemical-formula')
        self._add_value('strlist', 'elements', modelpath='element')

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

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('date', 'date', valuerequired=True)
        self._add_value('record', 'systems', recordclass=ElementSystem,
                        modelpath='system')
        self._add_value('longstr', 'comment')

    @property
    def defaultname(self) -> str:
        name = str(self.date)
        for system in self.systems:
            for element in system.elements:
                name += ' ' + element
        return name

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
        self.get_value('systems').append(model=model, formula=formula, elements=elements)
