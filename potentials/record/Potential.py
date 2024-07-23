# coding: utf-8
# Standard Python libraries
import io
from typing import Optional, Tuple, Union
import uuid
import datetime

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_value

# Local imports
from .Citation import Citation
from .Implementation import Implementation
from ..tools import aslist

class Potential(Record):
    """
    Class for representing Potential metadata records.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'Potential'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'Potential.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'Potential.xsd')

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'interatomic-potential'

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
        
        self.__key = load_value('str', 'key', self,
                                valuerequired=True)
        self.__id = load_value('str', 'id', self)
        self.__url = load_value('str', 'url', self,
                                modelpath='URL')
        self.__recorddate = load_value('recorddate', 'date', self,
                                       modelpath='record-version')
        self.__citations = load_value('record', 'citations', self, recordclass='Citation',
                                      modelpath='description.citation')
        self.__notes = load_value('str', 'notes', self,
                                  modelpath='description.notes.text')
        self.__implementations = load_value('record', 'implementations', self,
                                            recordclass='Implementation',
                                            modelpath='implementation')
        self.__fictional = load_value('list_contains', 'fictional', self,
                                      modelpath='fictional-element')
        self.__elements = load_value('list_contains', 'elements', self)
        self.__othername = load_value('str', 'othername', self,
                                      modelpath='other-element')
        
        value_objects.extend([self.__key, self.__id, self.__url, self.__recorddate,
                              self.__citations, self.__notes, self.__implementations,
                              self.__fictional, self.__elements, self.__othername])

        return value_objects

    @property
    def defaultname(self) -> str:
        return f'potential.{self.id}'

    @property
    def key(self) -> str:
        """str : The potential's uuid4 key"""
        return self.__key.value
    
    @key.setter
    def key(self, val: Optional[str]):
        self.__key.value = val

    @property
    def id(self) -> str:
        """str : The potential's unique id generated from citation info"""
        # Check for a citation
        if len(self.citations) > 0:
            potential_id = self.citations[0].year_authors
        else:
            return None
        
        potential_id += '-'
        
        if self.fictional:
            potential_id += '-fictional'
        
        if self.othername is not None:
            potential_id += '-' + str(self.othername)
        else:
            for element in self.elements:
                potential_id += '-' + element
        
        if self.modelname is not None:
            potential_id += '-' + str(self.modelname)
        
        return potential_id

    @property
    def url(self):
        """str : URL for an online copy of the record."""
        return self.__url.value

    @url.setter
    def url(self, val: Union[str, None]):
        self.__url.value = val

    @property
    def recorddate(self) -> datetime.date:
        """datetime.date : The date associated with the record"""
        return self.__recorddate.value
    
    @recorddate.setter
    def recorddate(self, val: Union[datetime.date, str, None]):
        self.__recorddate.value = val

    @property
    def citations(self) -> list:
        """list: Any associated Citation objects"""
        return self.__citations.value

    @property
    def implementations(self) -> list:
        """list: Any associated Implementation objects"""
        return self.__implementations.value

    @property
    def elements(self) -> list:
        """list: elements associated with the potential"""
        return self.__elements.value

    @elements.setter
    def elements(self, val: Union[str, list, None]):
        self.__elements.value = val
    
    @property
    def othername(self) -> Optional[str]:
        """str or None: Alternate name for what the potential models"""
        return self.__othername.value
    
    @othername.setter
    def othername(self, val: Optional[str]):
        self.__othername.value = val
    
    @property
    def fictional(self) -> list:
        """list: fictional elements associated with the potential"""
        return self.__fictional.value

    @fictional.setter
    def fictional(self, val: Union[str, list, None]):
        self.__fictional.value = val
    
    @property
    def notes(self) -> Optional[str]:
        """str or None: Any extra notes associated with the potential"""
        return self.__notes.value

    @notes.setter
    def notes(self, val: Optional[str]):
        self.__notes.value = val

    @property
    def modelname(self) -> Optional[str]:
        """str: Extra tag for differentiating potentials when needed"""
        return self.__modelname
    
    @modelname.setter
    def modelname(self, v: Optional[str]):
        self.__modelname = str(v)

    @property
    def impid_prefix(self) -> str:
        """str : The recommended prefix to use for implementation ids"""
        if len(self.citations) > 0:
            potential_id = self.citations[0].year_first_author
        else:
            return None
        
        potential_id += '-'
        
        if self.fictional:
            potential_id += '-fictional'
        
        if self.othername is not None:
            potential_id += '-' + str(self.othername)
        else:
            for element in self.elements:
                potential_id += '-' + element
        
        if self.modelname is not None:
            potential_id += '-' + str(self.modelname)
        
        return potential_id
    
    def add_citation(self, **kwargs):
        """
        Initializes a new Citation object and appends it to the citations list.
        """
        self.__citations.append(**kwargs)

    def add_implementation(self, **kwargs):
        """
        Initializes a new Implementation object and appends it to the implementations list.
        """
        implementation = Implementation(**kwargs)
        for imp in self.implementations:
            if imp.id == implementation.id:
                raise ValueError(f'Implementation with id {imp.id} already exists')
        self.implementations.append(implementation)

    