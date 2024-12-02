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

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_value

class Author(Record):
    """
    Class for describing cited authors
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'author'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'author'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'author.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'author.xsd')

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
        
        self.__givenname = load_value('str', 'givenname', self,
                                modelpath='given-name')
        self.__surname = load_value('longstr', 'surname', self)
        self.__suffix = load_value('str', 'suffix', self)
        
        value_objects.extend([self.__givenname, self.__surname, self.__suffix])

        return value_objects

    @property
    def givenname(self) -> Optional[str]:
        """str or None: initials of first (and middle) names"""
        return self.__givenname.value
    
    @givenname.setter
    def givenname(self, val: Optional[str]):
        self.__givenname.value = val

    @property
    def surname(self) -> Optional[str]:
        """str or None: last (sur)name"""
        return self.__surname.value
    
    @surname.setter
    def surname(self, val: Optional[str]):
        self.__surname.value = val
    
    @property
    def suffix(self) -> Optional[str]:
        """str or None: name suffix"""
        return self.__suffix.value
    
    @suffix.setter
    def suffix(self, val: Optional[str]):
        self.__suffix.value = val


class Citation(Record):
    """
    Class for representing Citation metadata records.
    """

    ########################## Basic metadata fields ##########################

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
        self.__bibdict = None

        value_objects = super()._init_value_objects()
        
        self.__doctype = load_value('str', 'doctype', self,
                                 modelpath='document-type', #valuerequired=True,
                                 allowedvalues=['book', 'journal', 'report', 
                                                'thesis', 'conference proceedings',
                                                'unspecified'])
        self.__title = load_value('longstr', 'title', self)
        self.__authors = load_value('record', 'author', self, recordclass=Author,
                                    modelpath='author')
        self.__publication = load_value('longstr', 'publication', self,
                                        modelpath='publication-name')
        self.__year = load_value('int', 'year', self,
                                 modelpath='publication-date.year')
        self.__month = load_value('month', 'month', self,
                                  modelpath='publication-date.month')
        self.__volume = load_value('str', 'volume', self)
        self.__issue = load_value('str', 'issue', self)
        self.__abstract = load_value('longstr', 'abstract', self)
        self.__pages = load_value('str', 'pages', self)
        self.__doi = load_value('str', 'doi', self,
                                modelpath='DOI')
        self.__url = load_value('str', 'url', self)
        self.__bibtex = load_value('longstr', 'bibtex', self)

        value_objects.extend([self.__doctype, self.__title, self.__authors,
                              self.__publication, self.__year, self.__month,
                              self.__volume, self.__issue, self.__abstract,
                              self.__pages, self.__doi, self.__url, self.__bibtex])

        return value_objects

    @property
    def defaultname(self) -> Optional[str]:
        """str: The name to default to, usually based on other properties"""
        if self.doi is not None:
            # Filename compatible version of the doi
            return self.doi.lower().replace('/', '_')
        else:
            return None

    @property
    def doctype(self) -> str:
        """str: The type of document"""
        return self.__doctype.value

    @doctype.setter
    def doctype(self, val: str):
        self.__doctype.value = val

    @property
    def title(self) -> str:
        """str: The title of the citation"""
        return self.__title.value

    @title.setter
    def title(self, val: str):
        self.__title.value = val

    @property
    def authors(self) -> list:
        """list: The Author component objects associated with author names"""
        return self.__authors.value

    @authors.setter
    def authors(self, val: str):
        self.__authors.value = val

    @property
    def publication(self) -> str:
        """str: The publication/journal name"""
        return self.__publication.value

    @publication.setter
    def publication(self, val: str):
        self.__publication.value = val

    @property
    def year(self) -> int:
        """int: The year of publication/creation"""
        return self.__year.value

    @year.setter
    def year(self, val: int):
        self.__year.value = val

    @property
    def month(self) -> str:
        """str: The month of publication/creation"""
        return self.__month.value

    @month.setter
    def month(self, val: Union[str, int, None]):
        self.__month.value = val

    @property
    def volume(self) -> str:
        """str: The publication volume number"""
        return self.__volume.value

    @volume.setter
    def volume(self, val: str):
        self.__volume.value = val

    @property
    def issue(self) -> str:
        """str: The publication issue number"""
        return self.__issue.value

    @issue.setter
    def issue(self, val: str):
        self.__issue.value = val

    @property
    def abstract(self) -> str:
        """str: The publication's abstract"""
        return self.__abstract.value

    @abstract.setter
    def abstract(self, val: Union[str, int, None]):
        self.__abstract.value = val

    @property
    def pages(self) -> str:
        """str: The publication's page numbers or article number"""
        return self.__pages.value

    @pages.setter
    def pages(self, val: Union[str, int, None]):
        if isinstance(val, str):
            val = val.replace('--', '-')
        self.__pages.value = val

    @property
    def doi(self) -> str:
        """str: The publication's doi"""
        return self.__doi.value

    @doi.setter
    def doi(self, val: Union[str, int, None]):
        self.__doi.value = val

    @property
    def url(self) -> str:
        """str: The publication's url"""
        return self.__url.value

    @url.setter
    def url(self, val: Union[str, int, None]):
        self.__url.value = val

    @property
    def bibtex(self) -> str:
        """str : The bibtex version of the citation"""
        return self.__bibtex.value

    @bibtex.setter
    def bibtex(self, val: str):
        self.__bibtex.value = val

    @property
    def bibdict(self) -> Optional[dict]:
        """dict: dict representation of the bibtex, if parsed"""
        return self.__bibdict

    @property
    def author_string(self) -> str:
        """str: single string """

    def add_author(self,
                   model: Union[str, io.IOBase, DM, None] = None,
                   **kwargs):
        """
        Initializes an Artifact object and adds it to the artifacts list.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Model content or file path to model content.
        filename : str, optional
            The name of the file without path information.
        label : str, optional
            A short description label.
        url : str, optional
            URL for file where downloaded, if available.
        """
        self.__authors.append(model=model, **kwargs)

    @staticmethod
    def doctype_from_entrytype(entrytype):
        converter = {
            'article': 'journal',
            'book': 'book',
            'booklet': 'book',
            'conference': 'conference proceedings',
            'inbook': 'book',
            'incollection': 'book',
            'inproceedings': 'conference proceedings',
            'manual': 'report',
            'mastersthesis': 'thesis',
            'misc': 'unspecified',
            'phdthesis': 'thesis',
            'proceedings': 'conference proceedings',
            'techreport': 'report',
            'unpublished': 'unspecified',
        }
        return converter[entrytype]
    
    @staticmethod
    def entrytype_from_doctype(doctype):
        converter = {
            'book': 'book',
            'journal': 'article',
            'report': 'techreport',
            'thesis': 'phdthesis',
            'conference proceedings': 'inproceedings',
            'unspecified': 'unpublished',
            None: 'misc'
        }
        return converter[doctype]

    def load_bibtex(self,
                    bibtex):
        
        # Define bibtexparser customization operations
        def customizations(record):
            record = bibtexparser.customization.author(record)
            record = bibtexparser.customization.convert_to_unicode(record)
            return record
    
        # Initialize parser and parse
        parser = bibtexparser.bparser.BibTexParser()
        parser.customization = customizations
        bib_database = bibtexparser.loads(bibtex, parser=parser)   
        assert len(bib_database.entries) == 1, 'bibtex must be for a single reference'
        bibdict = bib_database.entries[0]

        # Save values from bibdict to object attributes
        self.bibtex = bibtex
        self.__bibdict = bibdict
        self.doctype = self.doctype_from_entrytype(bibdict['ENTRYTYPE'])
        self.title = bibdict.get('title', None)
        self.publication = bibdict.get('journal', None)
        self.year = bibdict.get('year', None)
        self.month = bibdict.get('month', None)
        self.volume = bibdict.get('volume', None)
        self.issue = bibdict.get('number', None)
        self.pages = bibdict.get('pages', None)
        self.doi = bibdict.get('doi', None)

        # Split and parse author field
        if 'author' in bibdict:
            self.__authors.value = []
            for author in bibdict['author']:
                authordict = bibtexparser.customization.splitname(author)

                # Build given name as initials
                initials = ''
                for name in authordict['first']:
                    for nname in name.split('.'):
                        nname = nname.strip()
                        if nname == '':
                            continue
                        if nname[0] == '-':
                            initials += nname[:2] + '.'
                        else:
                            initials += nname[0] + '.'
                    
                        if '-' in nname[1:]:
                            for nnname in nname.split('-')[1:]:
                                initials += '-' + nnname[0] + '.'

                # Build surname by joining von and last
                sur = ' '.join(authordict['von'] + authordict['last'])
                
                # Check suffix value
                suffix = ' '.join(authordict['jr'])
                if suffix == '':
                    suffix = None
                
                self.add_author(givenname=initials, surname=sur, suffix=suffix)

    def load_model(self,
                   model: str | io.IOBase | DM,
                   name: str | None = None):
        
        super().load_model(model, name)
        self.build_bibtex()
    
    def build_bibtex(self):
        """str : bibtex of citation"""
        
        # Initialize/clear bibdict
        self.__bibdict = {}

        # Set ID
        self.bibdict['ID'] = self.year_authors

        # Set entrytype
        self.bibdict['ENTRYTYPE'] = self.entrytype_from_doctype(self.doctype)

        # Build bibdict fields
        if len(self.authors) > 0:
            authorfields = []
            for author in self.authors:
                if author.suffix is None:
                    authorfields.append(f'{author.surname}, {author.givenname}')
                else:
                    authorfields.append(f'{author.surname}, {author.suffix}, {author.givenname}')
            self.bibdict['author'] = ' and '.join(authorfields)
        if self.title is not None:
            self.bibdict['title'] = self.title
        if self.publication is not None:
            self.bibdict['journal'] = self.publication
        if self.year is not None:
            self.bibdict['year'] = str(self.year)
        if self.volume is not None:
            self.bibdict['volume'] = self.volume
        if self.issue is not None:
            self.bibdict['number'] = self.issue
        if self.pages is not None:
            self.bibdict['pages'] = self.pages
        if self.month is not None:
            self.bibdict['month'] = self.__month.fullname
        if self.doi is not None:
            self.bibdict['doi'] = self.doi
       
        # Convert bibdict to bibtex
        bib_database = bibtexparser.bibdatabase.BibDatabase()
        bib_database.entries = [self.bibdict]
        self.bibtex = bibtexparser.dumps(bib_database)

    def build_model(self):
        self.build_bibtex()
        
        try:
            self.name
        except:
            self.name = self.defaultname

        return super().build_model()

    def metadata(self) -> dict:

        meta = super().metadata()
        meta['year_authors'] = self.year_authors

        return meta

    @property
    def queries(self):
        """dict: Query objects and their associated parameter names."""
        queries = super().queries
        
        # Make author query an alias of surname
        queries.update({
            'author': queries['surname'],
        })

        return queries

    @property
    def year_authors(self) -> str:
        """
        str: Partial id for potentials that uses YEAR--LAST-F-M with up to 4 authors.
        """
        partialid = f'{self.year}-'
        if len(self.authors) <= 4:
            for author in self.authors:
                partialid += f'-{author.surname}'
                partialid += '-' + author.givenname.replace('-', '').replace('.', '-').strip('-')
        else:
            for author in self.authors[:3]:
                partialid += f'-{author.surname}'
                partialid += '-' + author.givenname.replace('-', '').replace('.', '-').strip('-')
            partialid += '-et-al'

        return unidecode(partialid.replace("'", '').replace(" ", '-'))

    @property
    def year_first_author(self) -> str:
        """
        str: Partial id for implementations that uses YEAR--LAST-F-M with only the first author.
        """
        partialid = f'{self.year}-'
        author = self.authors[0]
        partialid += f'-{author.surname}'
        partialid += '-' + author.givenname.replace('-', '').replace('.', '-').strip('-')
        
        return unidecode(partialid.replace("'", '').replace(" ", '-'))