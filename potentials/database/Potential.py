# Standard libraries
import uuid
import datetime
from pathlib import Path

from DataModelDict import DataModelDict as DM

import requests

from .Citation import Citation
from ..tools import aslist, parse_authors
from .. import rootdir

class Potential(object):
    """
    Class for representing Potential metadata records.
    """
    def __init__(self, model=None, dois=None, elements=None, key=None,
                 othername=None, fictional=False, modelname=None,
                 notes=None, recorddate=None, citations=None,
                 developers=None, year=None):
        """
        Creates a new Potential object.

        Parameters
        ----------
        model
        dois
        elements
        key
        othername
        fictional
        modelname
        recorddate
        notes
        citations
        """

        if model is not None:
            # Load existing record
            try:
                assert dois is None
                assert elements is None
                assert key is None
                assert othername is None
                assert fictional is False
                assert modelname is None
                assert recorddate is None
                assert notes is None
                assert developers is None
                assert year is None
            except:
                raise TypeError('model cannot be given with any other parameter')
            else:
                self.load(model, citations=citations)
            
        else:
            # Build new record
            self.elements = elements
            self.key = key
            self.recorddate = recorddate
            self.othername = othername
            self.fictional = fictional
            self.modelname = modelname
            self.notes = notes
            self.citations = citations
            self.developers = developers
            self.year = year
            if dois is not None:
                self.dois = dois
    
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
    def dois(self):
        return self.__dois

    @dois.setter
    def dois(self, v):
        if v is None:
            self.__dois = None
            self.__citations = None
        else:
            self.__dois = aslist(v)

            # Get current citations (to avoid reloading)
            if self.citations is None:
                oldcitations = []
            else:
                oldcitations = self.citations

            # Set citations accordingly
            self.__citations = []
            for doi in self.dois:
                match = False
                for old in oldcitations:
                    if old.doi == doi:
                        self.__citations.append(old)
                        match = True
                        break
                if not match:
                    self.__citations.append(Citation(doi))

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

    @property
    def developers(self):
        return self.__developers

    @developers.setter
    def developers(self, v):
        if v is None:
            self.__developers = None
        else:
            self.__developers = str(v)

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, v):
        if v is None:
            self.__year = None
        else:
            self.__year = str(v)
        
    @property
    def citations(self):
        return self.__citations

    @citations.setter
    def citations(self, v):
        if v is None:
            self.__citations = None
            self.__dois = None
        else:
            self.__citations = aslist(v)
            
            # Update dois accordingly
            self.__dois = []
            for citation in self.citations:
                self.__dois.append(citation.doi)

    @classmethod
    def fetch(cls, key, localdir=None, verbose=True, citations=None):
        """
        Fetches saved potential content.  First checks localdir, then
        potentials github.

        Parameters
        ----------
        key : str
            The potential key to load.
        localdir : Path, optional
            The local directory for the potential JSON files.  If not given,
            will use the default path in potentials/data/potential directory.
        """
        if localdir is None:
            localdir = Path(rootdir, '..', 'data', 'potential')
        localfile = Path(localdir, f'{key}.json')
        
        if localfile.is_file():
            if verbose:
                print('potential loaded from localdir')
            return cls(model=localfile, citations=citations)
            
        else:
            r = requests.get(f'https://github.com/usnistgov/potentials/raw/master/data/potential/{key}.json')
            try:
                r.raise_for_status()
            except:
                raise ValueError(f'no potential with key {key} found')
            else:
                if verbose:
                    print('potential downloaded from github')
                return cls(model=r.text, citations=citations)

    def save(self, localdir=None):
        """
        Saves content locally

        Parameters
        ----------
        localdir : Path, optional
            The local directory for the potential JSON files.  If not given,
            will use the default path in potentials/data/potential directory.
        """
        if localdir is None:
            localdir = Path(rootdir, '..', 'data', 'potential')

        localfile = Path(localdir, f'{self.key}.json')

        with open(localfile, 'w', encoding='UTF-8') as f:
            self.asmodel().json(fp=f, indent=4)

    def asdict(self):
        """
        Builds flat dictionary representation of the potential.
        """
        data = {}
        
        # Copy class attributes to dict
        data['key'] = self.key
        data['id'] = self.id
        data['recorddate'] = self.recorddate
        data['dois'] = self.dois
        data['notes'] = self.notes
        data['fictional'] = self.fictional
        data['elements'] = self.elements
        data['othername'] = self.othername
        data['modelname'] = self.modelname
        data['developers'] = self.developers
        data['year'] = self.year
        
        return data

    def asmodel(self):
        """
        Builds data model (tree-like JSON/XML) representation for the potential.
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
        if self.developers is not None:
            description['developers'] = self.developers
        if self.year is not None:
            description['year'] = self.year
        if self.modelname is not None:
            description['model-name'] = self.modelname
        if self.dois is not None:
            for doi in self.dois:
                description.append('citation', DM([('DOI', doi)]))
        if self.notes is not None:
            description['notes'] = DM([('text', self.notes)])
        
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

    def load(self, model, citations=None):
        """
        Load a Potential model into the Potential class.

        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        """
        # Set given citations objects
        self.citations = citations
        
        # Load model
        model = DM(model)
        potential = model.find('interatomic-potential')
        
        # Extract information
        self.key = potential['key']
        self.recorddate = potential['record-version']
        self.developers = potential.get('developers', None)
        self.year = potential.get('year', None)
        
        description = potential['description']
        self.developers = description.get('developers', None)
        self.year = description.get('year', None)
        self.modelname = description.get('model-name', None)
        dois = []
        for citation in description.iteraslist('citation'):
            dois.append(citation['DOI'])
        self.dois = dois
        if 'notes' in description:
            self.notes = description['notes']['text']
        else:
            self.notes = None

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
        
        if self.id != potential['id']:
            print(f"Different ids: {self.id} != {potential['id']} {self.key}")

    def html(self):
        htmlstr = f'<h3>{self.id}</h3>'
        for citation in self.citations:
            htmlstr += f'<b>Citation:</b> {citation.html()}</br>\n'
        if self.notes is not None:
            htmlstr += f'<b>Notes:</b> {self.notes}</br>\n'
        
        return htmlstr

    @property
    def id(self):
        if self.citations is not None and len(self.citations) > 0:
            first_citation = self.citations[0]
            authors = parse_authors(first_citation.content['author'])
            year = first_citation.content['year']
        elif self.developers is not None and self.year is not None:
            authors = parse_authors(self.developers)
            year = self.year
        else:
            return None
        
        potential_id = str(year) + '-'
        
        if len(authors) <= 4:
            for author in authors:
                potential_id += '-' + author['surname']
                potential_id += '-' + author['givenname'].replace('-', '').replace('.', '-').strip('-')
        else:
            for author in authors[:3]:
                potential_id += '-' + author['surname']
                potential_id += '-' + author['givenname'].replace('-', '').replace('.', '-').strip('-')
            potential_id += '-et-al'
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
        
        replace_keys = {"'":'', 'á':'a', 'ä':'a', 'ö':'o', 'ø':'o', ' ':'-', 'č':'c', 'ğ':'g', 'ü':'u', 'é':'e', 'Ç':'C', 'ı': 'i'}
        for k,v in replace_keys.items():
            potential_id = potential_id.replace(k,v)
        
        return potential_id
