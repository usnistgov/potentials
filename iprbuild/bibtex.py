# Standard libraries
from pathlib import Path

# https://github.com/sckott/habanero
from habanero import cn

# https://bibtexparser.readthedocs.io/en/master/
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

__all__ = ['bibfname', 'fetch_bibtex', 'noref_bibtex', 'save_bibtex']

def bibfname(doi):
    """
    Generates an allowed file name based on a DOI

    Parameters
    ----------
    doi : str
        The DOI to generate a file name for.
    
    Returns
    -------
    str
        The DOI with prohibited characters replaced, and appended with '.bib'.
    """
    
    return doi.replace('/', '_')+'.bib'

def fetch_bibtex(dois, biblibrary):
    """
    Fetches bibtex for published content.  If there is locally saved content,
    it will load it.  Otherwise, will download from CrossRef.

    Parameters
    ----------
    dois : list
        The reference dois to fetch content for.
    biblibrary : str
        Path to the directory containing bibtex files.
    
    Returns
    -------
    list of bibtexparser.bibdatabase.BibDatabase
    """
    
    bib_databases = []
    
    for doi in dois:
        fname = Path(biblibrary, bibfname(doi))
        try:
            # Load bibtex from file
            with open(fname, encoding='UTF-8') as bibtex_file:
                bibtex = bibtex_file.read()
        except:
            # Download using habanero
            bibtex = cn.content_negotiation(ids=doi, format="bibtex")
            with open(fname, 'w', encoding='UTF-8') as bibtex_file:
                bibtex_file.write(bibtex)

        # Parse and extract content
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_databases.append(bibtexparser.loads(bibtex, parser=parser))
    
    return bib_databases

def noref_bibtex(potential_ids, biblibrary):
    """
    Fetches (local copy) or generates bibtex for unpublished content.

    Parameters
    ----------
    potential_ids : list
        Reference-specific potential ids to refer to in place of DOIs.
    biblibrary : str
        Path to the directory containing bibtex files.
    
    Returns
    -------
    list of bibtexparser.bibdatabase.BibDatabase
    """
    
    bib_databases = []
    
    for potential_id in potential_ids:
        fname = Path(biblibrary, bibfname(potential_id))
        try:
            # Load bibtex from file
            with open(fname, encoding='UTF-8') as bibtex_file:
                bibtex = bibtex_file.read()    
        except:
            # Generate new bib_database
            bib_database = bibtexparser.bibdatabase.BibDatabase()
            bib_database.entries = [
                {'ID': potential_id,
                 'note': potential_id,
                 'ENTRYTYPE': 'unpublished'}]
            bib_databases.append(bib_database)
            with open(fname, 'w', encoding='UTF-8') as bibtex_file:
                bibtexparser.dump(bib_database, bibtex_file)
            
        else:
            # Parse and extract content
            parser = BibTexParser()
            parser.customization = convert_to_unicode
            bib_databases.append(bibtexparser.loads(bibtex, parser=parser))

    return bib_databases

def save_bibtex(bib_databases, biblibrary):
    """
    Saves bibtex files to biblibrary for all databases in bib_databases.

    Parameters
    ----------
    bib_databases : list
        bibtexparser.bibdatabase.BibDatabase objects.
    biblibrary : str
        Path to the directory containing bibtex files.
    """
    for bib_database in bib_databases:
        bib_dict = bib_database.entries[0]

        doi = bib_dict.get('doi', bib_dict['ID'])

        with open(Path(biblibrary, bibfname(doi)), 'w', encoding='UTF-8') as bibtex_file:
            bibtexparser.dump(bib_database, bibtex_file)