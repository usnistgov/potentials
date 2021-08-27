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

class Potential(Record):
    """
    Class for representing Potential metadata records.
    """

    def __init__(self, model=None, name=None, **kwargs):
        """
        Initializes a Record object for a given style.
        
        Parameters
        ----------
        model : str, file-like object, DataModelDict
            The contents of the record.
        name : str, optional
            The unique name to assign to the record.  If model is a file
            path, then the default record name is the file name without
            extension.
        
        """
        # Set default values
        self.elements = None
        self.key = None
        self.othername = None
        self.fictional = False
        self.modelname = None
        self.notes = None
        self.recorddate = datetime.date.today()
        self.__citations = []
        self.__implementations = []

        super().__init__(model=model, name=name, **kwargs)


    @property
    def style(self):
        """str: The record style"""
        return 'Potential'

    @property
    def xsl_filename(self):
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'Potential.xsl')

    @property
    def xsd_filename(self):
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'Potential.xsd')

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'interatomic-potential'

    def load_model(self, model, name=None):
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
        super().load_model(model, name=name)
        potential = self.model[self.modelroot]
        
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
                   othername=None, fictional=None, modelname=None,
                   notes=None, recorddate=None, citations=None,
                   implementations=None):
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
        
        if elements is not None:
            self.elements = elements
        if key is not None:
            self.key = key
        if othername is not None:
            self.othername = othername
        if fictional is not None:
            self.fictional = fictional
        if modelname is not None:
            self.modelname = modelname
        if notes is not None:
            self.notes = notes
        if recorddate is not None:
            self.recorddate = recorddate
        
        if citations is not None:
            self.__citations = []
            if citations is not None:
                for citation in aslist(citations):
                    if isinstance(citation, dict):
                        self.add_citation(**citation)
                    elif isinstance(citation, Citation):
                        self.citations.append(citation)
        
        if implementations is not None:
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
            try:
                self.name = f'potential.{self.id}'
            except:
                self.name = 'potential.unknown'

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
        """datetime.date : The date associated with the record"""
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
        """list: Any associated Citation objects"""
        return self.__citations

    @property
    def implementations(self):
        """list: Any associated Implementation objects"""
        return self.__implementations

    @property
    def elements(self):
        """list: elements associated with the potential"""
        return self.__elements

    @elements.setter
    def elements(self, v):
        if v is None:
            self.__elements = None
        else:
            self.__elements = aslist(v)
    
    @property
    def othername(self):
        """str or None: Alternate name for what the potential models"""
        return self.__othername
    
    @othername.setter
    def othername(self, v):
        if v is None:
            self.__othername = None
        else:
            self.__othername = str(v)
    
    @property
    def fictional(self):
        """bool: Indicates if the potential is classified as fictional"""
        return self.__fictional
    
    @fictional.setter
    def fictional(self, v):
        assert isinstance(v, bool)
        self.__fictional = v
    
    @property
    def modelname(self):
        """str: Extra tag for differentiating potentials when needed"""
        return self.__modelname
    
    @modelname.setter
    def modelname(self, v):
        if v is None:
            self.__modelname = None
        else:
            self.__modelname = str(v)

    @property
    def notes(self):
        """str or None: Any extra notes associated with the potential"""
        return self.__notes

    @notes.setter
    def notes(self, v):
        if v is None:
            self.__notes = None
        else:
            self.__notes = str(v)

    def metadata(self):
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
        Generates and returns model content based on the values set to object.
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

    def pandasfilter(self, dataframe, name=None, key=None, id=None,
                     notes=None, fictional=None, element=None,
                     othername=None, modelname=None, year=None, author=None,
                     abstract=None):
        """
        Filters a pandas.DataFrame based on kwargs values for the record style.
        
        Parameters
        ----------
        dataframe : pandas.DataFrame
            A table of metadata for multiple records of the record style.
        name : str or list
            The record name(s) to parse by.
        key : str or list
            The unique potential id(s) to parse by.
        id : str or list
            The UUID4 potential key(s) to parse by.
        notes : str or list
            Terms in the notes to parse for.
        fictional : bool or list
            Value of fictional to parse for.
        element : str or list
            Element(s) to parse by.
        othername : str or list
            Other name(s) to parse by.
        modelname : str or list
            Model name(s) to parse by.
        year : int or list
            Publication/creation year(s) to parse by.
        author : str or list
            Author(s) to parse by.  Only last names guaranteed to work.
        abstract : str or list
            Terms in the publication abstracts to parse for.
        
        Returns
        -------
        pandas.Series, numpy.NDArray
            Boolean map of matching values
        """
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

    def mongoquery(self, name=None, key=None, id=None,
                   notes=None, fictional=None, element=None,
                   othername=None, modelname=None, year=None, author=None,
                   abstract=None):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        name : str or list
            The record name(s) to parse by.
        key : str or list
            The unique potential id(s) to parse by.
        id : str or list
            The UUID4 potential key(s) to parse by.
        notes : str or list
            Terms in the notes to parse for.
        fictional : bool or list
            Value of fictional to parse for.
        element : str or list
            Element(s) to parse by.
        othername : str or list
            Other name(s) to parse by.
        modelname : str or list
            Model name(s) to parse by.
        year : int or list
            Publication/creation year(s) to parse by.
        author : str or list
            Author(s) to parse by.  Only last names guaranteed to work.
        abstract : str or list
            Terms in the publication abstracts to parse for.
        
        Returns
        -------
        dict
            The Mongo-style query
        """        
        
        mquery = {}
        query.str_match.mongo(mquery, f'name', name)

        root = f'content.{self.modelroot}'
        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_contains.mongo(mquery, f'{root}.notes', notes)
        
        query.int_match.mongo(mquery, f'{root}.description.citation.publication-date.year', year)
        query.str_contains.mongo(mquery, f'{root}.description.citation.author.surname', author)
        query.str_contains.mongo(mquery, f'{root}.description.citation.abstract', abstract)
        return mquery

    def cdcsquery(self, key=None, id=None, notes=None,
                  fictional=None, element=None, othername=None, modelname=None,
                  year=None, author=None, abstract=None):
        """
        Builds a CDCS-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        key : str or list
            The unique potential id(s) to parse by.
        id : str or list
            The UUID4 potential key(s) to parse by.
        notes : str or list
            Terms in the notes to parse for.
        fictional : bool or list
            Value of fictional to parse for.
        element : str or list
            Element(s) to parse by.
        othername : str or list
            Other name(s) to parse by.
        modelname : str or list
            Model name(s) to parse by.
        year : int or list
            Publication/creation year(s) to parse by.
        author : str or list
            Author(s) to parse by.  Only last names guaranteed to work.
        abstract : str or list
            Terms in the publication abstracts to parse for.
        
        Returns
        -------
        dict
            The CDCS-style query
        """
        
        mquery = {}
        root = self.modelroot
        query.str_match.mongo(mquery, f'{root}.key', key)
        query.str_match.mongo(mquery, f'{root}.id', id)
        query.str_contains.mongo(mquery, f'{root}.notes', notes)
        
        query.int_match.mongo(mquery, f'{root}.description.citation.publication-date.year', year)
        query.str_contains.mongo(mquery, f'{root}.description.citation.author.surname', author)
        query.str_contains.mongo(mquery, f'{root}.description.citation.abstract', abstract)
        return mquery
