# coding: utf-8
# Standard Python libraries
from pathlib import Path

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/sckott/habanero
from habanero import cn

# Local imports
from .. import Citation
from ..tools import aslist

@property
def citations(self):
    """list or None: Loaded Citation objects"""
    return self.__citations

@property
def citations_df(self):
    """pandas.DataFrame or None: Metadata for loaded Citation objects"""
    return self.__citations_df

def _no_load_citations(self):
    """Initializes properties if load_citations is not called"""
    self.__citations = None
    self.__citations_df = None

def load_citations(self, localpath=None, verbose=False):
    """
    Loads citations from the database, first checking localpath, then
    trying to download from host.
    
    Parameters
    ----------
    localpath : str, optional
        Path to a local directory to check for records first.  If not given,
        will check localpath value set during object initialization.  If not
        given or set during initialization, then only the remote database will
        be loaded.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    
    """
    citations = []
    dois = []
    # Set localpath as given here or during init
    if localpath is None:
        localpath = self.localpath
    
    # Check localpath first
    if localpath is not None:
        for citfile in Path(localpath, 'Citation').glob('*'):
            if citfile.suffix in ['.xml', '.json', '.bib']:
                
                with open(citfile, encoding='UTF-8') as f:
                    cit = Citation(f.read())
                citations.append(cit)
                try:
                    dois.append(cit.doi)
                except:
                    dois.append(cit.note) # pylint: disable=no-member
        if verbose:
            print(f'Loaded {len(citations)} local citations')
    
    # Load remote
    try:
        records = self.cdcs.query(template='Citation')
    except:
        if verbose:
            print('Failed to load citations from remote')
    else:
        if verbose:
            print(f'Loaded {len(records)} remote citations')
        for i in range(len(records)):
            record = records.iloc[i]
            cit = Citation(record.xml_content)
            if hasattr(cit, 'doi'):
                if cit.doi not in dois:
                    citations.append(cit)
            else:
                if cit.note not in dois:
                    citations.append(cit)

        if verbose and len(dois) > 0:
            print(f' - {len(citations) - len(dois)} new')
    
    # Build citations and citations_df
    if len(citations) > 0:
        citdicts = []
        for citation in citations:
            citdicts.append(citation.asdict())
        self.__citations = np.array(citations)
        self.__citations_df = pd.DataFrame(citdicts)
    else:
        self.__citations = None
        self.__citations_df = None
        
def get_citation(self, doi, localpath=None, verbose=False):
    
    # Try loaded values first
    if self.citations_df is not None:
        matches = self.citations[(self.citations_df.doi == doi)
                                |(self.citations_df.note == doi)]
        if len(matches) == 1:
            if verbose:
                print('Citation retrieved from loaded citations')
            return matches[0]
        elif len(matches) > 1:
            raise ValueError('Multiple loaded records found for the given doi')
        
    # Try localpath next
    if localpath is None:
        localpath = self.localpath
    if localpath is not None:
        doifname = doi.lower().replace('/', '_')
        for fname in Path(localpath, 'Citation').glob(doifname+'.*'):
            if verbose:
                print(f'Citation retrieved from local file {fname.name}')
            with open(fname, encoding='UTF-8') as f:
                return Citation(f.read())
    
    # Try remote next
    doifname = doi.replace('/', '_')
    try:
        record = self.cdcs.query(template='Citation', title=doifname)
        assert len(record) == 1
    except:
        pass
    else:
        if verbose:
            print(f'Citation retrieved from remote database')
        return Citation(record.iloc[0].xml_content)
    
    # Lastly, download from CrossRef
    bibtex = cn.content_negotiation(ids=doi, format="bibtex")
    if verbose:
        print(f'Citation retrieved from CrossRef')
    return Citation(bibtex)

def download_citations(self, localpath=None, citations=None, format='bib'):
    
    # Handle localpath value
    if localpath is None:
        localpath = self.localpath
    if localpath is None:
        raise ValueError('No local path set to save files to')
    if not Path(localpath, 'Citation').is_dir():
        Path(localpath, 'Citation').mkdir(parents=True)

    # Handle citations value
    if citations is None:
        citations = self.citations
    else:
        citations = aslist(citations)

    # Handle format value
    allowed_formats = ['xml', 'json', 'bib']
    format = format.lower()
    if format not in allowed_formats:
        raise ValueError('Invalid format style: allowed values are "xml", "json" and "bib"')
    for fmt in allowed_formats:
        if fmt == format:
            continue
        count = len(list(Path(localpath, 'Citation').glob(f'*.{fmt}')))
        if count > 0:
            raise ValueError(f'{count} citations already exist in {fmt} format')

    for citation in citations:
        doifname = citation.doifname

        fname = Path(localpath, 'Citation', f'{doifname}.{format}')
        if format == 'bib':
            with open(fname, 'w', encoding='UTF-8') as f:
                f.write(citation.bibtex)
        elif format == 'xml':
            with open(fname, 'w', encoding='UTF-8') as f:
                citation.asmodel().xml(fp=f)
        elif format == 'json':
            with open(fname, 'w', encoding='UTF-8') as f:
                citation.asmodel().json(fp=f)

def save_citation(self, citation, verbose=False):
    title = citation.doifname
    content = citation.asmodel().xml()
    template = 'Citation'
    try:
        self.cdcs.upload_record(content=content, template=template, title=title)
        if verbose:
            print('Citation added to database')
    except:
        self.cdcs.update_record(content=content, template=template, title=title)
        if verbose:
            print('Citation updated in database')