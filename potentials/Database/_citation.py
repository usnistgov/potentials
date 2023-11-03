# coding: utf-8
# Standard libraries
from pathlib import Path
from typing import Optional, Tuple, Union

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/sckott/habanero
from habanero import cn

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

# Local imports
from .. import load_record

def get_citations(self, 
                  name: Union[str, list, None] = None,
                  year: Union[int, list, None] = None,
                  volume: Union[int, list, None] = None,
                  title: Union[str, list, None] = None,
                  journal: Union[str, list, None] = None,
                  doi: Union[str, list, None] = None,
                  author: Union[str, list, None] = None,
                  abstract: Union[str, list, None] = None,
                  local: Optional[bool] = None,
                  remote: Optional[bool] = None,
                  refresh_cache: bool = False,
                  return_df: bool = False,
                  verbose: bool = False
                  ) -> Union[np.ndarray, Tuple[np.ndarray, pd.DataFrame]]:
    """
    Gets all matching citations from the database.

    Parameters 
    ----------
    name : str or list, optional
        The name(s) of records to limit the search by.
    year : int or list, optional
        Publication year(s) to limit the search by.
    volume : int or list, optional
        Journal volume(s) to limit the search by.
    title : str or list, optional
        Word(s) to search for in the article titles.
    journal : str or list, optional
        Journal name(s) to limit the search by.
    doi : str or list, optional
        Article DOI(s) to limit the search by. 
    author : str or list, optional
        Author name(s) to search for.  Works best for last names only.
    abstract : str or list, optional
        Word(s) to search for in the article abstracts.
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    refresh_cache : bool, optional
        If the local database is of style "local", indicates if the metadata
        cache file is to be refreshed.  If False,
        metadata for new records will be added but the old record metadata
        fields will not be updated.  If True, then the metadata for all
        records will be regenerated, which is needed to update the metadata
        for modified records.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    
    Returns
    -------
    numpy.NDArray of Record subclasses
        The retrived records.
    pandas.DataFrame
        A table of the records' metadata.  Returned if return_df = True.
    """
    return self.get_records(
        style='Citation', name=name, local=local, remote=remote, 
        refresh_cache=refresh_cache, return_df=return_df, verbose=verbose,
        year=year, volume=volume, title=title, journal=journal, doi=doi,
        author=author, abstract=abstract)

def get_citation(self, 
                name: Union[str, list, None] = None,
                  year: Union[int, list, None] = None,
                  volume: Union[int, list, None] = None,
                  title: Union[str, list, None] = None,
                  journal: Union[str, list, None] = None,
                  doi: Union[str, list, None] = None,
                  author: Union[str, list, None] = None,
                  abstract: Union[str, list, None] = None,
                  local: Optional[bool] = None,
                  remote: Optional[bool] = None, 
                  prompt: bool = True,
                  refresh_cache: bool = False,
                  verbose: bool = False) -> Record:
    """
    Gets exactly one matching citation from the database.

    Parameters 
    ----------
    name : str or list, optional
        The name(s) of records to limit the search by.
    year : int or list, optional
        Publication year(s) to limit the search by.
    volume : int or list, optional
        Journal volume(s) to limit the search by.
    title : str or list, optional
        Word(s) to search for in the article titles.
    journal : str or list, optional
        Journal name(s) to limit the search by.
    doi : str or list, optional
        Article DOI(s) to limit the search by. 
    author : str or list, optional
        Author name(s) to search for.  Works best for last names only.
    abstract : str or list, optional
        Word(s) to search for in the article abstracts.
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    prompt : bool, optional
        If prompt=True (default) then a screen input will ask for a selection
        if multiple matching potentials are found.  If prompt=False, then an
        error will be thrown if multiple matches are found.
    refresh_cache : bool, optional
        If the local database is of style "local", indicates if the metadata
        cache file is to be refreshed.  If False,
        metadata for new records will be added but the old record metadata
        fields will not be updated.  If True, then the metadata for all
        records will be regenerated, which is needed to update the metadata
        for modified records.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.

    Raises
    ------
    ValueError
        If no or multiple matching records are found.
    """
    def promptfxn(df):
        """Generates a prompt list for citations."""

        js = df.sort_values('year_authors').index
        for i, j in enumerate(js):
            print(i+1, df.loc[j, 'year_authors'], )
        i = int(input('Please select one:')) - 1

        if i < 0 or i >= len(js):
            raise ValueError('Invalid selection')

        return js[i]

    return self.get_record(
        style='Citation', name=name, local=local, remote=remote, prompt=prompt,
        promptfxn=promptfxn, refresh_cache=refresh_cache, verbose=verbose,
        year=year, volume=volume, title=title, journal=journal, doi=doi,
        author=author, abstract=abstract)

def retrieve_citation(self,
                      name: Union[str, list, None] = None,
                      dest: Optional[Path] = None,
                      year: Union[int, list, None] = None,
                      volume: Union[int, list, None] = None,
                      title: Union[str, list, None] = None,
                      journal: Union[str, list, None] = None,
                      doi: Union[str, list, None] = None,
                      author: Union[str, list, None] = None,
                      abstract: Union[str, list, None] = None,
                      local: Optional[bool] = None,
                      remote: Optional[bool] = None, 
                      prompt: bool = True,
                      format: str = 'json',
                      indent: int = 4, 
                      refresh_cache: bool = False,
                      verbose: bool = False):
    """
    Gets a single matching citation from the database and saves it to a
    file based on the record's name.

    Parameters 
    ----------
    name : str or list, optional
        The name(s) of records to limit the search by.
    dest : path, optional
        The parent directory where the record will be saved to.  If not given,
        will use the current working directory.
    year : int or list, optional
        Publication year(s) to limit the search by.
    volume : int or list, optional
        Journal volume(s) to limit the search by.
    title : str or list, optional
        Word(s) to search for in the article titles.
    journal : str or list, optional
        Journal name(s) to limit the search by.
    doi : str or list, optional
        Article DOI(s) to limit the search by. 
    author : str or list, optional
        Author name(s) to search for.  Works best for last names only.
    abstract : str or list, optional
        Word(s) to search for in the article abstracts.
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    prompt : bool, optional
        If prompt=True (default) then a screen input will ask for a selection
        if multiple matching potentials are found.  If prompt=False, then an
        error will be thrown if multiple matches are found.
    format : str, optional
        The file format to save the record in: 'json', 'xml' or 'bib'.  Default
        is 'json'.
    indent : int, optional
        The number of space indentation spacings to use in the saved
        record for the different tiered levels.  Default is 4.  Giving None
        will create a compact record.
    refresh_cache : bool, optional
        If the local database is of style "local", indicates if the metadata
        cache file is to be refreshed.  If False,
        metadata for new records will be added but the old record metadata
        fields will not be updated.  If True, then the metadata for all
        records will be regenerated, which is needed to update the metadata
        for modified records.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.

    Raises
    ------
    ValueError
        If no or multiple matching records are found.
    """
    # Set default dest
    if dest is None:
        dest = Path.cwd()

    # Get the record
    record = self.get_citation(
        name=name, year=year, volume=volume, title=title, journal=journal,
        doi=doi, author=author, abstract=abstract, local=local, remote=remote,
        prompt=prompt, refresh_cache=refresh_cache, verbose=verbose)

    # Save as json
    if format == 'json':
        fname = Path(dest, f'{record.name}.json')
        with open(fname, 'w', encoding='UTF-8') as f:
            record.model.json(fp=f, indent=indent, ensure_ascii=False)
        if verbose:
            print(f'{fname} saved')
    
    # Save as xml
    elif format == 'xml':
        fname = Path(dest, f'{record.name}.xml')
        with open(fname, 'w', encoding='UTF-8') as f:
            record.model.xml(fp=f, indent=indent)
        if verbose:
            print(f'{fname} saved')

    # Save as bib
    elif format == 'bib':
        fname = Path(dest, f'{record.name}.bib')
        with open(fname, 'w', encoding='UTF-8') as f:
            f.write(record.build_bibtex())
        if verbose:
            print(f'{fname} saved')

    else:
        raise ValueError('Invalid format: must be json, xml or bib.')

def fetch_citation(self,
                   doi: str,
                   local: Optional[str] = None,
                   remote: Optional[str] = None,
                   verbose: bool = False):
    """
    Retrieves a single citation based on its DOI.  First, the database is checked
    for matches with the DOI, then with the record name.  If no matches are found
    in the database, then the corresponding citation is downloaded from CrossRef.

    Parameters
    ----------
    doi : str
        The citation's DOI.  If the citation has no DOI, then the citation's
        record name should be given instead.
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    if local is not False or remote is not False:
        # Try fetching based on doi
        try:
            return self.get_citation(doi=doi, local=local, remote=remote, verbose=verbose)
        except:
            pass

        # Try fetching based on name
        try:
            return self.get_citation(name=doi, local=local, remote=remote, verbose=True)
        except:
            pass
    
    # Fetch from CrossRef if database search failed/skipped
    bibtex = cn.content_negotiation(ids=doi, format="bibtex")
    if verbose:
        print('Citation retrieved from CrossRef')

    return load_record('Citation', bibtex)

def download_citations(self,
                       name: Union[str, list, None] = None,
                       year: Union[int, list, None] = None,
                       volume: Union[int, list, None] = None,
                       title: Union[str, list, None] = None,
                       journal: Union[str, list, None] = None,
                       doi: Union[str, list, None] = None,
                       author: Union[str, list, None] = None,
                       abstract: Union[str, list, None] = None,
                       overwrite: bool = False,
                       return_records: bool = False,
                       verbose: bool = False) -> Optional[np.ndarray]:
    """
    Downloads citations from the remote to the local.

    Parameters 
    ----------
    name : str or list, optional
        The name(s) of records to limit the search by.
    year : int or list, optional
        Publication year(s) to limit the search by.
    volume : int or list, optional
        Journal volume(s) to limit the search by.
    title : str or list, optional
        Word(s) to search for in the article titles.
    journal : str or list, optional
        Journal name(s) to limit the search by.
    doi : str or list, optional
        Article DOI(s) to limit the search by. 
    author : str or list, optional
        Author name(s) to search for.  Works best for last names only.
    abstract : str or list, optional
        Word(s) to search for in the article abstracts.
    overwrite : bool, optional
        Flag indicating if any existing local records with names matching
        remote records are updated (True) or left unchanged (False).  Default
        value is False.
    return_records : bool, optional
        If True, the retrieved record objects are also returned.  Default
        value is False.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """

    return self.download_records(
        style='Citation', name=name, overwrite=overwrite,
        return_records=return_records, verbose=verbose,
        year=year, volume=volume, title=title, journal=journal, doi=doi,
        author=author, abstract=abstract)

def save_citation(self,
                  citation: Record,
                  overwrite: bool = False,
                  verbose: bool = False):
    """
    Saves a citation to the local database.
    
    Parameters
    ----------
    citation : Citation
        The record to save.  
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the local
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.save_record(record=citation, overwrite=overwrite, verbose=verbose)

def upload_citation(self,
                    citation: Record,
                    workspace: Union[str, pd.Series, None] = None,
                    auto_set_pid_off: bool = False,
                    overwrite: bool = False,
                    verbose: bool = False):
    """
    Uploads a citation to the remote database.
    
    Parameters
    ----------
    citation : Citation
        The record to upload.
    workspace : str, optional
        The workspace to assign the record to. If not given, no workspace will
        be assigned (only accessible to user who submitted it).
    auto_set_pid_off : bool, optional
        If True then the CDCS auto_set_pid setting will be turned off during
        the upload and automatically turned back on afterwards.  Use this if
        your records contain PID URL values and you are only uploading one
        entry.  For multiple records with PIDs, manually turn the setting off
        or use the CDCS.auto_set_pid_off() context manager. 
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the remote
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.upload_record(record=citation, workspace=workspace,
                       auto_set_pid_off=auto_set_pid_off,
                       overwrite=overwrite, verbose=verbose)

def delete_citation(self,
                    citation: Record,
                    local: bool = True,
                    remote: bool = False,
                    verbose: bool = False):
    """
    Deletes a citation from the local and/or remote locations.  

    Parameters
    ----------
    citation : Citation
        The record to delete.  If not given, then style and name
        are required.
    local : bool, optional
        Indicates if the record will be deleted from the local location.
        Default value is True.
    remote : bool, optional
        Indicates if the record will be deleted from the remote location.
        Default value is False.  If True, requires an account for the remote
        location with write permissions.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.delete_record(record=citation, local=local, remote=remote,
                       verbose=verbose)