# coding: utf-8
# Standard Python libraries
from pathlib import Path

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

from DataModelDict import DataModelDict as DM

# Local imports
from .. import Potential
from ..tools import aslist

@property
def potentials(self):
    """list or None: Loaded Potential objects"""
    return self.__potentials

@property
def potentials_df(self):
    """pandas.DataFrame or None: Metadata for loaded Potential objects"""
    return self.__potentials_df

def _no_load_potentials(self):
    """Initializes properties if load_potentials is not called"""
    self.__potentials = None
    self.__potentials_df = None

def load_potentials(self, localpath=None, local=None, remote=None, verbose=False):
    """
    Loads potentials from the database, first checking localpath, then
    trying to download from host.
    
    Parameters
    ----------
    localpath : str, optional
        Path to a local directory to check for records first.  If not given,
        will check localpath value set during object initialization.  If
        neither, then no local records will be loaded.
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
    potentials = []
    potnames = []

    # Set localpath, local, and remote as given here or during init
    if localpath is None:
        localpath = self.localpath
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    # Check localpath first
    if local is True and localpath is not None:
        for potfile in Path(localpath, 'Potential').glob('*'):
            if potfile.suffix in ['.xml', '.json']:
                potentials.append(Potential(potfile))
                potnames.append(potfile.stem)

        if verbose:
            print(f'Loaded {len(potentials)} local potentials')
    
    # Load remote
    if remote is True:
        try:
            records = self.cdcs.query(template='Potential')
        except:
            if verbose:
                print('Failed to load potentials from remote')
        else:
            if verbose:
                print(f'Loaded {len(records)} remote potentials')
            for i in range(len(records)):
                record = records.iloc[i]
                if record.title not in potnames:
                    potentials.append(Potential(record.xml_content))

            if verbose and len(potnames) > 0:
                print(f' - {len(potentials) - len(potnames)} new')
    
    # Build potentials and potentials_df
    if len(potentials) > 0:
        potdicts = []
        for potential in potentials:
            potdicts.append(potential.asdict())
        self.__potentials_df = pd.DataFrame(potdicts).sort_values('id')
        self.__potentials = np.array(potentials)[self.__potentials_df.index]
        self.__potentials_df.reset_index(drop=True)

    else:
        if verbose:
            print('No potentials loaded')
        self.__potentials = None
        self.__potentials_df = None

def get_potentials(self, id=None, key=None, author=None, year=None, element=None,
                  localpath=None, verbose=False):
    """
    Selects potentials matching the given parameters.  If 
    
    Parameters
    ----------
    id : str or list, optional
    key : str or list, optional
    author : str or list, optional
    year : str or list, optional
    element : str or list, optional
    localpath : str, optional
        
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    
    Returns
    -------
    list of Potential
        The matching potentials
    """
    # Check loaded values if available
    if self.potentials_df is not None:
        
        def idmatch(series, val):
            if val is None:
                return True
            else:
                return series.id in aslist(val)

        def keymatch(series, val):
            if val is None:
                return True
            else:
                return series.key in aslist(val)
        
        def authormatch(series, val):
            if val is None:
                return True
            else:
                val = aslist(val)
                matches = [False for i in range(len(val))]
                for citation in series.citations:
                    for i in range(len(val)):
                        if val[i] in citation.author:
                            matches[i] = True
                if sum(matches) == len(val):
                    return True
                else:
                    return False

        def yearmatch(series, val):
            if val is None:
                return True
            else:
                val = aslist(val)
                for i in range(len(val)):   
                    val[i] = str(val[i])
                for citation in series.citations:
                    if citation.year in aslist(val):
                        return True
                return False
        
        def elementmatch(series, val):
            if val is None:
                return True
            
            elif isinstance(series.elements, list):
                for v in aslist(val):
                    if v not in series.elements:
                        return False
                return True
            else:
                return False
        
        potentials = self.potentials[self.potentials_df.apply(idmatch, args=[id], axis=1)
                              &self.potentials_df.apply(keymatch, args=[key], axis=1)
                              &self.potentials_df.apply(authormatch, args=[author], axis=1)
                              &self.potentials_df.apply(yearmatch, args=[year], axis=1)
                              &self.potentials_df.apply(elementmatch, args=[element], axis=1)]
        if verbose:
            print(len(potentials), 'matching potentials found from loaded records')
        return potentials

    # Check remote values if no loaded values
    else:
        # Build Mongoquery
        mquery = {}

        # Add id query
        if id is not None:
            id = aslist(id)
            mquery['interatomic-potential.id'] = {'$in': id}

        # Add key query
        if key is not None:
            key = aslist(key)
            mquery['interatomic-potential.key'] = {'$in': key}

        # Add author query
        if author is not None:
            author = aslist(author)
            mquery['$and'] = []
            for auth in author:
                mquery['$and'].append({'interatomic-potential.description.citation.author.surname':{'$regex': auth}})
                
        # Add year query
        if year is not None:
            year = aslist(year)
            for i in range(len(year)):
                year[i] = int(year[i])
            mquery['interatomic-potential.description.citation.publication-date.year'] = {'$in': year}
            
        # Add year query
        if element is not None:
            element = aslist(element)
            mquery['interatomic-potential.element'] = {'$all': element}

        matches = self.cdcs.query(template='Potential', mongoquery=mquery)

        if verbose:
            print(len(matches), 'matching potentials found from remote database')

        if len(matches) > 0:
            matches = matches.sort_values('title').reset_index(drop=True)

            def makepotentials(series):
                return Potential(model=series.xml_content)

            return matches.apply(makepotentials, axis=1).values
        else:
            return np.array([])

def get_potential(self, id=None, author=None, year=None, element=None,
                  localpath=None, verbose=False):
    """
    Loads potential from the database, first checking localpath, then
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
    potentials = self.get_potentials(id=id, author=author, year=year, element=element,
                                     localpath=localpath, verbose=verbose)
    if len(potentials) == 1:
        return potentials[0]
    elif len(potentials) == 0:
        raise ValueError('No matching potentials found')
    else:
        raise ValueError('Multiple matching potentials found')

def download_potentials(self, localpath=None, potentials=None, format='xml',
                        indent=None, verbose=False):
    """
    Download all potentials from the remote to the localpath directory.

    Parameters
    ----------
    localpath : str, optional
        Path to a local directory where the records are to be copied to.
        If not given, will check localpath value set during object
        initialization.
    potentials : list of Potential, optional
        A list of potentials to download. If not given, all potentials will
        be downloaded.
    format : str, optional
        The file format to save the file as.  Allowed values are 'xml'
        (default) and 'json'.
    indent : int, optional
        The indentation spacing size to use for the locally saved file.  If not
        given, the JSON/XML content will be compact.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    
    Raises
    ------
    ValueError
        If no localpath, no potentials, invalid format, or records in a
        different format already exist in localpath.    
    """

    template = 'Potential'

    # Check localpath values
    if localpath is None:
        localpath = self.localpath
    if localpath is None:
        raise ValueError('No local path set to save files to')

    # Check format value
    format = format.lower()
    allowed_formats = ['xml', 'json']
    if format not in allowed_formats:
        raise ValueError("Format must be 'xml' or 'json'")
    
    # Create save directory if needed
    save_directory = Path(localpath, template)
    if not save_directory.is_dir():
        save_directory.mkdir(parents=True)

    for fmt in allowed_formats:
        if fmt != format:
            numexisting = len([fname for fname in save_directory.glob(f'*.{fmt}')])
            if numexisting > 0:
                raise ValueError(f'{numexisting} records of format {fmt} already saved locally')

    # Download and save
    if potentials is None:
        records = self.cdcs.query(template=template)
        for i in range(len(records)):
            record = records.iloc[i]
            fname = Path(save_directory, f'{record.title}.{format}')
            content = DM(record.xml_content)
            with open(fname, 'w', encoding='UTF-8') as f:
                if format == 'xml':
                    content.xml(fp=f, indent=indent)
                else:
                    content.json(fp=f, indent=indent)
        if verbose:
            print(f'Downloaded {len(records)} of {template}')
    
    # Save loaded content
    else:
        for potential in aslist(potentials):
            potname = potential.id

            fname = Path(save_directory, f'potential.{potname}.{format}')
            if format == 'xml':
                with open(fname, 'w', encoding='UTF-8') as f:
                    potential.asmodel().xml(fp=f, indent=indent)
            elif format == 'json':
                with open(fname, 'w', encoding='UTF-8') as f:
                    potential.asmodel().json(fp=f, indent=indent)
        
        if verbose:
            print(f'Downloaded {len(potentials)} of {template}')

def upload_potential(self, potential, verbose=False):
    """
    Saves a new potential to the remote database.  Requires write
    permissions to potentials.nist.gov

    Parameters
    ----------
    potential : Potential
        The content to save.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    
    title = 'potential.' + potential.id
    content = potential.asmodel().xml()
    template = 'Potential'
    try:
        try:
            self.cdcs.upload_record(content=content, template=template, title=title)
            if verbose:
                print('Potential added to database')
        except:
            self.cdcs.update_record(content=content, template=template, title=title)
            if verbose:
                print('Potential updated in database')
    except:
        if verbose:
            print('Failed to upload potential to database')