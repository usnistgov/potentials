# coding: utf-8
# Standard libraries
import string

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://bibtexparser.readthedocs.io/en/master/
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from bibtexparser.bibdatabase import BibDatabase

class Citation():
    """
    Class for representing Citation metadata records.
    """
    def __init__(self, model=None, **kwargs):
        """
        Class initializer
        
        Parameters
        ----------
        model : str or DataModelDict, optional
            Model content or file path to model content.
        """
        if model is not None:
            if len(kwargs) > 0:
                raise TypeError('model cannot be given with any other parameter')
            self.load(model)
        else:
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    @property
    def bibtex(self):
        """Returns string bibtex of citation"""
        bib_database = BibDatabase()
        bib_database.entries = [self.asdict()]
        return bibtexparser.dumps(bib_database)
    
    @property
    def doifname(self):
        """str: file path compatible form of doi"""
        try:
            name = self.doi
        except:
            name = self.note # pylint: disable=no-member
        return name.lower().replace('/', '_')

    def load(self, model):
        """
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        """
        # Check if model is data model
        try:
            model = DM(model)
        except:
            bibtex = model
        else:
            bibtex = model.find('bibtex')
        
        for key in self.asdict():
            delattr(self, key)
            
        # Parse and extract content
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.loads(bibtex, parser=parser)
        assert len(bib_database.entries) == 1, 'bibtex must be for a single reference'
        
        bibdict = bib_database.entries[0]
        for key, value in bibdict.items():
            setattr(self, key, value)
    
    def asmodel(self):
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict: The data model content.
        """
        bibdict = self.asdict()
        model = DM()
        
        def asint(val):
            try:
                return int(val)
            except:
                return val

        if bibdict['ENTRYTYPE'] == 'article':
            model['document-type'] = 'journal' 
            model['title'] = bibdict['title']
            model['author'] = self.parse_authors(bibdict['author'])
            model['publication-name'] = bibdict['journal']
            model['publication-date'] = DM()
            model['publication-date']['year'] = asint(bibdict['year'])
            model['volume'] = asint(bibdict['volume'])
            if 'number' in bibdict:
                model['issue'] = asint(bibdict['number'])
            elif 'issue' in bibdict:
                model['issue'] = asint(bibdict['issue'])
            if 'abstract' in bibdict:
                model['abstract'] = bibdict['abstract']
            if 'pages' in bibdict:
                model['pages'] = bibdict['pages'].replace('--', '-')
            model['DOI'] = bibdict['doi']
        
        elif bibdict['ENTRYTYPE'] == 'unpublished':
            model['document-type'] = 'unspecified'
            model['title'] = bibdict['title']
            model['author'] = self.parse_authors(bibdict['author'])
            model['publication-date'] = DM()
            model['publication-date']['year'] = bibdict['year']
        
        model['bibtex'] = self.bibtex
        
        return DM([('citation', model)])
    
    def asdict(self):
        """Returns a flat dict representation of the object"""

        funcnames = ['asdict', 'asmodel', 'bibtex', 'doifname', 'html', 'load',
                     'parse_authors', 'year_authors']
        bibdict = {}
        for key in dir(self):
            if '__' not in key and key not in funcnames:
                bibdict[key] = str(getattr(self, key))
        return bibdict

    @property
    def year_authors(self):
        """str: YEAR--LAST-F-M string providing a partial id based on citation info"""
        bibdict = self.asdict()
        partialid = str(bibdict['year']) + '-'
        authors = self.parse_authors(bibdict['author'])
        if len(authors) <= 4:
            for author in authors:
                partialid += '-' + author['surname']
                partialid += '-' + author['given-name'].replace('-', '').replace('.', '-').strip('-')
        else:
            for author in authors[:3]:
                partialid += '-' + author['surname']
                partialid += '-' + author['given-name'].replace('-', '').replace('.', '-').strip('-')
            partialid += '-et-al'
        
        replace_keys = {"'":'', 'á':'a', 'ä':'a', 'ö':'o', 'ø':'o', ' ':'-', 'č':'c', 'ğ':'g', 'ü':'u', 'é':'e', 'Ç':'C', 'ı': 'i'}
        for k,v in replace_keys.items():
            partialid = partialid.replace(k,v)

        return partialid

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
    
    def html(self):
        """Returns an HTML representation of the object"""
        bibdict = self.asdict()
        htmlstr = ''

        if 'author' in bibdict:
            author_dicts = self.parse_authors(bibdict['author'])
            numauthors = len(author_dicts)
            for i, author_dict in enumerate(author_dicts):

                # Add formatted names
                givenname = author_dict['given-name']
                surname = author_dict['surname']
                htmlstr += f'{givenname} {surname}'
                
                # Add 'and' and/or comma
                if numauthors >= 3 and i < numauthors - 2:
                    htmlstr += ','
                if numauthors >= 2 and i == numauthors - 2:
                    htmlstr += ' and'
                htmlstr += ' '
        
        if 'year' in bibdict:
            htmlstr += f'({bibdict["year"]}), '

        if 'title' in bibdict:
            htmlstr += f'"{bibdict["title"]}", '

        if 'journal' in bibdict:
            htmlstr += f'<i>{bibdict["journal"]}</i>, '

        if 'volume' in bibdict:
            if 'number' in bibdict:
                number = f'({bibdict["number"]})'
            else:
                number = ''
            
            htmlstr += f'<b>{bibdict["volume"]}{number}</b>, '

        if 'pages' in bibdict:
            htmlstr += f'{bibdict["pages"]} '
        htmlstr = htmlstr.strip() +'. '

        htmlstr += f'DOI: <a href="https://doi.org/{bibdict["doi"]}">{bibdict["doi"]}</a>'

        if 'abstract' in bibdict:
            htmlstr += f'<br/><b>Abstract:</b> {bibdict["abstract"]}'

        return htmlstr