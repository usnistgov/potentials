# coding: utf-8
# Standard libraries
import uuid
import datetime

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# Local imports
from .Citation import Citation
from .Implementation import Implementation
from ..tools import aslist

from datamodelbase.record import Record
from datamodelbase import query

modelroot = 'interatomic-potential'

class Potential(Record):
    """
    Class for representing Potential metadata records.
    """

    @property
    def style(self):
        """str: The record style"""
        return 'Potential'

    @property
    def xsl_filename(self):
        return ('potentials.xsl', 'Potential.xsl')

    @property
    def xsd_filename(self):
        return ('potentials.xsd', 'Potential.xsd')

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return modelroot

    def load_model(self, model, name=None):

        super().load_model(model, name=name)
        potential = self.model[modelroot]
        
        # Extract information
        self.key = potential['key']
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
            except:
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


    def set_values(self, name=None, elements=None, key=None,
                   othername=None, fictional=False, modelname=None,
                   notes=None, recorddate=None, citations=None,
                   implementations=None):

        # Build new record
        self.elements = elements
        self.key = key
        self.othername = othername
        self.fictional = fictional
        self.modelname = modelname
        self.notes = notes
        self.recorddate = recorddate
        
        self.__citations = []
        if citations is not None:
            for citation in aslist(citations):
                if isinstance(citation, dict):
                    self.add_citation(**citation)
                elif isinstance(citation, Citation):
                    self.citations.append(citation)
        
        self.__implementations = []
        if implementations is not None:
            for implementation in aslist(implementations):
                if isinstance(implementation, dict):
                    self.add_implementation(**implementation)
                elif isinstance(implementation, Implementation):
                    self.implementations.append(implementation)

        # Set name
        if name is not None:
            self.name = name
        else:
            self.name = f'potential.{self.id}'

    @property
    def key(self):
        """str : The potential's uuid4 key"""
        return self.__key
    
    @key.setter
    def key(self, v):
        if v is None:
            self.__key = str(uuid.uuid4())
        else:
            self.__key = str(v)

    @property
    def id(self):
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
    def impid_prefix(self):
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
    def recorddate(self):
        return self.__recorddate
    
    @recorddate.setter
    def recorddate(self, v):
        if v is None:
            self.__recorddate = datetime.date.today()
        elif isinstance(v, datetime.date):
            self.__recorddate = v
        elif isinstance(v, str):
            self.__recorddate = datetime.datetime.strptime(v, '%Y-%m-%d').date()
        else:
            raise TypeError('Invalid date type')

    @property
    def citations(self):
        return self.__citations

    @property
    def implementations(self):
        return self.__implementations

    @property
    def elements(self):
        return self.__elements

    @elements.setter
    def elements(self, v):
        if v is None:
            self.__elements = None
        else:
            self.__elements = aslist(v)
    
    @property
    def othername(self):
        return self.__othername
    
    @othername.setter
    def othername(self, v):
        if v is None:
            self.__othername = None
        else:
            self.__othername = str(v)
    
    @property
    def fictional(self):
        return self.__fictional
    
    @fictional.setter
    def fictional(self, v):
        assert isinstance(v, bool)
        self.__fictional = v
    
    @property
    def modelname(self):
        return self.__modelname
    
    @modelname.setter
    def modelname(self, v):
        if v is None:
            self.__modelname = None
        else:
            self.__modelname = str(v)

    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, v):
        if v is None:
            self.__notes = None
        else:
            self.__notes = str(v)

    def metadata(self):
        """Returns a flat dict representation of the object"""
        data = {}
        
        # Copy class attributes to dict
        data['name'] = self.name
        data['key'] = self.key
        data['id'] = self.id
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

    def build_model(self):
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict: The data model content.
        """
        # Initialize model
        model = DM()
        model['interatomic-potential'] = potential = DM()
        
        # Build identifiers
        potential['key'] = self.key
        potential['id'] = self.id
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
        self.citations.append(Citation(**kwargs))

    def add_implementation(self, **kwargs):
        implementation = Implementation(**kwargs)
        for imp in self.implementations:
            if imp.id == implementation.id:
                raise ValueError(f'Implementation with id {imp.id} already exists')
        self.implementations.append(implementation)

    @staticmethod
    def pandasfilter(dataframe, name=None, key=None, id=None,
                     notes=None, fictional=None, element=None,
                     othername=None, modelname=None, year=None, author=None,
                     abstract=None):
        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.str_match.pandas(dataframe, 'key', key)
            &query.str_match.pandas(dataframe, 'id', id)
            &query.str_contains.pandas(dataframe, 'notes', notes)
            &query.str_match.pandas(dataframe, 'fictional', fictional)
            &query.in_list.pandas(dataframe, 'elements', element)
            &query.str_match.pandas(dataframe, 'othername', othername)
            &query.str_match.pandas(dataframe, 'modelname', modelname)
            &query.int_match.pandas(dataframe, 'year', year, parent='citations')
            &query.str_contains.pandas(dataframe, 'author', author, parent='citations')
            &query.str_contains.pandas(dataframe, 'abstract', abstract, parent='citations')
        )
        return matches

    @staticmethod
    def mongoquery(name=None, key=None, id=None,
                   notes=None, fictional=None, element=None,
                   othername=None, modelname=None, year=None, author=None,
                   abstract=None):
        mquery = {}
        query.str_match.mongo(mquery, f'name', name)

        root = f'content.{modelroot}'
        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_contains.mongo(mquery, f'{root}.notes', notes)
        
        query.int_match.mongo(mquery, f'{root}.description.citation.publication-date.year', year)
        query.str_contains.mongo(mquery, f'{root}.description.citation.author.surname', author)
        query.str_contains.mongo(mquery, f'{root}.description.citation.abstract', abstract)
        return mquery

    @staticmethod
    def cdcsquery(key=None, id=None, notes=None,
                  fictional=None, element=None, othername=None, modelname=None,
                  year=None, author=None, abstract=None):
        mquery = {}
        root = modelroot
        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_contains.mongo(mquery, f'{root}.notes', notes)
        
        query.int_match.mongo(mquery, f'{root}.description.citation.publication-date.year', year)
        query.str_contains.mongo(mquery, f'{root}.description.citation.author.surname', author)
        query.str_contains.mongo(mquery, f'{root}.description.citation.abstract', abstract)
        return mquery
