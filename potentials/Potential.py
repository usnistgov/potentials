# coding: utf-8
# Standard libraries
import uuid
import datetime

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# Local imports
from .Citation import Citation
from .Implementation import Implementation
from .tools import aslist

class Potential(object):
    """
    Class for representing Potential metadata records.
    """
    def __init__(self, model=None, elements=None, key=None,
                 othername=None, fictional=False, modelname=None,
                 notes=None, recorddate=None, citations=None,
                 implementations=None):
        """
        Creates a new Potential object.

        Parameters
        ----------
        model : str or DataModelDict, optional
            Model content or file path to model content.
        elements
        key
        othername
        fictional
        modelname
        notes
        recorddate
        citations
        implementations
        """

        if model is not None:
            # Load existing record
            try:
                assert elements is None
                assert key is None
                assert othername is None
                assert fictional is False
                assert modelname is None
                assert notes is None
                assert recorddate is None
                assert citations is None
                assert implementations is None
            except:
                raise TypeError('model cannot be given with any other parameter')
            else:
                self.load(model)
            
        else:
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
    
    def __str__(self):
        return f'Potential {self.id}'

    @property
    def key(self):
        return self.__key
    
    @key.setter
    def key(self, v):
        if v is None:
            self.__key = str(uuid.uuid4())
        else:
            self.__key = str(v)

    @property
    def id(self):
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
    
    def html(self):
        """Returns an HTML representation of the object."""
        htmlstr = f'<h3>{self.id}</h3>'
        for citation in self.citations:
            htmlstr += f'<b>Citation:</b> {citation.html()}</br>\n'
        if self.notes is not None:
            htmlstr += f'<b>Notes:</b> {self.notes}</br>\n'
        
        for implementation in self.implementations:
            htmlstr += '</br>' + implementation.html()

        return htmlstr

    def asdict(self):
        """Returns a flat dict representation of the object"""
        data = {}
        
        # Copy class attributes to dict
        data['key'] = self.key
        data['id'] = self.id
        data['recorddate'] = self.recorddate
        data['notes'] = self.notes
        data['fictional'] = self.fictional
        data['elements'] = self.elements
        data['othername'] = self.othername
        data['modelname'] = self.modelname
        data['citations'] = self.citations
        data['implementations'] = self.implementations
        
        return data

    def asmodel(self):
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
            description.append('citation', citation.asmodel()['citation'])
        if self.notes is not None:
            description['notes'] = DM([('text', self.notes)])
        
        # Build implementations
        for implementation in self.implementations:
            potential.append('implementation', implementation.asmodel()['implementation'])

        # Build element information
        if self.fictional:
            for element in self.elements:
                potential.append('fictional-element', element)
        else:
            for element in self.elements:
                potential.append('element', element)
        if self.othername is not None:
            potential['other-element'] = self.othername

        return model

    def load(self, model):
        """
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        """
        
        # Load model
        model = DM(model)
        potential = model.find('interatomic-potential')
        
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

    def add_citation(self, **kwargs):
        self.citations.append(Citation(**kwargs))

    def add_implementation(self, **kwargs):
        self.implementations.append(Implementation(**kwargs))

    
