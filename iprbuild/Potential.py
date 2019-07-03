# Standard libraries
import os
import uuid
import string
import datetime

import bibtexparser

from DataModelDict import DataModelDict as DM

class Implementation(object):
    """
    Class for representing the implementation portion of Potential metadata
    records.
    """
    def __init__(self, model=None, style=None, key=None, id=None, status='active', date=None,
                 notes=None):
        """
        Parameters
        ----------
        style
        key
        id
        status
        date
        notes
        """
        if model is not None:
            self.model = model
        else:
            self.build(style,
                       key=key,
                       id=id,
                       status=status,
                       date=date,
                       notes=notes)

    def build(self, style, key=None, id=None, status='active', date=None,
              notes=None):
        """
        Parameters
        ----------
        style
        key
        id
        status
        date
        notes
        """
        self.model = DM()
        if key is None:
            self.model['key'] = str(uuid.uuid4())
        else:
            self.model['key'] = key
        
        if id is not None:
            self.id = id
        
        self.status = status

        if date is None:
            self.date = str(datetime.date.today())
        else:
            self.date = str(date)
        self.style = style
        
        if notes is not None:
            self.notes = notes
        
    @property
    def key(self):
        return self.model['key']
    
    @property
    def id(self):
        try:
            return self.model['id']
        except:
            return None
    
    @id.setter
    def id(self, value):
        if 'id' not in self.model:
            reorder = True        
        self.model['id'] = str(value)
        if reorder:
            self.model.move_to_end('id', last=False)
            self.model.move_to_end('key', last=False)

    @property
    def status(self):
        return self.model['status']

    @status.setter
    def status(self, value):
        self.model['status'] = str(value)

    @property
    def date(self):
        return self.model['date']
    
    @date.setter
    def date(self, value):
        self.model['date'] = str(value)

    @property
    def style(self):
        return self.model['type']

    @style.setter
    def style(self, value):
        self.model['type'] = str(value)
    
    @property
    def notes(self):
        try:
            return self.model['notes']['text']
        except:
            return None

    @notes.setter
    def notes(self, value):
        try:
            self.model['notes']['text'] = str(value)
        except:
            self.model['notes'] = DM()
            self.model['notes']['text'] = str(value)

    def build_artifact(self, url, label=None):
        artifact = DM()
        artifact['web-link'] = DM()
        artifact['web-link']['URL'] = url
        if label is not None:
            artifact['web-link']['label'] = label
        artifact['web-link']['link-text'] = os.path.basename(url)

        return artifact

    def add_artifacts(self, urls, labels=None):
        if labels is None:
            labels = [None for i in range(len(urls))]
        assert len(labels) == len(urls), 'Length of urls and labels not the same'
        
        for url, label in zip(urls, labels):
            artifact = self.build_artifact(url, label)
            self.model.append('artifact', artifact)
    
    def build_link(self, url, label=None):
        link = DM()
        link['web-link'] = DM()
        link['web-link']['URL'] = url
        if label is not None:
            link['web-link']['label'] = label
        link['web-link']['link-text'] = url
        
        return link

    def add_links(self, urls, labels=None):
        if labels is None:
            labels = [None for i in range(len(urls))]
        assert len(labels) == len(urls), 'Length of urls and labels not the same'
        
        for url, label in zip(urls, labels):
            link = self.build_link(url, label)
            self.model.append('link', link)

    def build_parameter(self, line):
        parameter = DM()
        parameter['name'] = line
        return parameter

    def add_parameters(self, lines):
        for line in lines:
            parameter = self.build_parameter(line)
            self.model.append('parameter', parameter)

class Potential(object):
    """
    Class for representing full Potential metadata records.
    """
    def __init__(self, model=None, bib_databases=None, elements=None, key=None,
                 othername=None, fictional=False, modelname=None,
                 notes=None):
        """
        Creates a new Potential object.

        Parameters
        ----------
        model
        bib_databases
        elements
        key
        othername
        fictional
        modelname
        notes
        """

        if model is not None:
            # Load existing record
            try:
                assert bib_databases is None
                assert elements is None
                assert key is None
                assert othername is None
                assert fictional is False
                assert modelname is None
                assert notes is None
            except:
                raise TypeError('model cannot be given with any other parameter')
            else:
                self.load(model)
            
        else:
            # Build new record
            self.build(elements,
                       bib_databases=bib_databases,
                       key=key,
                       othername=othername,
                       fictional=fictional,
                       modelname=modelname,
                       notes=notes)
            

    def build(self, elements, bib_databases=None, key=None,
              othername=None, fictional=False, modelname=None,
              notes=None):
        """
        Builds new Potential model content.

        Parameters
        ----------
        bib_databases
        elements
        key
        othername
        fictional
        modelname
        notes
        """
        # Initialize model
        self.model = DM()
        self.model['interatomic-potential'] = potential = DM()
        
        # Build identifiers
        if key is None:
            potential['key'] = str(uuid.uuid4())
        else:
            potential['key'] = key

        potential['record-version'] = str(datetime.date.today())

        # Build description
        potential['description'] = self.description = DM()
        self.description['citation'] = None
        if notes is not None:
            self.notes = notes

        # Build list for implementations
        self.implementations = []
        potential['implementation'] = None
        
        # Build element information
        if fictional is True:
            for element in elements:
                potential.append('fictional-element', element)
        else:
            for element in elements:
                potential.append('element', element)
        if othername is not None:
            potential['other-element'] = str(othername)
        self.__elements = tuple(elements)
        self.__othername = othername
        self.__fictional = fictional
        self.__modelname = modelname

        # Add citation(s) and potential_id
        if bib_databases is not None:
            self.replace_citations(bib_databases)
            potential['id'] = self.id
            potential.move_to_end('id', last=False)
            potential.move_to_end('key', last=False)

    def load(self, model):
        """
        Load a Potential model into the Potential class.

        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        """
        # Load model
        self.model = DM(model)
        potential = self.model['interatomic-potential']
        
        # Extract information
        self.__key = potential['key']
        self.description = potential['description']
        self.implementations = []
        self.model['implementation'] = None
        for implementation in potential.aslist('implementation'):
            self.implementations.append(Implementation(model=implementation))

        felements = potential.aslist('fictional-element')
        oelements = potential.aslist('other-element')
        elements = potential.aslist('element')
        
        if len(felements) > 0:
            assert len(elements) == 0
            self.__fictional = True
            self.__elements = tuple(felements)
        else:
            assert len(elements) > 0
            self.__fictional = False
            self.__elements = tuple(elements)
        if len(oelements) > 0:
            assert len(oelements) == 1
            self.__othername = str(oelements[0])
        else:
            self.__othername = None
        
        self.__modelname = None
        if self.id != potential['id']:
            self.__modelname = str(potential['id']).split('-')[-1]
            if self.id != potential['id']:
                raise ValueError(f"Different ids: {self.id} != {potential['id']}")

    def update_version(self):
        """
        Updates the model's record-version element to today's date
        """
        potential = self.model['interatomic-potential']
        potential['record-version'] = str(datetime.date.today())

    def build_citation(self, bib_database):
        """
        Converts bibtex into xml description

        Parameters
        ----------
        bib_database : bibtexparser.bibdatabase.BibDatabase
            Object containing bibtex data
        """
        bib_dict = bib_database.entries[0]
        citation = DM()
        
        if bib_dict['ENTRYTYPE'] == 'article':
            citation['document-type'] = 'journal' 
            citation['title'] = bib_dict['title']
            citation['author'] = self.parse_authors(bib_dict['author'])
            citation['publication-name'] = bib_dict['journal']
            citation['publication-date'] = DM()
            citation['publication-date']['year'] = bib_dict['year']
            citation['volume'] = bib_dict['volume']
            if 'number' in bib_dict:
                citation['issue'] = bib_dict['number']
            elif 'issue' in bib_dict:
                citation['issue'] = bib_dict['issue']
            if 'abstract' in bib_dict:
                citation['abstract'] = bib_dict['abstract']
            if 'pages' in bib_dict:
                citation['pages'] = bib_dict['pages'].replace('--', '-')
            citation['DOI'] = bib_dict['doi']
        
        elif bib_dict['ENTRYTYPE'] == 'unpublished':
            citation['document-type'] = 'unspecified'
            citation['title'] = bib_dict['title']
            citation['author'] = self.parse_authors(bib_dict['author'])
            citation['publication-date'] = DM()
            citation['publication-date']['year'] = bib_dict['year']
        
        citation['bibtex'] = bibtexparser.dumps(bib_database)
        return citation

    def add_citation(self, bib_database):
        citation = self.build_citation(bib_database)
        if self.description['citation'] is None:
            self.description['citation'] = citation
        else:
            self.description.append('citation', citation)
        self.update_version()

    def replace_citations(self, bib_databases):
        self.description['citation'] = None
        for bib_database in bib_databases:
            self.add_citation(bib_database)

    def parse_authors(self, authors):
        """
        Parse bibtex authors field.
        """
        author_dicts = []
        
        # remove ands from bib
        splAuth = authors.split(' and ') 
        
        author = ' , '.join(splAuth)
        list_authors = author.split(' , ') #used for given/surname splitting 
        for k in range(len(list_authors)):
            author_dict = DM()
            
            if '.' in list_authors[k]:  #if . is in initials, find the most right and strip given name and surname
                l = list_authors[k].rindex(".")
                author_dict['given-name'] = list_authors[k][:l+1].strip()
                author_dict['surname'] = list_authors[k][l+1:].strip()
                
            else: #otherwise just split by the most right space
                l = list_authors[k].rindex(" ")
                author_dict['given-name'] = list_authors[k][:l+1].strip()
                author_dict['surname'] = list_authors[k][l+1:].strip()
                
            # Change given-name just into initials
            given = ''
            for letter in str(author_dict['given-name']).replace(' ', '').replace('.', ''):
                if letter in string.ascii_uppercase:
                    given += letter +'.'
                elif letter in ['-']:
                    given += letter
            author_dict['given-name'] = given
            
            author_dicts.append(author_dict)
            
        return author_dicts

    @property
    def id(self):
        try:
            first_citation = self.description.aslist('citation')[0]
        except:
            return None
        authors = first_citation.aslist('author')
        year = first_citation['publication-date']['year']
        
        potential_id = str(year) + '-'
        
        if len(authors) <= 4:
            for author in authors:
                potential_id += '-' + author['surname']
                potential_id += '-' + author['given-name'].replace('-', '').replace('.', '-').strip('-')
        else:
            for author in authors[:3]:
                potential_id += '-' + author['surname']
                potential_id += '-' + author['given-name'].replace('-', '').replace('.', '-').strip('-')
            potential_id += '-et-al'
        potential_id += '-'
        
        if self.__fictional is True:
            potential_id += '-fictional'
        
        if self.__othername is not None:
            potential_id += '-' + str(self.__othername)
        else:
            for element in self.__elements:
                potential_id += '-' + element
        
        if self.__modelname is not None:
            potential_id += '-' + str(self.__modelname)
        
        replace_keys = {"'":'', 'á':'a', 'ä':'a', 'ö':'o', 'ø':'o', ' ':'-', 'č':'c', 'ğ':'g', 'ü':'u', 'é':'e', 'Ç':'C', 'ı': 'i'}
        for k,v in replace_keys.items():
            potential_id = potential_id.replace(k,v)
        
        return potential_id
    
    @property
    def notes(self):
        try:
            return self.description['notes']['text']
        except:
            return None

    @notes.setter
    def notes(self, value):
        try:
            self.description['notes']['text'] = str(value)
        except:
            self.description['notes'] = DM()
            self.description['notes']['text'] = str(value)
    
    @property
    def key(self):
        return self.model['interatomic-potential']['key']

    @property
    def elements(self):
        return self.__elements
    
    @property
    def othername(self):
        return self.__othername
    
    @property
    def fictional(self):
        return self.__fictional
    
    @property
    def modelname(self):
        return self.__modelname

    @property
    def versiondate(self):
        return self.model['interatomic-potential']['record-version']

    def append_implementation(self, implementation):
        """
        Properly appends an Implementation object
        
        implementation : Implementation
            The implementation to append to the model
        """
        if self.model['interatomic-potential']['implementation'] is None:
            self.model['interatomic-potential']['implementation'] = implementation.model
        else:
            self.model['interatomic-potential'].append('implementation',
                                                   implementation.model)
        self.implementations.append(implementation)