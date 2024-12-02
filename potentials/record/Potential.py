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
from yabadaba import load_value, load_query

# Local imports
from .Citation import Citation
from .Implementation import Implementation
from ..tools import aslist

class Potential(Record):

    def __init__(self,
                 model: str | io.IOBase | DM | None = None,
                 name: str | None = None,
                 database=None,
                 **kwargs: any):
        
        self.modelname = None
        super().__init__(model, name, database, **kwargs)

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
                                valuerequired=True,
                                defaultvalue=str(uuid.uuid4()))
        self.__id = load_value('str', 'id', self)
        self.__url = load_value('str', 'url', self,
                                modelpath='URL')
        self.__recorddate = load_value('date', 'recorddate', self,
                                       modelpath='record-version')
        self.__citations = load_value('record', 'citations', self, recordclass=Citation,
                                      modelpath='description.citation')
        self.__notes = load_value('str', 'notes', self,
                                  modelpath='description.notes.text')
        self.__implementations = load_value('record', 'implementations', self,
                                            recordclass=Implementation,
                                            modelpath='implementation')
        self.__fictionalelements = load_value('strlist', 'fictionalelements', self,
                                      modelpath='fictional-element')
        self.__elements = load_value('strlist', 'elements', self,
                                     modelpath='element')
        self.__othername = load_value('str', 'othername', self,
                                      modelpath='other-element')
        
        # Modify citation queries
        del self.__citations.queries['doctype']
        del self.__citations.queries['title']
        del self.__citations.queries['publication']
        del self.__citations.queries['month']
        del self.__citations.queries['volume']
        del self.__citations.queries['issue']
        del self.__citations.queries['pages']
        del self.__citations.queries['doi']
        del self.__citations.queries['url']
        del self.__citations.queries['bibtex']

        # Modify implemetation queries
        self.__implementations.queries['imp_key'] = self.__implementations.queries.pop('key')
        self.__implementations.queries['imp_id'] = self.__implementations.queries.pop('id')
        self.__implementations.queries['imp_type'] = self.__implementations.queries.pop('type')
        del self.__implementations.queries['status']
        del self.__implementations.queries['date']
        del self.__implementations.queries['notes']
        
        value_objects.extend([self.__key, self.__id, self.__url, self.__recorddate,
                              self.__citations, self.__notes, self.__implementations,
                              self.__fictionalelements, self.__elements, self.__othername])

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
        if self.__id is None:
            
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
            
            self.id = potential_id
        
        return self.__id.value

    @id.setter
    def id(self, val: Union[str, None]):
        self.__id.value = val

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
    def fictionalelements(self) -> list:
        """list: fictional elements associated with the potential"""
        return self.__fictionalelements.value

    @fictionalelements.setter
    def fictionalelements(self, val: Union[str, list, None]):
        self.__fictionalelements.value = val
    
    @property
    def fictional(self) -> bool:
        """bool: Indicates if the potential includes fictional elements"""
        if self.fictionalelements is None or len(self.fictionalelements) == 0:
            return False
        return True

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
    def modelname(self, val: Optional[str]):
        if val is None:
            self.__modelname = None
        else:
            self.__modelname = str(val)

    @property
    def surnames(self) -> list:
        """list: The author surnames pulled out to be queryable"""
        surnames = []
        for citation in self.citations:
            for author in citation.authors:
                surnames.append(author.surname)
        return surnames

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

    def set_values(self, **kwargs):
        if 'modelname' in kwargs:
            self.modelname = kwargs['modelname']
        super().set_values(**kwargs)

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        queries = super().queries
        
        queries.update({
            'surnames': load_query(
                style='list_contains',
                name='surnames',
                path=f'{self.modelroot}.description.citation.author.surname',
                description="search based on citation author surnames"),
            'author': load_query(
                style='list_contains',
                name='surnames',
                path=f'{self.modelroot}.description.citation.author.surname',
                description="search based on citation author surnames"),
        })

        return queries
    
    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        meta = super().metadata()

        meta['surnames'] = self.surnames

        return meta