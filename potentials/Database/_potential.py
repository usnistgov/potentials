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

def get_potentials(self, id=None, key=None, author=None, year=None, elements=None,
                  localpath=None, verbose=False):
    """
    Get all matching potentials from the database.
    
    Parameters
    ----------
    id : str or list, optional
        Potential ID(s) to search for.  These are unique identifiers derived
        from the publication information and the elemental system being modeled.
    key : str or list, optional
        UUID4 key(s) to search for.  Each entry has a unique random-generated
        UUID4 key.
    author : str or list, optional
        Author string(s) to search for.
    year : int or list, optional
        Publication year(s) to search for.
    elements : str or list, optional
        Element(s) to search for.
    localpath : str, optional
        Path to a local directory to check for records first.  If not given,
        will check localpath value set during object initialization.  If not
        given or set during initialization, then only the remote database will
        be loaded.
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
                              &self.potentials_df.apply(elementmatch, args=[elements], axis=1)]
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
            
        # Add elements query
        if elements is not None:
            elements = aslist(elements)
            mquery['interatomic-potential.element'] = {'$all': elements}

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

def get_potential(self, id=None, author=None, year=None, elements=None,
                  localpath=None, verbose=False):
    """
    Get a single matching potential from the database.
    
    Parameters
    ----------
    id : str or list, optional
        Potential ID(s) to search for.  These are unique identifiers derived
        from the publication information and the elemental system being modeled.
    key : str or list, optional
        UUID4 key(s) to search for.  Each entry has a unique random-generated
        UUID4 key.
    author : str or list, optional
        Author string(s) to search for.
    year : int or list, optional
        Publication year(s) to search for.
    elements : str or list, optional
        Element(s) to search for.
    localpath : str, optional
        Path to a local directory to check for records first.  If not given,
        will check localpath value set during object initialization.  If not
        given or set during initialization, then only the remote database will
        be loaded.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    
    Returns
    -------
    Potential
        The matching potential.

    Raises
    ------
    ValueError
        If no or multiple matching potentials found.
    """
    potentials = self.get_potentials(id=id, author=author, year=year, elements=elements,
                                     localpath=localpath, verbose=verbose)
    if len(potentials) == 1:
        return potentials[0]
    elif len(potentials) == 0:
        raise ValueError('No matching potentials found')
    else:
        raise ValueError('Multiple matching potentials found')

def download_potentials(self, format='xml', localpath=None, indent=None,
                        overwrite=True, verbose=False):
    """
    Download all potentials from the remote to the localpath directory.

    Parameters
    ----------
    format : str, optional
        The file format to save the file as.  Allowed values are 'xml'
        (default) and 'json'.
    localpath : str, optional
        Path to a local directory where the records are to be copied to.
        If not given, will check localpath value set during object
        initialization.
    indent : int, optional
        The indentation spacing size to use for the locally saved file.  If not
        given, the JSON/XML content will be compact.
    overwrite : bool, optional
        If True (default) then any matching potentials already in the localpath
        will be updated if the content has changed.  If False, all existing
        potentials in the localpath will be unchanged.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    reload : bool, optional
        If True, will call load_potentials() after adding the new
        potential.  Default value is False: loading is slow and should only be
        done when you wish to retrieve the saved potentials.
    
    Raises
    ------
    ValueError
        If no localpath, no potentials, invalid format, or records in a
        different format already exist in localpath.    
    """

    # Download all potentials from remote
    records = self.cdcs.query(template='Potential')
    def makepotentials(series):
        return Potential(model=series.xml_content)
    potentials = records.apply(makepotentials, axis=1)
    
    # Save locally
    self.save_potentials(potentials, format=format, localpath=localpath, 
                         indent=indent, overwrite=overwrite, verbose=verbose)

def upload_potential(self, potential, workspace=None, verbose=False):
    """
    Saves a new potential to the remote database.  Requires write
    permissions to potentials.nist.gov

    Parameters
    ----------
    potential : Potential
        The content to save.
    workspace, str, optional
        The workspace to assign the record to. If not given, no workspace will
        be assigned (only accessible to user who submitted it).
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    
    title = 'potential.' + potential.id
    content = potential.asmodel().xml()
    template = 'Potential'

    self.upload_record(template, content, title, workspace=workspace, 
                        verbose=verbose)

def save_potentials(self, potentials, format='xml', localpath=None,
                    indent=None, overwrite=True, verbose=False, reload=False):
    """
    Save Potential records to the localpath.
    
    Parameters
    ----------
    potentials : Potential or list of Potential
        The potential(s) to save. 
    format : str, optional
        The file format to save the record files as.  Allowed values are 
        'xml' (default) and 'json'.
    localpath : path-like object, optional
        Path to a local directory where the files will be saved to.  If not
        given, will use the localpath value set during object initialization.
    indent : int, optional
        The indentation spacing size to use for the locally saved record files.
        If not given, the JSON/XML content will be compact.
    overwrite : bool, optional
        If True (default) then any matching potentials already in the localpath
        will be updated if the content has changed.  If False, all existing
        potentials in the localpath will be unchanged.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    reload : bool, optional
        If True, will call load_potentials() after adding the new
        potential.  Default value is False: loading is slow and should only be
        done when you wish to retrieve the saved potentials.
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

    count_duplicate = 0
    count_updated = 0
    count_new = 0

    potentials = aslist(potentials)

    for potential in potentials:
        
        # Build filename
        potname = potential.id
        fname = Path(save_directory, f'potential.{potname}.{format}')
        
        # Skip existing files if overwrite is False
        if overwrite is False and fname.is_file():
            count_duplicate += 1
            continue

        # Build content
        if format == 'xml':
            content = potential.asmodel().xml(indent=indent)
        elif format == 'json':
            content = potential.asmodel().json(indent=indent)

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
        print(f'{len(potentials)} potentials saved to localpath')
        if count_new > 0:
            print(f' - {count_new} new potentials added')
        if count_updated > 0:
            print(f' - {count_updated} existing potentials updated')
        if count_duplicate > 0:
            print(f' - {count_duplicate} duplicate potentials skipped')

    if reload:
        self.load_potentials(verbose=verbose)

def delete_potential(self, potential, local=True, remote=False, localpath=None,
                     verbose=False):
    """
    Deletes a potential from the remote database.  Requires write
    permissions to potentials.nist.gov

    Parameters
    ----------
    potential : Potential or str
        The potential to delete from the remote database.  Can either give the
        corresponding Potential object or just the potential's id/title.
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
    template = 'Potential'
    if isinstance(potential, Potential):
        title = 'potential.' + potential.id
    elif isinstance(potential, str):
        if 'potential.' in title:
            title = potential
        else:
            title = 'potential.' + potential
    else:
        raise TypeError('Invalid potential value: must be Potential or str')
    
    self.delete_record(template, title, local=local, remote=remote,
                       localpath=localpath, verbose=verbose)
    