# coding: utf-8
# Standard libraries
import io
import string
from typing import Optional, Tuple, Union

# https://github.com/avian2/unidecode
from unidecode import unidecode

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://bibtexparser.readthedocs.io/en/master/
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bibdatabase import BibDatabase

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_query

class Citation(Record):
    """
    Class for representing Citation metadata records.
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
        self.__bib = {}
        self.bib['note'] = ''

        super().__init__(model=model, name=name, database=database, **kwargs)

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'Citation'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'citation'
    
    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'Citation.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'Citation.xsd')

    @property
    def bib(self) -> dict:
        """dict : Contains the bibtex fields"""
        return self.__bib

    @property
    def doifname(self) -> str:
        """str: file path compatible form of doi"""
        try:
            name = self.bib['doi']
        except KeyError:
            name = self.bib['note']
        return name.lower().replace('/', '_')

    def load_model(self,
                   model: Union[str, io.IOBase, DM],
                   name: Optional[str] = None):
        """
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict
            A JSON/XML data model for the content.
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
        **kwargs : any, ptional
            Any other kwargs are set to the bibdict
        """
        # Set bib values
        for key, value in kwargs.items():
            self.bib[key] = str(value)

        # Set record name
        if name is None:
            self.name = self.doifname
        else:
            self.name = name

    def build_model(self) -> DM:
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
            except (TypeError, ValueError):
                return val

        if self.bib['ENTRYTYPE'] == 'article':
            citmodel['document-type'] = 'journal'
            citmodel['title'] = self.bib['title']
            citmodel['author'] = self.parse_authors(self.bib['author'])
            if 'journal' in self.bib:
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
    
    def build_bibtex(self) -> str:
        """str : bibtex of citation"""
        bib_database = BibDatabase()
        bib_database.entries = [self.bib]
        return bibtexparser.dumps(bib_database)

    def metadata(self) -> dict:
        """Returns a flat dict representation of the object"""
        meta = {}
        meta['name'] = self.name
        meta['year_authors'] = self.year_authors
        meta.update(self.bib)
        return meta

    @property
    def queries(self) -> dict:
        """dict: Query objects and their associated parameter names."""
        return {
            'year': load_query(
                style='int_match',
                name='year', 
                path=f'{self.modelroot}.publication-date.year',
                description="search based on publication year"),
            'volume': load_query(
                style='str_match',
                name='volume',
                path=f'{self.modelroot}.volume',
                description="search based on volume number"),
            'title': load_query(
                style='str_contains',
                name='title',
                path=f'{self.modelroot}.title',
                description="search article titles for contained strings"),
            'journal': load_query(
                style='str_match',
                name='journal',
                path=f'{self.modelroot}..publication-name',
                description="search based on publication journal name"),
            'doi': load_query(
                style='str_match',
                name='doi',
                path=f'{self.modelroot}.DOI',
                description="search based on publication DOI"),
            'author': load_query(
                style='str_contains',
                name='author',
                path=f'{self.modelroot}.author.surname',
                description="search based on publication author"),
            'abstract': load_query(
                style='str_contains',
                name='abstract',
                path=f'{self.modelroot}.abstract',
                description="search article abstract for contained strings"),
        }

    @property
    def year_authors(self) -> str:
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
    def year_first_author(self) -> str:
        """
        str: Partial id for implementations that uses YEAR--LAST-F-M with only the first author.
        """
        partialid = str(self.bib['year']) + '-'
        author = self.parse_authors(self.bib['author'])[0]
        partialid += '-' + author['surname']
        partialid += '-' + author['given-name'].replace('-', '').replace('.', '-').strip('-')
        
        return unidecode(partialid.replace("'", '').replace(" ", '-'))
    
    def parse_authors(self, authors: str) -> DM:
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
