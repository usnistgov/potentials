# coding: utf-8
# Standard Python libraries
from pathlib import Path
import json

from DataModelDict import DataModelDict as DM

import numpy as np
import pandas as pd

from datamodelbase import load_record

from ..tools import aslist

def get_records(self, style=None, name=None,
                local=None, remote=None, verbose=False,
                refresh_cache=False, return_df=False, **kwargs):
    """
    Retrieves all matching records from the local and/or remote locations.  If
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
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
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
    
def get_record(self, style=None, name=None,
               local=None, remote=None,
               prompt=True, promptfxn=None,
               verbose=False, refresh_cache=False, **kwargs):
    """
    Retrieves a single matching record from the local and/or remote locations.
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
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    refresh_cache : bool, optional
        If the local database is of style "local", indicates if the metadata
        cache file is to be refreshed.  If False,
        metadata for new records will be added but the old record metadata
        fields will not be updated.  If True, then the metadata for all
        records will be regenerated, which is needed to update the metadata
        for modified records.
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

def remote_query(self, style=None, keyword=None, query=None, name=None,
                 return_df=False):
    """
    Allows for custom Mongo-style or keyword search queries to be performed on
    records from the remote database.

    Parameters
    ----------
    style : str, optional
        The record style to search. If not given, a prompt will ask for it.
    name : str or list, optional
        The name(s) of records to limit the search by.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned
    query : dict, optional
        A custom-built CDCS Mongo-style query to use for the record search.
        Cannot be given with keyword.
    keyword : str, optional
        Allows for a search of records whose contents contain a keyword.
        Cannot be given with query.
    
    Returns
    -------
    numpy.NDArray of Record subclasses
        The retrived records.
    pandas.DataFrame
        A table of the records' metadata.  Returned if return_df = True.
    """
    return self.remote_database.get_records(style=style, return_df=return_df,
                                            query=query, keyword=keyword, name=name)

def download_records(self, style=None, name=None, overwrite=False,
                     keyword=None, query=None, return_records=False,
                     verbose=False, **kwargs):
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
    query : dict, optional
        A custom-built CDCS-style query to use for the record search.
        Alternative to passing in the record-specific metadata kwargs.
        Note that name can be given with query.
    keyword : str, optional
        Allows for a search of records whose contents contain a keyword.
        Alternative to giving query or kwargs.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    return_records : bool, optional
        If True, the retrieved record objects are also returned.  Default
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

def save_record(self, record=None, style=None, name=None,
                  model=None, overwrite=False, verbose=False):
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
    except ValueError:
        if overwrite:
            self.local_database.update_record(record=record,
                                              verbose=verbose)
        else:
            raise ValueError('Matching record already exists: use overwrite=True to change it')

def upload_record(self, record=None, style=None, name=None,
                  model=None, workspace=None, overwrite=False, verbose=False):
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
    workspace : str, optional
        The workspace to assign the record to. If not given, no workspace will
        be assigned (only accessible to user who submitted it).
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
                                        verbose=verbose) 
    except ValueError:
        if overwrite:
            self.remote_database.update_record(record=record, workspace=workspace,
                                               verbose=verbose)
        else:
            raise ValueError('Matching record already exists: use overwrite=True to change it')

def delete_record(self, record=None, style=None, name=None,
                  local=True, remote=False, verbose=False):
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