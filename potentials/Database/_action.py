# coding: utf-8
# Standard Python libraries
from pathlib import Path
from typing import Optional, Tuple, Union

# https://numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

# https://pandas.pydata.org/
import pandas as pd

def get_actions(self,
                name: Union[str, list, None] = None,
                date: Union[str, list, None] = None,
                type: Union[str, list, None] = None,
                potential_id: Union[str, list, None] = None,
                potential_key: Union[str, list, None] = None,
                element: Union[str, list, None] = None,
                comment: Union[str, list, None] = None,
                local: Optional[bool] = None,
                remote: Optional[bool] = None,
                refresh_cache: bool = False,
                return_df: bool = False,
                verbose: bool = False
                ) -> Union[np.ndarray, Tuple[np.ndarray, pd.DataFrame]]:
    """
    Gets all matching actions from the database.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    date : str or list
        The date associated with the record.
    type : str or list
        The type of action: 'new posting', 'updated posting', 'retraction',
        or 'site change'.
    potential_id : str or list
        Limits results to entries related to the given potential id.
    potential_key : str or list
        Limits results to entries related to the given potential key.
    element : str or list
        Limits results to entries related to potentials with the given
        element(s).
    comment : str or list
        Term(s) to search for in the action's comment field.
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
        style='Action', name=name, local=local, remote=remote,
        refresh_cache=refresh_cache, return_df=return_df, verbose=verbose,
        date=date, type=type, potential_id=potential_id,
        potential_key=potential_key, element=element, comment=comment)

def get_action(self,
               name: Union[str, list, None] = None,
               date: Union[str, list, None] = None,
               type: Union[str, list, None] = None,
               potential_id: Union[str, list, None] = None,
               potential_key: Union[str, list, None] = None,
               element: Union[str, list, None] = None,
               comment: Union[str, list, None] = None,
               local: Optional[bool] = None,
               remote: Optional[bool] = None, 
               prompt: bool = True,
               refresh_cache: bool = False,
               verbose: bool = False) -> Record:
    """
    Gets exactly one matching action from the database.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    date : str or list
        The date associated with the record.
    type : str or list
        The type of action: 'new posting', 'updated posting', 'retraction',
        or 'site change'.
    potential_id : str or list
        Limits results to entries related to the given potential id.
    potential_key : str or list
        Limits results to entries related to the given potential key.
    element : str or list
        Limits results to entries related to potentials with the given
        element(s).
    comment : str or list
        Term(s) to search for in the action's comment field.
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
    """
    return self.get_record(
        style='Action', name=name, local=local, remote=remote,
        prompt=prompt, refresh_cache=refresh_cache, verbose=verbose,
        date=date, type=type, potential_id=potential_id,
        potential_key=potential_key, element=element, comment=comment)

def retrieve_action(self,
                    name: Union[str, list, None] = None,
                    dest: Optional[Path] = None,
                    date: Union[str, list, None] = None,
                    type: Union[str, list, None] = None,
                    potential_id: Union[str, list, None] = None,
                    potential_key: Union[str, list, None] = None,
                    element: Union[str, list, None] = None,
                    comment: Union[str, list, None] = None,
                    local: Optional[bool] = None,
                    remote: Optional[bool] = None, 
                    prompt: bool = True,
                    format: str = 'json',
                    indent: int = 4, 
                    refresh_cache: bool = False,
                    verbose: bool = False):
    """
    Gets a single matching action from the database and saves it to a
    file based on the record's name.

    Parameters
    ----------
    name : str or list, optional
        The name(s) of records to limit the search by.
    dest : path, optional
        The parent directory where the record will be saved to.  If not given,
        will use the current working directory.
    date : str or list
        The date associated with the record.
    type : str or list
        The type of action: 'new posting', 'updated posting', 'retraction',
        or 'site change'.
    potential_id : str or list
        Limits results to entries related to the given potential id.
    potential_key : str or list
        Limits results to entries related to the given potential key.
    element : str or list
        Limits results to entries related to potentials with the given
        element(s).
    comment : str or list
        Term(s) to search for in the action's comment field.
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
    
    Raises
    ------
    ValueError
        If local or remote is set to True when the corresponding database
        interaction has not been set.
    ValueError
        If multiple or no matching records are discovered.
    """
    self.retrieve_record(
        style='Action', name=name, dest=dest, local=local, remote=remote,
        prompt=prompt, format=format, indent=indent,
        refresh_cache=refresh_cache, verbose=verbose,
        date=date, type=type, potential_id=potential_id,
        potential_key=potential_key, element=element, comment=comment)

def download_actions(self, 
                     name: Union[str, list, None] = None,
                     date: Union[str, list, None] = None,
                     type: Union[str, list, None] = None,
                     potential_id: Union[str, list, None] = None,
                     potential_key: Union[str, list, None] = None,
                     element: Union[str, list, None] = None,
                     comment: Union[str, list, None] = None,
                     overwrite: bool = False,
                     return_records: bool = False,
                     verbose: bool = False) -> Optional[np.ndarray]:
    """
    Downloads actions from the remote to the local.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    date : str or list
        The date associated with the record.
    type : str or list
        The type of action: 'new posting', 'updated posting', 'retraction',
        or 'site change'.
    potential_id : str or list
        Limits results to entries related to the given potential id.
    potential_key : str or list
        Limits results to entries related to the given potential key.
    element : str or list
        Limits results to entries related to potentials with the given
        element(s).
    comment : str or list
        Term(s) to search for in the action's comment field.
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
        style='Action', name=name, overwrite=overwrite,
        return_records=return_records, verbose=verbose,
        date=date, type=type, potential_id=potential_id,
        potential_key=potential_key, element=element, comment=comment)

def save_action(self,
                action: Record,
                overwrite: bool = False,
                verbose: bool = False):
    """
    Saves an action to the local database.
    
    Parameters
    ----------
    action : Action
        The record to save.  
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the local
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.save_record(record=action, overwrite=overwrite, verbose=verbose)

def upload_action(self,
                  action: Record,
                  workspace: Union[str, pd.Series, None] = None,
                  overwrite: bool = False,
                  verbose: bool = False):
    """
    Uploads an action to the remote database.
    
    Parameters
    ----------
    action : Action
        The record to upload.
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
    self.upload_record(record=action, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def delete_action(self,
                  action: Record,
                  local: bool = True,
                  remote: bool = False,
                  verbose: bool = False):
    """
    Deletes an action from the local and/or remote locations.  

    Parameters
    ----------
    action : Action
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
    self.delete_record(record=action, local=local, remote=remote,
                       verbose=verbose)