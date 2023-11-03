# coding: utf-8
# Standard Python libraries
import io
from pathlib import Path
from typing import Callable, Optional, Tuple, Union

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_record

def get_records(self,
                style: Optional[str] = None,
                name: Union[str, list, None] = None,
                local: Optional[bool] = None,
                remote: Optional[bool] = None,
                refresh_cache: bool = False,
                return_df: bool = False,
                verbose: bool = False,
                **kwargs
                ) -> Union[np.ndarray, Tuple[np.ndarray, pd.DataFrame]]:
    """
    Gets all matching records from the local and/or remote locations.  If
    records with the same record name are retrieved from both locations, then
    the local versions of those records are given.

    Parameters
    ----------
    style : str, optional
        The record style to search. If not given, a prompt will ask for it.
    name : str or list, optional
        The name(s) of records to limit the search by.
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
    **kwargs : any, optional
        Any extra keyword arguments supported by the record style.

    Returns
    -------
    numpy.NDArray of Record subclasses
        The retrived records.
    pandas.DataFrame
        A table of the records' metadata.  Returned if return_df = True.
    
    Raises
    ------
    ValueError
        If local or remote is set to True when the corresponding database
        interaction has not been set.
    """
    # Handle local and remote
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote

    # Test that the respective databases have been set
    if local and self.local_database is None:
        raise ValueError('local database info not set: initialize with local=True or call set_local_database')
    if remote and self.remote_database is None:
        raise ValueError('remote database info not set: initialize with remote=True or call set_remote_database')
    
    # Get local records
    if local:
        if refresh_cache is True:
            if self.local_database.style != 'local':
                raise ValueError('local database must be of style local to refresh cache')
            else:
                kwargs['refresh_cache'] = refresh_cache
        l_recs, l_df = self.local_database.get_records(style, name=name, return_df=True, **kwargs)
        if len(l_recs) == 0:
            l_df = pd.DataFrame({'name':[]})
        if verbose:
            print(f'Found {len(l_recs)} matching {style} records in local library')
    else:
        l_recs = np.array([])
        l_df = pd.DataFrame({'name':[]})
    
    # Get remote records
    if remote:
        try:
            r_recs, r_df = self.remote_database.get_records(style, name=name,
                                                            return_df=True, **kwargs)
        except Exception as e:
            r_recs = np.array([])
            r_df = pd.DataFrame({'name':[]})
            if verbose:
                print(f'Remote access failed: {e}')
        if verbose:
            print(f'Found {len(r_recs)} matching {style} records in remote library')
    else:
        r_recs = np.array([])
        r_df = pd.DataFrame({'name':[]})

    # Combine results
    if len(r_recs) == 0:
        records = l_recs
        df = l_df
    elif len(l_recs) == 0:
        records = r_recs
        df = r_df
    else:
        # Identify missing remotes
        newr_df = r_df[~r_df.name.isin(l_df.name)]
        newr_recs = r_recs[newr_df.index.tolist()]
        if verbose:
            print(f' - {len(newr_recs)} remote records are new')
        
        # Combine local and new remote
        records = np.hstack([l_recs, newr_recs])
        df = pd.concat([l_df, newr_df], ignore_index=True, sort=False)

    # Sort by name
    df = df.sort_values('name')
    records = records[df.index.tolist()]

    # Return records (and df)
    if return_df:
        return records, df.reset_index(drop=True)
    else:
        return records
    
def get_record(self, 
               style: Optional[str] = None,
               name: Union[str, list, None] = None,
               local: Optional[bool] = None,
               remote: Optional[bool] = None, 
               prompt: bool = True,
               promptfxn: Optional[Callable] = None,
               refresh_cache: bool = False,
               verbose: bool = False,
               **kwargs) -> Record:
    """
    Gets a single matching record from the local and/or remote locations.
    If local is True and the record is found there, then the local copy of the
    record is returned without searching the remote.

    Parameters
    ----------
    style : str, optional
        The record style to search. If not given, a prompt will ask for it.
    name : str or list, optional
        The name(s) of records to limit the search by.
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
    promptfxn : function, optional
        A function that generates the prompt selection list.  If not given,
        the prompt will be a list of "id" values. 
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
    **kwargs : any, optional
        Any extra keyword arguments supported by the record style.

    Returns
    -------
    Record subclass
        The retrived record.
    
    Raises
    ------
    ValueError
        If local or remote is set to True when the corresponding database
        interaction has not been set.
    ValueError
        If multiple or no matching records are discovered.
    """
    # Handle local and remote
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote

    # Define default promptfxn if needed
    if promptfxn is None:
        def promptfxn(df):
            """Generates a prompt list based on id or name fields."""
            if 'id' in df:
                key = 'id'
            else:
                key = 'name'

            js = df.sort_values(key).index
            for i, j in enumerate(js):
                print(i+1, df.loc[j, key])
            i = int(input('Please select one:')) - 1

            if i < 0 or i >= len(js):
                raise ValueError('Invalid selection')

            return js[i]
    
    # Check local first
    if local:
        if refresh_cache is True:
            if self.local_database.style != 'local':
                raise ValueError('local database must be of style local to refresh cache')
            else:
                kwargs['refresh_cache'] = refresh_cache
        records, df = self.get_records(style, local=True, remote=False,
                                       name=name, return_df=True, **kwargs)
        if len(records) == 1:
            if verbose:
                print('Matching record retrieved from local')
            return records[0]

        elif len(records) > 1:
            if prompt:
                print('Multiple matching record retrieved from local')
                index = promptfxn(df)
                return records[index]
            else:
                raise ValueError('Multiple matching records found')
    
    # Get remote records
    if remote:
        records, df = self.get_records(style, local=False, remote=True,
                                       name=name, return_df=True, **kwargs)
        if len(records) == 1:
            if verbose:
                print('Matching record retrieved from remote')
            return records[0]

        elif len(records) > 1:
            if prompt:
                print('Multiple matching record retrieved from remote')
                index = promptfxn(df)
                return records[index]
            else:
                raise ValueError('Multiple matching records found')
    
    raise ValueError('No matching records found')

def retrieve_record(self, 
                    style: Optional[str] = None,
                    name: Union[str, list, None] = None,
                    dest: Optional[Path] = None,
                    local: Optional[bool] = None,
                    remote: Optional[bool] = None, 
                    prompt: bool = True,
                    promptfxn: Optional[Callable] = None,
                    format: str = 'json',
                    indent: int = 4, 
                    refresh_cache: bool = False,
                    verbose: bool = False,
                    **kwargs):
    """
    Gets a single matching record from the database and saves it to a
    file based on the record's name.

    Parameters
    ----------
    style : str, optional
        The record style to search. If not given, a prompt will ask for it.
    name : str or list, optional
        The name(s) of records to limit the search by.
    dest : path, optional
        The parent directory where the record will be saved to.  If not given,
        will use the current working directory.
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
    promptfxn : function, optional
        A function that generates the prompt selection list.  If not given,
        the prompt will be a list of "id" values.
    format : str, optional
        The file format to save the record in: 'json' or 'xml'.  Default
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
    **kwargs : any, optional
        Any extra keyword arguments supported by the record style.

    
    Raises
    ------
    ValueError
        If local or remote is set to True when the corresponding database
        interaction has not been set.
    ValueError
        If multiple or no matching records are discovered.
    """
    # Set default dest
    if dest is None:
        dest = Path.cwd()

    # Get the record
    record = self.get_record(
        style=style, name=name, local=local, remote=remote, prompt=prompt,
        promptfxn=promptfxn, verbose=verbose, refresh_cache=refresh_cache,
        **kwargs)

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

    else:
        raise ValueError('Invalid format: must be json or xml.')

def remote_query(self,
                 style: Optional[str] = None,
                 keyword: Optional[str] = None,
                 query: Optional[dict] = None,
                 name: Union[str, list, None] = None,
                 return_df: bool = False
                 )-> Union[np.ndarray, Tuple[np.ndarray, pd.DataFrame]]:
    """
    Allows for custom Mongo-style or keyword search queries to be performed on
    records from the remote database.

    Parameters
    ----------
    style : str, optional
        The record style to search. If not given, a prompt will ask for it.
    keyword : str, optional
        Allows for a search of records whose contents contain a keyword.
        Cannot be given with query.
    query : dict, optional
        A custom-built CDCS Mongo-style query to use for the record search.
        Cannot be given with keyword.
    name : str or list, optional
        The name(s) of records to limit the search by.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned
    
    Returns
    -------
    numpy.NDArray of Record subclasses
        The retrived records.
    pandas.DataFrame
        A table of the records' metadata.  Returned if return_df = True.
    """
    return self.remote_database.get_records(style=style, return_df=return_df,
                                            query=query, keyword=keyword, name=name)

def download_records(self,
                     style: Optional[str] = None,
                     name: Union[str, list, None] = None,
                     overwrite: bool = False,
                     return_records: bool = False,
                     verbose: bool = False,
                     **kwargs) -> Optional[np.ndarray]:
    """
    Retrieves all matching records from the remote location and saves them to
    the local location.

    Parameters
    ----------
    style : str, optional
        The record style to search. If not given, a prompt will ask for it.
    name : str or list, optional
        The name(s) of records to limit the search by.
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
    **kwargs : any, optional
        Any extra keyword arguments supported by the record style.

    Returns
    -------
    numpy.NDArray of Record subclasses
        The retrived records.  Only returned if return_records=True.
    
    Raises
    ------
    ValueError
        If local or remote is set to True when the corresponding database
        interaction has not been set.
    """
    # Test that the respective databases have been set
    if self.local_database is None:
        raise ValueError('local database info not set: initialize with local=True or call set_local_database')
    if self.remote_database is None:
        raise ValueError('remote database info not set: initialize with remote=True or call set_remote_database')
    
    # Get matching remote records
    records = self.remote_database.get_records(style, name=name, **kwargs)
    if verbose:
        print(f'Found {len(records)} matching {style} records in remote library')
    
    num_added = 0
    num_changed = 0
    num_skipped = 0
    for record in records:
        try:
            self.local_database.add_record(record=record)
            num_added += 1
        except:
            if overwrite:
                self.local_database.update_record(record=record)
                num_changed += 1
            else:
                num_skipped += 1
    
    if verbose:
        print(num_added, 'new records added to local')
        if num_changed > 0:
            print(num_changed, 'existing records changed in local')
        if num_skipped > 0:
            print(num_skipped, 'existing records skipped')
    
    if return_records is True:
        return records

def save_record(self,
                record: Optional[Record] = None,
                style: Optional[str] = None,
                name: Optional[str] = None,
                model: Union[str, io.IOBase, DM, None] = None,
                overwrite: bool = False,
                verbose: bool = False):
    """
    Saves a record to the local database.
    
    Parameters
    ----------
    record : Record, optional
        The record to save.  If not given, then style and model are
        required.
    style : str, optional
        The record style to save.  Required if record is not given.
    model : str, DataModelDict, or file-like object, optional
        The contents of the record to save.  Required if record is not given.
    name : str, optional
        The name to assign to the record.  Required if record is not given and
        model is not a file name.
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the remote
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    if record is None:
        record = load_record(style, model, name=name)
    
    try:
        self.local_database.add_record(record=record, verbose=verbose)
    except ValueError as e:
        if overwrite:
            self.local_database.update_record(record=record,
                                              verbose=verbose)
        else:
            raise ValueError('Matching record already exists: use overwrite=True to change it') from e

def upload_record(self,
                  record: Optional[Record] = None,
                  style: Optional[str] = None,
                  name: Optional[str] = None,
                  model: Union[str, io.IOBase, DM, None] = None,
                  workspace: Union[str, pd.Series, None] = None,
                  auto_set_pid_off: bool = False,
                  overwrite: bool = False,
                  verbose: bool = False):
    """
    Uploads a record to the remote database.  Requires an account for the remote
    location with write permissions.

    Parameters
    ----------
    record : Record, optional
        The record to upload.  If not given, then style and model are
        required.
    style : str, optional
        The record style to upload.  Required if record is not given.
    model : str, DataModelDict, or file-like object, optional
        The contents of the record to upload.  Required if record is not given.
    name : str, optional
        The name to assign to the record.  Required if record is not given and
        model is not a file name.
    workspace : str or pandas.Series, optional
        The CDCS workspace or workspace name to assign the record to. If not
        given, no workspace will be assigned (only accessible to user who
        submitted it).
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
    if record is None:
        record = load_record(style, model, name=name)
    
    try:
        self.remote_database.add_record(record=record, workspace=workspace,
                                        auto_set_pid_off=auto_set_pid_off,
                                        verbose=verbose) 
    except ValueError as e:
        if overwrite:
            self.remote_database.update_record(record=record, workspace=workspace,
                                               auto_set_pid_off=auto_set_pid_off,
                                               verbose=verbose)
        else:
            raise ValueError('Matching record already exists: use overwrite=True to change it') from e

def delete_record(self,
                  record: Optional[Record] = None,
                  style: Optional[str] = None,
                  name: Optional[str] = None,
                  local: bool = True,
                  remote: bool = False,
                  verbose: bool = False):
    """
    Deletes a record from the local and/or remote locations.  

    Parameters
    ----------
    record : Record, optional
        The record to delete.  If not given, then style and name
        are required.
    style : str, optional
        The style of the record to delete.  Required if record is not given.
    name : str, optional
        The name of the record to delete.  Required if record is not given.
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
    if not local and not remote:
        print('local and remote both False: no records deleted')
        return None
    
    if local:
        self.local_database.delete_record(record=record, name=name, style=style,
                                          verbose=verbose)
    if remote:
        self.remote_database.delete_record(record=record, name=name, style=style,
                                           verbose=verbose)
