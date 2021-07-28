# coding: utf-8
# Standard libraries
import string
from pathlib import Path

# https://github.com/avian2/unidecode
from unidecode import unidecode

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://bibtexparser.readthedocs.io/en/master/
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bibdatabase import BibDatabase

from datamodelbase.record import Record
from datamodelbase import query 

modelroot = 'citation'

class Citation(Record):
    """
    Class for representing Citation metadata records.
    """

    @property
    def style(self):
        """str: The record style"""
        return 'Citation'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return modelroot
    
    @property
    def xsl_filename(self):
        return ('potentials.xsl', 'Citation.xsl')

    @property
    def xsd_filename(self):
        return ('potentials.xsd', 'Citation.xsd')

    @property
    def bib(self):
        """dict : Contains the bibtex fields"""
        return self.__bib

    @property
    def doifname(self):
        """str: file path compatible form of doi"""
        try:
            name = self.bib['doi']
        except:
            name = self.bib['note']
        return name.lower().replace('/', '_')

    def load_model(self, model, name=None):
        """
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        name : str, optional
            The name to use when saving the record.
        """
        try:
            super().load_model(model, name=name)
        except:
            bibtex = model
        else:
            bibtex = self.model.find('bibtex')

        # Parse and extract content
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.loads(bibtex, parser=parser)
        assert len(bib_database.entries) == 1, 'bibtex must be for a single reference'
        
        self.__bib = bib_database.entries[0]
        try:
            self.name
        except:
            self.name = self.doifname

        try:
            self.model
        except:
            self.build_model()
    
    def set_values(self, name=None, **kwargs):

        # Set bib values
        self.__bib = {}
        for key, value in kwargs.items():
            self.bib[key] = str(value)

        # Set record name
        if name is None:
            self.name = self.doifname
        else:
            self.name = name

    def build_model(self):
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict: The data model content.
        """
        citmodel = DM()
        
        def asint(val):
            try:
                return int(val)
            except:
                return val

        if self.bib['ENTRYTYPE'] == 'article':
            citmodel['document-type'] = 'journal' 
            citmodel['title'] = self.bib['title']
            citmodel['author'] = self.parse_authors(self.bib['author'])
            citmodel['publication-name'] = self.bib['journal']
            citmodel['publication-date'] = DM()
            citmodel['publication-date']['year'] = asint(self.bib['year'])
            if 'volume' in self.bib:
                citmodel['volume'] = asint(self.bib['volume'])
            if 'number' in self.bib:
                citmodel['issue'] = asint(self.bib['number'])
            elif 'issue' in self.bib:
                citmodel['issue'] = asint(self.bib['issue'])
            if 'abstract' in self.bib:
                citmodel['abstract'] = self.bib['abstract']
            if 'pages' in self.bib:
                citmodel['pages'] = self.bib['pages'].replace('--', '-')
            citmodel['DOI'] = self.bib['doi']
        
        elif self.bib['ENTRYTYPE'] == 'unpublished':
            citmodel['document-type'] = 'unspecified'
            citmodel['title'] = self.bib['title']
            citmodel['author'] = self.parse_authors(self.bib['author'])
            citmodel['publication-date'] = DM()
            citmodel['publication-date']['year'] = self.bib['year']
        
        citmodel['bibtex'] = self.build_bibtex()
        
        model = DM([('citation', citmodel)])

        self._set_model(model)
        return model
    
    def build_bibtex(self):
        """str : bibtex of citation"""
        bib_database = BibDatabase()
        bib_database.entries = [self.bib]
        return bibtexparser.dumps(bib_database)

    def metadata(self):
        """Returns a flat dict representation of the object"""
        meta = {}
        meta['name'] = self.name
        meta['year_authors'] = self.year_authors
        meta.update(self.bib)
        return meta

    @staticmethod
    def pandasfilter(dataframe, name=None, year=None, volume=None,
                     title=None, journal=None, doi=None, author=None,
                     abstract=None):

        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.int_match.pandas(dataframe, 'year', year)
            &query.str_match.pandas(dataframe, 'volume', volume)
            &query.str_contains.pandas(dataframe, 'title', title)
            &query.str_match.pandas(dataframe, 'journal', journal)
            &query.str_match.pandas(dataframe, 'doi', doi)
            &query.str_contains.pandas(dataframe, 'author', author)
            &query.str_contains.pandas(dataframe, 'abstract', abstract)
        )
        return matches

    @staticmethod
    def mongoquery(name=None, year=None, volume=None,
                   title=None, journal=None, doi=None, author=None,
                   abstract=None):
        mquery = {}
        query.str_match.mongo(mquery, f'name', name)

        root = f'content.{modelroot}'
        query.int_match.mongo(mquery, f'{root}.publication-date.year', year)
        query.str_match.mongo(mquery, f'{root}.volume', volume)
        query.str_contains.mongo(mquery, f'{root}.title', title)
        query.str_match.mongo(mquery, f'{root}.publication-name', journal)
        query.str_match.mongo(mquery, f'{root}.DOI', doi)
        query.str_contains.mongo(mquery, f'{root}.author.surname', author)
        query.str_contains.mongo(mquery, f'{root}.abstract', abstract)
        
        return mquery

    @staticmethod
    def cdcsquery(year=None, volume=None,
                  title=None, journal=None, doi=None, author=None,
                  abstract=None):
        mquery = {}
        root = modelroot
        query.int_match.mongo(mquery, f'{root}.publication-date.year', year)
        query.str_match.mongo(mquery, f'{root}.volume', volume)
        query.str_contains.mongo(mquery, f'{root}.title', title)
        query.str_match.mongo(mquery, f'{root}.publication-name', journal)
        query.str_match.mongo(mquery, f'{root}.DOI', doi)
        query.str_contains.mongo(mquery, f'{root}.author.surname', author)
        query.str_contains.mongo(mquery, f'{root}.abstract', abstract)
        
        return mquery

    @property
    def year_authors(self):
        """
        str: Partial id for potentials that uses YEAR--LAST-F-M with up to 4 authors.
        """
        partialid = str(self.bib['year']) + '-'
        authors = self.parse_authors(self.bib['author'])
        if len(authors) <= 4:
            for author in authors:
                partialid += '-' + author['surname']
                partialid += '-' + author['given-name'].replace('-', '').replace('.', '-').strip('-')
        else:
            for author in authors[:3]:
                partialid += '-' + author['surname']
                partialid += '-' + author['given-name'].replace('-', '').replace('.', '-').strip('-')
            partialid += '-et-al'

        return unidecode(partialid.replace("'", '').replace(" ", '-'))

    @property
    def year_first_author(self):
        """
        str: Partial id for implementations that uses YEAR--LAST-F-M with only the first author.
        """
        partialid = str(self.bib['year']) + '-'
        author = self.parse_authors(self.bib['author'])[0]
        partialid += '-' + author['surname']
        partialid += '-' + author['given-name'].replace('-', '').replace('.', '-').strip('-')
        
        return unidecode(partialid.replace("'", '').replace(" ", '-'))
    
    def parse_authors(self, authors):
        """
        Parse bibtex authors field.

        Parameters
        ----------
        authors : str
            bibtex-formatted author field.

        Returns
        -------
        DataModelDict
            Data model of the parsed and separated names
        """
        author_dicts = []
        
        # remove ands from bib
        splAuth = authors.split(' and ') 
        
        author = ' , '.join(splAuth)
        list_authors = author.split(' , ') #used for given/surname splitting 
        for k in range(len(list_authors)):
            author_dict = DM()
            
            # if . is in initials, find the most right and strip given name and surname
            if '.' in list_authors[k]:  
                l = list_authors[k].rindex(".")
                author_dict['given-name'] = list_authors[k][:l+1].strip()
                author_dict['surname'] = list_authors[k][l+1:].strip()
            
            # otherwise just split by the most right space
            else: 
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
