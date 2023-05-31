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
from yabadaba import load_query

# Local imports
from .Citation import Citation
from .Implementation import Implementation
from ..tools import aslist

class Potential(Record):
    """
    Class for representing Potential metadata records.
    """

    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 **kwargs):
        """
        Initializes a Record object for a given style.
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            A JSON/XML data model for the content.
        name : str, optional
            The unique name to assign to the record.  If model is a file
            path, then the default record name is the file name without
            extension.
        database : yabadaba.Database, optional
            Allows for a default database to be associated with the record.
        """
        # Set default values
        self.url = None
        self.elements = None
        self.key = None
        self.othername = None
        self.fictional = False
        self.modelname = None
        self.notes = None
        self.recorddate = datetime.date.today()
        self.__citations = []
        self.__implementations = []

        super().__init__(model=model, name=name, database=database, **kwargs)

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

    def load_model(self,
                   model: Union[str, io.IOBase, DM],
                   name: Optional[str] = None):
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str, file-like object or DataModelDict
            A JSON/XML data model for the content.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
        super().load_model(model, name=name)
        potential = self.model[self.modelroot]
        
        # Extract information
        self.key = potential['key']
        self.url = potential.get('URL', None)
        self.recorddate = potential['record-version']
        
        description = potential['description']

        self.__citations = []
        for citation in description.iteraslist('citation'):
            self.add_citation(model=DM([('citation', citation)]))
        if 'notes' in description:
            self.notes = description['notes']['text']
        else:
            self.notes = None

        self.__implementations = []
        for implementation in potential.iteraslist('implementation'):
            self.add_implementation(model=DM([('implementation', implementation)]))

        felements = potential.aslist('fictional-element')
        oelements = potential.aslist('other-element')
        elements = potential.aslist('element')
        
        if len(felements) > 0:
            assert len(elements) == 0
            self.fictional = True
            self.elements = felements
        else:
            assert len(elements) > 0
            self.fictional = False
            self.elements = elements
        if len(oelements) > 0:
            assert len(oelements) == 1
            self.othername = oelements[0]
        else:
            self.othername = None
        
        # Identify modelname and check id
        self.modelname = None
        pot_id = potential['id']
        if self.id != pot_id:
            try:
                assert self.id == pot_id[:len(self.id)]
            except AssertionError:
                print(f"Different ids: {self.id} != {pot_id} {self.key}")
            else:
                self.modelname = pot_id[len(self.id):].strip('-')
                if self.id != pot_id:
                    print(f"Different ids: {self.id} != {pot_id} {self.key}")

        # Set name based on id if no name given
        try:
            self.name
        except:
            self.name = f'potential.{self.id}'

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs):
        """
        Set multiple object attributes at the same time.

        Parameters
        ----------
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        date : str or datetime.date, optional
            The date to assign to the record.
        type : str, optional
            The Action type to assign to the record.
        potentials : list, optional
            Potential or model contents for Potential records to associate
            with the action.
        comment : str, optional
            Any additional comments to assign to the record.
        """
        if 'url' in kwargs:
            self.url = kwargs['url']
        if 'elements' in kwargs:
            self.elements = kwargs['elements']
        if 'key' in kwargs:
            self.key = kwargs['key']
        if 'othername' in kwargs:
            self.othername = kwargs['othername']
        if 'fictional' in kwargs:
            self.fictional = kwargs['fictional']
        if 'modelname' in kwargs:
            self.modelname = kwargs['modelname']
        if 'notes' in kwargs:
            self.notes = kwargs['notes']
        if 'recorddate' in kwargs:
            self.recorddate = kwargs['recorddate']
        
        if 'citations' in kwargs:
            self.__citations = []
            for citation in aslist(kwargs['citations']):
                if isinstance(citation, dict):
                    self.add_citation(**citation)
                elif isinstance(citation, Citation):
                    self.citations.append(citation)
        
        if 'implementations' in kwargs:
            self.__implementations = []
            for implementation in aslist(kwargs['implementations']):
                if isinstance(implementation, dict):
                    self.add_implementation(**implementation)
                elif isinstance(implementation, Implementation):
                    self.implementations.append(implementation)

        # Set name
        if name is not None:
            self.name = name
        else:
            try:
                self.name = f'potential.{self.id}'
            except:
                self.name = 'potential.unknown'

    @property
    def key(self) -> str:
        """str : The potential's uuid4 key"""
        return self.__key
    
    @key.setter
    def key(self, v: Optional[str]):
        if v is None:
            self.__key = str(uuid.uuid4())
        else:
            self.__key = str(v)

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
        return self.__url

    @url.setter
    def url(self, v: Union[str, None]):
        if v is None:
            self.__url = None
        else:
            self.__url = str(v)

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

    @property
    def recorddate(self) -> datetime.date:
        """datetime.date : The date associated with the record"""
        return self.__recorddate
    
    @recorddate.setter
    def recorddate(self, v: Union[datetime.date, str, None]):
        if v is None:
            self.__recorddate = datetime.date.today()
        elif isinstance(v, datetime.date):
            self.__recorddate = v
        elif isinstance(v, str):
            self.__recorddate = datetime.datetime.strptime(v, '%Y-%m-%d').date()
        else:
            raise TypeError('Invalid date type')

    @property
    def citations(self) -> list:
        """list: Any associated Citation objects"""
        return self.__citations

    @property
    def implementations(self) -> list:
        """list: Any associated Implementation objects"""
        return self.__implementations

    @property
    def elements(self) -> list:
        """list: elements associated with the potential"""
        return self.__elements

    @elements.setter
    def elements(self, v: Union[str, list, None]):
        if v is None:
            self.__elements = None
        else:
            self.__elements = aslist(v)
    
    @property
    def othername(self) -> Optional[str]:
        """str or None: Alternate name for what the potential models"""
        return self.__othername
    
    @othername.setter
    def othername(self, v: Optional[str]):
        if v is None:
            self.__othername = None
        else:
            self.__othername = str(v)
    
    @property
    def fictional(self) -> bool:
        """bool: Indicates if the potential is classified as fictional"""
        return self.__fictional
    
    @fictional.setter
    def fictional(self, v: bool):
        assert isinstance(v, bool)
        self.__fictional = v
    
    @property
    def modelname(self) -> Optional[str]:
        """str: Extra tag for differentiating potentials when needed"""
        return self.__modelname
    
    @modelname.setter
    def modelname(self, v: Optional[str]):
        if v is None:
            self.__modelname = None
        else:
            self.__modelname = str(v)

    @property
    def notes(self) -> Optional[str]:
        """str or None: Any extra notes associated with the potential"""
        return self.__notes

    @notes.setter
    def notes(self, v: Optional[str]):
        if v is None:
            self.__notes = None
        else:
            self.__notes = str(v)

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        data = {}
        
        # Copy class attributes to dict
        data['name'] = self.name
        data['key'] = self.key
        data['id'] = self.id
        data['url'] = self.url
        data['recorddate'] = self.recorddate
        data['notes'] = self.notes
        data['fictional'] = self.fictional
        data['elements'] = self.elements
        data['othername'] = self.othername
        data['modelname'] = self.modelname
        
        data['citations'] = []
        for citation in self.citations:
            data['citations'].append(citation.metadata())

        data['implementations'] = []
        for implementation in self.implementations:
            data['implementations'].append(implementation.metadata())

        return data

    def build_model(self) -> DM:
        """
        Generates and returns model content based on the values set to object.
        """
        # Initialize model
        model = DM()
        model['interatomic-potential'] = potential = DM()
        
        # Build identifiers
        potential['key'] = self.key
        potential['id'] = self.id
        if self.url is not None:
            potential['URL'] = self.url
        potential['record-version'] = str(self.recorddate)
        
        # Build description
        potential['description'] = description = DM()
        for citation in self.citations:
            description.append('citation', citation.build_model()['citation'])
        if self.notes is not None:
            description['notes'] = DM([('text', self.notes)])
        
        # Build implementations
        for implementation in self.implementations:
            potential.append('implementation', implementation.build_model()['implementation'])

        # Build element information
        if self.fictional:
            for element in self.elements:
                potential.append('fictional-element', element)
        else:
            for element in self.elements:
                potential.append('element', element)
        if self.othername is not None:
            potential['other-element'] = self.othername

        self._set_model(model)
        return model
        
    def add_citation(self, **kwargs):
        """
        Initializes a new Citation object and appends it to the citations list.
        """
        self.citations.append(Citation(**kwargs))

    def add_implementation(self, **kwargs):
        """
        Initializes a new Implementation object and appends it to the implementations list.
        """
        implementation = Implementation(**kwargs)
        for imp in self.implementations:
            if imp.id == implementation.id:
                raise ValueError(f'Implementation with id {imp.id} already exists')
        self.implementations.append(implementation)

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        return {
            'key': load_query(
                style='str_match',
                name='key', 
                path=f'{self.modelroot}.key',
                description="search based on potential UUID key"),
            'id': load_query(
                style='str_match',
                name='id',
                path=f'{self.modelroot}.id',
                description="search based on potential id"),
            'notes': load_query(
                style='str_contains',
                name='notes',
                path=f'{self.modelroot}.notes',
                description='search potential notes for contained strings'),
            'fictional': load_query(
                style='str_match',
                name='fictional',
                path=f'{self.modelroot}.fictional-element',
                description='search for fictional potentials'),
            'element': load_query(
                style='list_contains',
                name='elements',
                path=f'{self.modelroot}.element',
                description='search based on potential elements'),
            'othername': load_query(
                style='str_match',
                name='othername',
                path=f'{self.modelroot}.other-element',
                description='search based on the othername field'),
            'year': load_query(
                style='int_match',
                name='year', parent='citations',
                path=f'{self.modelroot}.description.citation.publication-date.year',
                description='search based on publication year'),
            'author': load_query(
                style='str_contains',
                name='author', parent='citations',
                path=f'{self.modelroot}.description.citation.author.surname',
                description='search based on publication authors'),
            'abstract': load_query(
                style='str_contains',
                name='abstract', parent='citations',
                path=f'{self.modelroot}.description.citation.abstract',
                description='search publication abstract for contained strings'),
        }
