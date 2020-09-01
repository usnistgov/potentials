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

def load_citations(self, localpath=None, local=None, remote=None, verbose=False):
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
    local : bool, optional
        Indicates if records in localpath are to be loaded.  If not given,
        will use the local value set during initialization.
    remote : bool, optional
        Indicates if the records in the remote database are to be loaded.
        Setting this to be False is useful/faster if a local copy of the
        database exists.  If not given, will use the local value set during
        initialization.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    citations = []
    dois = []
    
    # Set localpath, local, and remote as given here or during init
    if localpath is None:
        localpath = self.localpath
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    # Check localpath first
    if local is True and localpath is not None:
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
    if remote is True:
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
        if verbose:
            print('No citations loaded')
        self.__citations = None
        self.__citations_df = None
        
def get_citations(self, doi, localpath=None, verbose=False):
    raise NotImplementedError('To be done...')

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

def download_citations(self, format='bib', localpath=None, indent=None,
                       overwrite=True, verbose=False):
    """
    Download all citation records from the remote and save to localpath.
    
    Parameters
    ----------
    format : str, optional
        The file format to save the record files as.  Allowed values are 'bib'
        (default), 'xml' and 'json'.
    localpath : path-like object, optional
        Path to a local directory where the files will be saved to.  If not
        given, will use the localpath value set during object initialization.
    indent : int, optional
        The indentation spacing size to use for the locally saved record files.
        If not given, the JSON/XML content will be compact.  Ignored if format
        is 'bib'.
    overwrite : bool, optional
        If True (default) then any matching citations already in the localpath
        will be updated with the new content.  If False, all existing citations
        in the localpath will be skipped.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    # Download all citations from remote
    records = self.cdcs.query(template='Citation')
    def makecitations(series):
        return Citation(model=series.xml_content)
    citations = records.apply(makecitations, axis=1)

    # Save locally
    self.save_citations(citations, format=format, localpath=localpath, 
                        indent=indent, overwrite=overwrite, verbose=verbose)

def upload_citation(self, citation, workspace=None, verbose=False):
    """
    Saves a new citation to the remote database.  Requires write
    permissions to potentials.nist.gov

    Parameters
    ----------
    citation : Citation
        The content to save.
    workspace, str, optional
        The workspace to assign the record to. If not given, no workspace will
        be assigned (only accessible to user who submitted it).
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """

    title = citation.doifname
    content = citation.asmodel().xml()
    template = 'Citation'
    
    self.upload_record(template, content, title, workspace=workspace, 
                        verbose=verbose)

def save_citations(self, citations, format='bib', localpath=None, 
                   indent=None, overwrite=True, verbose=False):
    """
    Save Citation records to the localpath.
    
    Parameters
    ----------
    citations : Citation or list of Citation
        The citation(s) to save. 
    format : str, optional
        The file format to save the record files as.  Allowed values are 'bib'
        (default), 'xml' and 'json'.
    localpath : path-like object, optional
        Path to a local directory where the files will be saved to.  If not
        given, will use the localpath value set during object initialization.
    indent : int, optional
        The indentation spacing size to use for the locally saved record files.
        If not given, the JSON/XML content will be compact.  Ignored if format
        is 'bib'.
    overwrite : bool, optional
        If True (default) then any matching citations already in the localpath
        will be updated with the new content.  If False, all existing citations
        in the localpath will be skipped.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    template = 'Citation'

    # Handle localpath value
    if localpath is None:
        localpath = self.localpath
    if localpath is None:
        raise ValueError('No local path set to save files to')
    
    # Check format value
    format = format.lower()
    allowed_formats = ['bib', 'xml', 'json']
    if format not in allowed_formats:
        raise ValueError("Format must be 'bib', 'xml' or 'json'")

    # Create save directory if needed
    save_directory = Path(localpath, template)
    if not save_directory.is_dir():
        save_directory.mkdir(parents=True)

    for fmt in allowed_formats:
        if fmt != format:
            numexisting = len([fname for fname in save_directory.glob(f'*.{fmt}')])
            if numexisting > 0:
                raise ValueError(f'{numexisting} records of format {fmt} already saved locally')

    count_duplicate = 0
    count_updated = 0
    count_new = 0

    citations = aslist(citations)

    for citation in citations:
        
        # Build filename 
        doifname = citation.doifname
        fname = Path(save_directory, f'{doifname}.{format}')
        
        # Skip existing files if overwrite is False
        if overwrite is False and fname.is_file():
            count_duplicate += 1
            continue

        # Build content
        if format == 'bib':
            content = citation.bibtex
        elif format == 'xml':
            content = citation.asmodel().xml(indent=indent)
        elif format == 'json':
            content = citation.asmodel().json(indent=indent)

        # Check if existing content has changed
        if fname.is_file():
            with open(fname, encoding='UTF-8') as f:
                oldcontent = f.read()
            if content == oldcontent:
                count_duplicate += 1
                continue
            else:
                count_updated += 1
        else:
            count_new += 1

        with open(fname, 'w', encoding='UTF-8') as f:
            f.write(content)
    
    if verbose:
        print(f'{len(citations)} citations saved to localpath')
        if count_new > 0:
            print(f' - {count_new} new citations added')
        if count_updated > 0:
            print(f' - {count_updated} existing citations updated')
        if count_duplicate > 0:
            print(f' - {count_duplicate} duplicate citations skipped')

def delete_citation(self, citation, local=True, remote=False, localpath=None,
                    verbose=False):
    """
    Deletes a citation from the database - local and/or remote.

    Parameters
    ----------
    citation : Citation or str
        The citation to delete from the database.  Can either give the
        corresponding Citation object or just the citation's doi.
    local : bool, optional
        If True (default) then the record will be deleted from the localpath.
    remote : bool, optional
        If True then the record will be deleted from the remote database.  
        Requires write permissions to potentials.nist.gov.  Default value is
        False.
    localpath : path-like object, optional
        Path to a local directory where the file to delete is located.  If not
        given, will use the localpath value set during object initialization.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    template = 'Citation'
    if isinstance(citation, Citation):
        title = citation.doifname
    elif isinstance(citation, str):
        title = citation.lower().replace('/', '_')
    else:
        raise TypeError('Invalid citation value: must be Citation or str')
    
    self.delete_record(template, title, local=local, remote=remote,
                       localpath=localpath, verbose=verbose)
    