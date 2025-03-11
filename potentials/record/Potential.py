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

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'key', valuerequired=True,
                        defaultvalue=str(uuid.uuid4()))
        self._add_value('str', 'id')
        self._add_value('str', 'url', modelpath='URL')
        self._add_value('date', 'recorddate', modelpath='record-version')
        self._add_value('record', 'citations', recordclass=Citation,
                        modelpath='description.citation')
        self._add_value('str', 'notes', modelpath='description.notes.text')
        self._add_value('record', 'implementations', recordclass=Implementation,
                        modelpath='implementation')
        self._add_value('strlist', 'fictionalelements', modelpath='fictional-element')
        self._add_value('strlist', 'elements', modelpath='element')
        self._add_value('str', 'othername', modelpath='other-element')
        
        # Modify citation queries
        citations_queries = self.get_value('citations').queries
        del citations_queries['doctype']
        del citations_queries['title']
        del citations_queries['publication']
        del citations_queries['month']
        del citations_queries['volume']
        del citations_queries['issue']
        del citations_queries['pages']
        del citations_queries['doi']
        del citations_queries['url']
        del citations_queries['bibtex']

        # Modify implemetation queries
        implemetations_queries = self.get_value('implementations').queries
        implemetations_queries['imp_key'] = implemetations_queries.pop('key')
        implemetations_queries['imp_id'] = implemetations_queries.pop('id')
        implemetations_queries['imp_type'] = implemetations_queries.pop('type')
        del implemetations_queries['status']
        del implemetations_queries['date']
        del implemetations_queries['notes']

    @property
    def defaultname(self) -> str:
        self.build_id()
        return f'potential.{self.id}'

    def build_id(self):
        """Builds an id value if id is currently None"""
        if self.id is None:
            
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
  
    @property
    def fictional(self) -> bool:
        """bool: Indicates if the potential includes fictional elements"""
        if self.fictionalelements is None or len(self.fictionalelements) == 0:
            return False
        return True

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
        self.get_value('citations').append(**kwargs)

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

    def build_model(self):
        self.build_id()
        return super().build_model()

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
        self.build_id()
        meta = super().metadata()

        meta['surnames'] = self.surnames

        return meta