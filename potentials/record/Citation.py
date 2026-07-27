# Standard libraries
import io
from typing import Optional, Tuple, Union

# https://github.com/avian2/unidecode
from unidecode import unidecode

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://bibtexparser.readthedocs.io/en/master/
import bibtexparser

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

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

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'givenname', modelpath='given-name')
        self._add_value('longstr', 'surname')
        self._add_value('str', 'suffix')

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

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        # init bibdict
        self.__bibdict = None
        
        self._add_value('str', 'doctype', modelpath='document-type',
                        allowedvalues=('book', 'booklet', 'journal', 'report', 'manual',
                                       'thesis', 'phd thesis', 'masters thesis',
                                       'conference proceedings', 'unspecified',
                                       'unpublished'))

        self._add_value('longstr', 'title')
        
        self._add_value('record', 'authors', recordclass=Author, modelpath='author')
        self._add_value('record', 'editors', recordclass=Author, modelpath='editor')
        editors_queries = self.get_value('editors').queries
        del editors_queries['givenname']
        del editors_queries['surname']
        del editors_queries['suffix']
        
        self._add_value('longstr', 'publication', modelpath='publication-name')
        self._add_value('longstr', 'series')
        self._add_value('longstr', 'chapter')
        self._add_value('longstr', 'edition')
        
        
        self._add_value('int', 'year', modelpath='publication-date.year')
        self._add_value('month', 'month', modelpath='publication-date.month')
        self._add_value('str', 'volume')
        self._add_value('str', 'issue')

        self._add_value('longstr', 'publisher', modelpath='publisher-name')
        self._add_value('longstr', 'address', modelpath='publisher-address')
        self._add_value('longstr', 'organization', modelpath='publisher-organization')

        self._add_value('longstr', 'abstract')

        self._add_value('citepage', 'pages')

        self._add_value('str', 'doi', modelpath='DOI')
        self._add_value('str', 'url')
        self._add_value('longstr', 'bibtex')

    @property
    def defaultname(self) -> Optional[str]:
        """str: The name to default to, usually based on other properties"""
        if self.noname is False and self.doi is not None:
            # Filename compatible version of the doi
            return self.doi.lower().replace('/', '_')
        else:
            return None

    @property
    def bibdict(self) -> Optional[dict]:
        """dict: dict representation of the bibtex, if parsed"""
        return self.__bibdict

    def add_author(self,
                   model: Union[str, io.IOBase, DM, None] = None,
                   **kwargs):
        """
        Initializes an Author object and adds it to the authors list.

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
        self.get_value('authors').append(model=model, **kwargs)

    def add_editor(self,
                   model: Union[str, io.IOBase, DM, None] = None,
                   **kwargs):
        """
        Initializes an Author object and adds it to the editors list.

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
        self.get_value('editors').append(model=model, **kwargs)

    @staticmethod
    def doctype_from_entrytype(entrytype):
        converter = {
            'article': 'journal',
            'book': 'book',
            'booklet': 'booklet',
            'conference': 'conference proceedings',
            'inbook': 'book',
            'incollection': 'book',
            'inproceedings': 'conference proceedings',
            'manual': 'manual',
            'mastersthesis': 'masters thesis',
            'misc': 'unspecified',
            'thesis': 'phd thesis',
            'phdthesis': 'phd thesis',
            'proceedings': 'conference proceedings',
            'techreport': 'report',
            'unpublished': 'unpublished',
        }
        return converter[entrytype]
    

    def entrytype_from_doctype(self):
        converter = {
            'book': 'book',
            'booklet': 'booklet',
            'journal': 'article',
            'report': 'techreport',
            'manual': 'manual',
            'phd thesis': 'phdthesis',
            'masters thesis': 'mastersthesis',
            'conference proceedings': 'inproceedings',
            'unpublished': 'unpublished',
            'unspecified': 'misc',
            None: 'misc'
        }
        entrytype = converter[self.doctype]

        # Switch for the different book types
        if entrytype == 'book':
            if self.publication is not None:
                entrytype = 'incollection'
            elif self.chapter is not None or self.pages is not None:
                entrytype = 'inbook'

        # Switch for the different proceedings types
        elif entrytype == 'inproceedings':
            if len(self.authors) == 0 and self.pages is None:
                entrytype = 'proceedings'

        return entrytype

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
        self.series = bibdict.get('series', None)
        self.organization = bibdict.get('organization', None)
        self.year = bibdict.get('year', None)
        self.month = bibdict.get('month', None)
        self.volume = bibdict.get('volume', None)
        self.issue = bibdict.get('number', None)
        self.pages = bibdict.get('pages', None)
        self.chapter = bibdict.get('chapter', None)
        self.edition = bibdict.get('edition', None)
        self.doi = bibdict.get('doi', None)

        def multifieldmap(bibdict, fields):
            """
            Maps multiple bibtex fields to one parameter. Note first found field
            is returned.
            """
            for field in fields:
                if field in bibdict:
                    return bibdict[field]
            return None
        
        # Set publication value
        self.publication = multifieldmap(bibdict, ['journal', 'booktitle',  'howpublished'])

        # Set publisher value
        self.publisher = multifieldmap(bibdict, ['publisher', 'institution', 'school'])

        # Split and parse author field
        if 'author' in bibdict:
            self.get_value('authors').value = []
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

        # Split and parse editor field
        if 'editor' in bibdict:
            self.get_value('editors').value = []
            for author in bibdict['editor']:
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
                
                self.add_editor(givenname=initials, surname=sur, suffix=suffix)

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
        self.bibdict['ENTRYTYPE'] = entrytype = self.entrytype_from_doctype()

        # Build bibdict fields
        if len(self.authors) > 0:
            authorfields = []
            for author in self.authors:
                if author.suffix is None:
                    authorfields.append(f'{author.surname}, {author.givenname}')
                else:
                    authorfields.append(f'{author.surname}, {author.suffix}, {author.givenname}')
            self.bibdict['author'] = ' and '.join(authorfields)
        
        if len(self.editors) > 0:
            authorfields = []
            for author in self.editors:
                if author.suffix is None:
                    authorfields.append(f'{author.surname}, {author.givenname}')
                else:
                    authorfields.append(f'{author.surname}, {author.suffix}, {author.givenname}')
            self.bibdict['editor'] = ' and '.join(authorfields)
        
        if self.title is not None:
            self.bibdict['title'] = self.title
        
        if self.publication is not None:
            if entrytype == 'article':
                self.bibdict['journal'] = self.publication
            elif entrytype in ['booklet', 'misc']:
                self.bibdict['howpublished'] = self.publication
            else:
                self.bibdict['booktitle'] = self.publication
        
        if self.series is not None:
            self.bibdict['series'] = self.series
        if self.year is not None:
            self.bibdict['year'] = str(self.year)
        if self.volume is not None:
            self.bibdict['volume'] = self.volume
        if self.issue is not None:
            self.bibdict['number'] = self.issue
        if self.pages is not None:
            self.bibdict['pages'] = self.pages
        if self.month is not None:
            self.bibdict['month'] = self.get_value('month').fullname
        if self.chapter is not None:
            self.bibdict['chapter'] = self.chapter
        if self.edition is not None:
            self.bibdict['edition'] = self.edition
        if self.organization is not None:
            self.bibdict['organization'] = self.organization

        if self.publisher is not None:
            if entrytype == 'techreport':
                self.bibdict['institution'] = self.publisher
            elif entrytype in ['phdthesis', 'mastersthesis']:
                self.bibdict['school'] = self.publisher
            else:
                self.bibdict['publisher'] = self.publisher

        if self.address is not None:
            self.bibdict['address'] = self.address
        
        if self.doi is not None:
            self.bibdict['doi'] = self.doi
       
        # Convert bibdict to bibtex
        bib_database = bibtexparser.bibdatabase.BibDatabase()
        bib_database.entries = [self.bibdict]
        self.bibtex = bibtexparser.dumps(bib_database)

    def build_model(self):
        self.build_bibtex()
        
        try:
            assert self.name is not None
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