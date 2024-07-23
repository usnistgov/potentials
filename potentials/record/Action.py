# coding: utf-8
# Standard Python libraries
import datetime
import io
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_query, load_value

# Local imports
from . import Potential

__all__ = ['Action']

class PotInfo(Record):
    """
    Component class designed to represent a subset of data from a Potential
    record for inclusion in an Action record.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'PotInfo'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'potential-info'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'PotInfo.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'PotInfo.xsd')

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
        
        self.__key = load_value('str', 'potential_key', self,
                                modelpath='key', metadatakey='key')
        self.__id = load_value('str', 'potential_id', self,
                               modelpath='id', metadatakey='id')
        self.__dois = load_value('strlist', 'dois', self)
        self.__fictional = load_value('list_contains', 'fictional', self,
                                      modelpath='fictional-element')
        self.__elements = load_value('list_contains', 'elements', self)
        self.__othername = load_value('str', 'othername', self,
                                      modelpath='other-element')
        
        value_objects.extend([self.__key, self.__id, self.__dois, self.__fictional,
                              self.__elements, self.__othername])

        return value_objects
    
    @classmethod
    def from_potential(cls, potential: Union[str, DM, Potential.Potential]):
        """
        Builds a PotInfo component class from a Potential record object

        Parameters
        ----------
        potential : Potential
            A Potential record object.
        """
        
        dois = []
        for citation in potential.citations:
            if citation.doi is not None:
                dois.append(citation.doi)

        return cls(key=potential.key, id=potential.id, dois=dois,
                   fictional=potential.fictional, elements=potential.elements,
                   othername=potential.othername)

    @property
    def key(self) -> str:
        """str: The Potential's key"""
        return self.__key.value
    
    @property
    def id(self) -> str:
        """str: The Potential's id"""
        return self.__id.value

    @property
    def dois(self) -> list:
        """list: The Potential's DOIs"""
        return self.__dois.value

    @property
    def elements(self) -> list:
        """list: The elements modeled by the Potential"""
        return self.__elements.value

    @property
    def othername(self) -> Optional[str]:
        """str or None: The Potential's othername"""
        return self.__othername.value

    @property
    def fictional(self) -> list:
        """list: The fictional elements modeled by the Potential."""
        return self.__fictional.value

class Action(Record):
    """
    Class for representing Action records that document changes to the
    Interatomic Potentials Repository.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'Action'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'action'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'Action.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'Action.xsd')

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
        
        self.__date = load_value('date', 'date', self)
        self.__type = load_value('str', 'type', self,
                                 modelpath='given-name',
                                 allowedvalues=['new posting', 'updated posting',
                                                'retraction', 'site change'])
        self.__potentials = load_value('record', 'potentials', self,
                                       recordclass=PotInfo,
                                       modelpath='potential')
        self.__comment = load_value('longstr', 'comment', self)
        
        value_objects.extend([self.__date, self.__type, self.__potentials,
                              self.__comment])

        return value_objects

    @property
    def defaultname(self) -> str:
        if self.comment is None:
            return f"{self.date}"
        else:
            return f"{self.date} {self.comment[:90]}"

    @property
    def date(self) -> datetime.date:
        """datetime.date: The date associated with the action."""
        return self.__date.value

    @date.setter
    def date(self, val: Union[datetime.date, str]):
        self.__date.value = val

    @property
    def type(self) -> str:
        """str: Broad category describing what the Action did."""
        return self.__type.value

    @type.setter
    def type(self, val: str):
        self.__type.value = val

    @property
    def potentials(self) -> list:
        """list: Any potentials associated with the action as PotInfo objects"""
        return self.__potentials.value

    @property
    def comment(self) -> Optional[str]:
        """str or None: Any comments further describing the Action."""
        return self.__comment.value

    @comment.setter
    def comment(self, val: Optional[str]):
        self.__comment.value = val
