# Standard libraries
import os
import uuid
import string
import datetime

import bibtexparser

from DataModelDict import DataModelDict as DM

def build_record(bib_databases, elements, key=None, othername=None, fictional=False, modelname=None, description_notes=None):
    
    model = DM()
    model['interatomic-potential'] = potential = DM()
    if key is None:
        potential['key'] = str(uuid.uuid4())
    else:
        potential['key'] = key
    potential['id'] = 'later'
    potential['record-version'] = str(datetime.date.today())
    
    potential['description'] = description = DM()
    for bib_database in bib_databases:
        description.append('citation', build_citation(bib_database))
    first_citation = description.aslist('citation')[0]
    potential['id'] = build_potential_id(first_citation.aslist('author'), 
                                         first_citation['publication-date']['year'],
                                         elements,
                                         othername = othername,
                                         fictional = fictional,
                                         modelname = modelname)
    if description_notes is not None:
        description['notes'] = DM()
        description['notes']['text'] = description_notes
    
    potential['implementation'] = None
    
    if fictional is True:
        for element in elements:
            potential.append('fictional-element', element)
    else:
        for element in elements:
            potential.append('element', element)
    if othername is not None:
        potential['other-element'] = str(othername)
    
    return model

def build_citation(bib_database):
    """
    Converts bib_dict into xml description
    """
    bib_dict = bib_database.entries[0]
    citation = DM()
    
    if bib_dict['ENTRYTYPE'] == 'article':
        citation['document-type'] = 'journal' 
        citation['title'] = bib_dict['title']
        citation['author'] = parse_authors(bib_dict['author'])
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
        citation['author'] = parse_authors(bib_dict['author'])
        citation['publication-date'] = DM()
        citation['publication-date']['year'] = bib_dict['year']
    
    citation['bibtex'] = bibtexparser.dumps(bib_database)
    return citation

def parse_authors(authors):
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
        for letter in author_dict['given-name'].replace(' ', '').replace('.', ''):
            if letter in string.ascii_uppercase:
                given += letter +'.'
            elif letter in ['-']:
                given += letter
        author_dict['given-name'] = given
        
        author_dicts.append(author_dict)
        
    return author_dicts

def build_potential_id(authors, year, elements, othername=None, fictional=False, modelname=None):
    potential_id = year + '-'
    
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
    
    if fictional is True:
        potential_id += '-fictional'
    
    if othername is not None:
        potential_id += '-' + str(othername)
    else:
        for element in elements:
            potential_id += '-' + element
    
    if modelname is not None:
        potential_id += '-' + str(modelname)
    
    replace_keys = {"'":'', 'á':'a', 'ä':'a', 'ö':'o', 'ø':'o', ' ':'-', 'č':'c', 'ğ':'g', 'ü':'u', 'é':'e'}
    for k,v in replace_keys.items():
        potential_id = potential_id.replace(k,v)
    
    return potential_id
    
def add_implementation(record, type, key=None, id=None, status='active', date=None, notes=None):
    """
    Adds an implementation to a potential record.
    
    Parameters
    ----------
    record : DataModelDict
        The content of the interatomic-potential record to add the implementation to.
    type : str
        The type/format for the implementation
    key : str, optional
        The unique (uuid) to assign to the implementation. If id is given and key is not, will be assigned a new uuid4.
    id : str, optional
        The implementation will be assigned a unique id starting with the record's id followed by this.  If not given, no key or id will be assigned.
    status : str, optional
        The status for the record.  Default value is 'active'.
    date : datetime.date, optional
        The date to assign to the implementation.  If not given, will use today's date.
    notes : str, optional
        Any notes to give the implementation.
        
    Returns
    -------
    implementation : DataModelDict
        The implementation sub-model that was added to record.
    """    
    implementation = DM()
    if id is not None:
        if key is None:
            implementation['key'] = str(uuid.uuid4())
        else:
            implementation['key'] = key
        implementation['id'] = record['interatomic-potential']['id'] + '--' + id
    implementation['status'] = status
    
    if date is None:
        implementation['date'] = str(datetime.date.today())
    else:
        implementation['date'] = str(date)
    implementation['type'] = type
    if notes is not None:
        implementation['notes'] = DM()
        implementation['notes']['text'] = notes
        
    if record['interatomic-potential']['implementation'] is None:
        record['interatomic-potential']['implementation'] = implementation
    else:
        record['interatomic-potential'].append('implementation', implementation)
    
    return implementation

def add_artifact(implementation, url, label=None):
    """
    Adds an artifact to an implementation.
    
    Parameters
    ----------
    implementation : DataModelDict
        The implementation sub-model of an interatomic-potential record to add the artifact to.
    url : str
        The absolute url path to where the artifact is stored.
    label : str, optional
        Label to assign to the artifact
    """
    artifact = DM()
    artifact['web-link'] = DM()
    artifact['web-link']['URL'] = url
    if label is not None:
        artifact['web-link']['label'] = label
    artifact['web-link']['link-text'] = os.path.basename(url)
    implementation.append('artifact', artifact) 
    
def add_artifacts(implementation, urls, labels=None):
    """
    Adds multiple artifacts to an implementation.
    
    Parameters
    ----------
    implementation : DataModelDict
        The implementation sub-model of an interatomic-potential record to add artifacts to.
    urls : list
        The absolute url paths to where the artifacts are stored.
    labels : list, optional
        String labels to assign to each artifact
    """
    if labels is None:
        labels = [None for i in range(len(urls))]
    assert len(labels) == len(urls), 'Length of urls and labels not the same'
    
    for url, label in zip(urls, labels):
         add_artifact(implementation, url, label)

def add_parameter(implementation, line):
    """
    Adds a parameter line to an implementation.
    
    Parameters
    ----------
    implementation : DataModelDict
        The implementation sub-model of an interatomic-potential record to add a parameter line to.
    line : str
        The parameter line to add.
    """
    parameter = DM()
    parameter['name'] = line
    implementation.append('parameter', parameter)
    
def add_parameters(implementation, lines):  
    """
    Adds multiple parameter lines to an implementation.
    
    Parameters
    ----------
    implementation : DataModelDict
        The implementation sub-model of an interatomic-potential record to add parameter lines to.
    lines : list
        The parameter lines to add.
    """
    for line in lines:
        add_parameter(implementation, line)