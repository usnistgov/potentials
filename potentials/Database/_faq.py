# coding: utf-8
# Standard libraries
from pathlib import Path
from typing import Optional, Tuple, Union

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

def get_faqs(self, 
             name: Union[str, list, None] = None,
             question: Union[str, list, None] = None,
             answer: Union[str, list, None] = None,
             local: Optional[bool] = None,
             remote: Optional[bool] = None,
             refresh_cache: bool = False,
             return_df: bool = False,
             verbose: bool = False
             ) -> Union[np.ndarray, Tuple[np.ndarray, pd.DataFrame]]:
    """
    Gets all matching FAQs from the database.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    question : str or list
        Term(s) to search for in the question field.
    answer : str or list
        Term(s) to search for in the answer field.
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
        style='FAQ', name=name, local=local, remote=remote,
        refresh_cache=refresh_cache, return_df=return_df, verbose=verbose,
        question=question, answer=answer)

def get_faq(self, 
            name: Union[str, list, None] = None,
            question: Union[str, list, None] = None,
            answer: Union[str, list, None] = None,
            local: Optional[bool] = None,
            remote: Optional[bool] = None, 
            prompt: bool = True,
            refresh_cache: bool = False,
            verbose: bool = False) -> Record:
    """
    Gets exactly one matching FAQ from the database.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    question : str or list
        Term(s) to search for in the question field.
    answer : str or list
        Term(s) to search for in the answer field.
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
        style='FAQ', name=name, local=local, remote=remote,
        prompt=prompt, refresh_cache=refresh_cache, verbose=verbose,
        question=question, answer=answer)

def retrieve_faq(self, 
                name: Union[str, list, None] = None,
                dest: Optional[Path] = None,
                question: Union[str, list, None] = None,
                answer: Union[str, list, None] = None,
                local: Optional[bool] = None,
                remote: Optional[bool] = None, 
                prompt: bool = True,
                format: str = 'json',
                indent: int = 4, 
                refresh_cache: bool = False,
                verbose: bool = False):
    """
    Gets a single matching FAQ from the database and saves it to a
    file based on the record's name.

    Parameters
    ----------
    name : str or list, optional
        The name(s) of records to limit the search by.
    dest : path, optional
        The parent directory where the record will be saved to.  If not given,
        will use the current working directory.
    question : str or list
        Term(s) to search for in the question field.
    answer : str or list
        Term(s) to search for in the answer field.
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
        style='FAQ', name=name, dest=dest, local=local, remote=remote,
        prompt=prompt, format=format, indent=indent,
        refresh_cache=refresh_cache, verbose=verbose,
        question=question, answer=answer)

def download_faqs(self, 
                  name: Union[str, list, None] = None,
                  question: Union[str, list, None] = None,
                  answer: Union[str, list, None] = None,
                  overwrite: bool = False,
                  return_records: bool = False,
                  verbose: bool = False) -> Optional[np.ndarray]:
    """
    Downloads FAQs from the remote to the local.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    question : str or list
        Term(s) to search for in the question field.
    answer : str or list
        Term(s) to search for in the answer field.
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
        style='FAQ', name=name, overwrite=overwrite,
        return_records=return_records, verbose=verbose,
        question=question, answer=answer)

def save_faq(self,
             faq: Record,
             overwrite: bool = False,
             verbose: bool = False):
    """
    Saves a FAQ to the local database.
    
    Parameters
    ----------
    faq : FAQ
        The record to save.  
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the local
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.save_record(record=faq, overwrite=overwrite, verbose=verbose)

def upload_faq(self,
               faq: Record,
               workspace: Union[str, pd.Series, None] = None,
               overwrite: bool = False,
               verbose: bool = False):
    """
    Uploads a FAQ to the remote database.
    
    Parameters
    ----------
    faq : FAQ
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
    self.upload_record(record=faq, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def delete_faq(self,
               faq: Record,
               local: bool = True,
               remote: bool = False,
               verbose: bool = False):
    """
    Deletes a FAQ from the local and/or remote locations.  

    Parameters
    ----------
    faq : FAQ
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
    self.delete_record(record=faq, local=local, remote=remote,
                       verbose=verbose)