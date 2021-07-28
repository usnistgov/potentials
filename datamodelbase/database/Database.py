# coding: utf-8
# Standard Python libraries
from pathlib import Path
import sys
import glob
import shutil
import tempfile

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import settings
from ..record import recordmanager
from ..tools import screen_input, aslist

class Database():
    """
    Class for handling different database styles in the same fashion.  This
    base class defines the common methods and attributes.
    """
    
    def __init__(self, host):
        """
        Initializes a connection to a database.
        
        Parameters
        ----------
        host : str
            The host name (path, url, etc.) for the database.
        """
        # Check that object is a subclass
        if self.__module__ == __name__:
            raise TypeError("Don't use Database itself, only use derived classes")
        
        # Set property values
        self.__host = host
    
    def __str__(self):
        """
        Returns
        -------
        str
            The string representation of the database.
        """
        return f'database style {self.style} at {self.host}'
    
    @property
    def style(self):
        """str: The database style"""
        raise NotImplementedError('Not defined for base class')
    
    @property
    def host(self):
        """str: The database's host."""
        return self.__host
    
    def get_records(self, style=None, name=None, query=None, return_df=False,
                    **kwargs):
        """
        Produces a list of all matching records in the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to search. If not given, a prompt will ask for it.
        name : str or list, optional
            Record name(s) to delimit by. 
        return_df : bool, optional
            If True, then the corresponding pandas.Dataframe of metadata
            will also be returned
        query : dict, optional
            A custom-built CDCS-style query to use for the record search.
            Alternative to passing in the record-specific metadata kwargs.
            Note that name can be given with query.
        keyword : str, optional
            Allows for a search of records whose contents contain a keyword.
            Alternative to giving query or kwargs.
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for.
            
        Returns
        ------
        records : numpy.NDArray
            All records from the database matching the given parameters.
        records_df : pandas.DataFrame
            The corresponding metadata values for the records.  Only returned
            if return_df is True.
        
        Raises
        ------
        AttributeError
            If get_records is not defined for database style.
        """
        raise AttributeError('get_records not defined for Database style')
    
    def get_record(self, name=None, style=None, query=None, **kwargs):
        """
        Returns a single matching record from the database.  Issues an error
        if multiple or no matching records are found.
        
        Parameters
        ----------
        name : str, optional
            The record name or id to limit the search by.
        style : str, optional
            The record style to limit the search by.
            
        Returns
        ------
        Record
            The single record from the database matching the given parameters.
        
        Raises
        ------
        AttributeError
            If get_record is not defined for database style.
        """
        raise AttributeError('get_record not defined for Database style')
    
    def get_records_df(self, name=None, style=None, query=None, full=True,
                       flat=False, **kwargs):
        """
        Produces a pandas.DataFrame of all matching records in the database.
        
        Parameters
        ----------
        style : str
            The record style to collect records of.
        full : bool, optional
            Flag used by the calculation records.  A True value will include
            terms for both the calculation's input and results, while a value
            of False will only include input terms (Default is True).
        flat : bool, optional
            Flag affecting the format of the dictionary terms.  If True, the
            dictionary terms are limited to having only str, int, and float
            values, which is useful for comparisons.  If False, the term
            values can be of any data type, which is convenient for analysis.
            (Default is False).
        
        Returns
        ------
        pandas.DataFrame
            All records from the database of the given record style.
        
        Raises
        ------
        AttributeError
            If get_record is not defined for database style.
        """
        raise AttributeError('get_records_df not defined for Database style')
    
    def add_record(self, record=None, name=None, style=None, model=None,
                   build=False, verbose=False):
        """
        Adds a new record to the database.
        
        Parameters
        ----------
        record : Record, optional
            The new record to add to the database.  If not given, then name,
            style and content are required.
        style : str, optional
            The record style for the new record.  Required if record is not
            given.
        name : str, optional
            The name to assign to the new record.  Required if record is not
            given.
        model : str or DataModelDict, optional
            The model contents of the new record.  Required if record is not
            given.
        build : bool, optional
            If True, then the uploaded content will be (re)built based on the
            record's attributes.  If False (default), then record's existing
            content will be loaded if it exists, or built if it doesn't exist.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
            
        Returns
        ------
        Record
            Either the given record or a record composed of the name, style,
            and content.
        
        Raises
        ------
        AttributeError
            If add_record is not defined for database style.
        """
        raise AttributeError('add_record not defined for Database style')
    
    def update_record(self, record=None, style=None, name=None, model=None,
                      build=False, verbose=False):
        """
        Replaces an existing record with a new record of matching name and
        style, but new content.
        
        Parameters
        ----------
        record : Record, optional
            The record with new content to update in the database.  If not
            given, content is required along with name and/or style to
            uniquely define a record to update.
        style : str, optional
            The style of the record to update.
        name : str, optional
            The name to uniquely identify the record to update.
        model : str or DataModelDict, optional
            The model contents of the new record.  Required if record is not
            given.
        build : bool, optional
            If True, then the uploaded content will be (re)built based on the
            record's attributes.  If False (default), then record's existing
            content will be loaded if it exists, or built if it doesn't exist.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.

        Returns
        ------
        Record
            Either the given record or a record composed of the name, style,
            and content.
        
        Raises
        ------
        AttributeError
            If update_record is not defined for database style.
        """
        raise AttributeError('update_record not defined for Database style')
    
    def delete_record(self, record=None, name=None, style=None):
        """
        Permanently deletes a record from the database.
        
        Parameters
        ----------
        record : Record, optional
            The record to delete from the database.  If not given, name and/or
            style are needed to uniquely define the record to delete.
        name : str, optional
            The name of the record to delete.
        style : str, optional
            The style of the record to delete.
        
        Raises
        ------
        AttributeError
            If delete_record is not defined for database style.
        """
        raise AttributeError('delete_record not defined for Database style')
    
    def get_tar(self, record=None, name=None, style=None, raw=False):
        """
        Retrives the tar archive associated with a record in the database.
        
        Parameters
        ----------
        record : Record, optional
            The record to retrive the associated tar archive for.
        name : str, optional
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
        raw : bool, optional
            If True, return the archive as raw binary content. If
            False, return as an open tarfile. (Default is False)
            
        Returns
        -------
        tarfile or str
            The tar archive as an open tarfile if raw=False, or as a binary
            str if raw=True.
        
        Raises
        ------
        AttributeError
            If get_tar is not defined for database style.
        """
        raise AttributeError('get_tar not defined for Database style')
    
    def add_tar(self, record=None, name=None, style=None, tar=None, root_dir=None):
        """
        Archives and stores a folder associated with a record.
        
        Parameters
        ----------
        record : Record, optional
            The record to associate the tar archive with.  If not given, then
            name and/or style necessary to uniquely identify the record are
            needed.
        name : str, optional
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
        tar : bytes, optional
            The bytes content of a tar file to save.  tar cannot be given
            with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  tar cannot be given
            with root_dir.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record or the record already
            has an archive.
        """
        raise AttributeError('add_tar not defined for Database style')
    
    def update_tar(self, record=None, name=None, style=None, tar=None, root_dir=None):
        """
        Replaces an existing tar archive for a record with a new one.
        
        Parameters
        ----------
        record : Record, optional
            The record to associate the tar archive with.  If not given, then 
            name and/or style necessary to uniquely identify the record are 
            needed.
        name : str, optional
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
        tar : bytes, optional
            The bytes content of a tar file to save.  tar cannot be given
            with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  tar cannot be given
            with root_dir.
        
        Raises
        ------
        AttributeError
            If update_tar is not defined for database style.
        """
        raise AttributeError('update_tar not defined for Database style')
    
    def delete_tar(self, record=None, name=None, style=None):
        """
        Deletes a tar file from the database.
        
        Parameters
        ----------
        record : Record, optional
            The record associated with the tar archive to delete.  If not
            given, then name and/or style necessary to uniquely identify
            the record are needed.
        name : str, optional
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
        
        Raises
        ------
        AttributeError
            If delete_tar is not defined for database style.
        """
        raise AttributeError('delete_tar not defined for Database style')
    
    def copy_records(self, dbase2, record_style=None, records=None, includetar=True, overwrite=False):
        """
        Copies records from one database to another.
        
        Parameters
        ----------
        dbase2 :  Database
            The database to copy to.
        record_style : str, optional
            The record style to copy.  If record_style and records not
            given, then the available record styles will be listed and the
            user prompted to pick one.  Cannot be given with records.
        records : list, optional
            A list of Record obejcts from the current database to copy
            to dbase2.  Allows the user full control on which records to
            copy/update.  Cannot be given with record_style.
        includetar : bool, optional
            If True, the tar archives will be copied along with the records.
            If False, only the records will be copied. (Default is True).
        overwrite : bool, optional
            If False (default) only new records and tars will be copied.
            If True, all existing content will be updated.
        """
        if record_style is None and records is None:
            # Prompt for record_style
            record_style = self.select_record_style()
        
        if record_style is not None:
            if records is not None:
                raise ValueError('record_style and records cannot both be given')
            
            # Retrieve records from self
            records = self.get_records(style=record_style) 
        
        elif records is None:
            # Set empty list if record_style is still None and no records given
            records = []
        
        print(len(records), 'records to try to copy')
        
        record_count = 0
        tar_count = 0
        # Copy records
        for record in records:
            try:
                # Add new records
                dbase2.add_record(record=record)
                record_count += 1
            except:
                # Update existing records
                if overwrite:
                    dbase2.update_record(record=record)
                    record_count += 1
            
            # Copy archives
            if includetar:
                try:
                    # Get tar if it exists
                    tar = self.get_tar(record=record, raw=True) 
                except:
                    
                    # Get folder if it exists
                    try:
                        root_dir = self.get_folder(record=record).parent
                    except:
                        pass
                    else:
                        try:
                            # Copy tar over
                            dbase2.add_tar(record=record, root_dir=root_dir)
                            tar_count += 1
                        except:
                            # Update existing tar
                            if overwrite:
                                dbase2.update_tar(record=record, root_dir=root_dir)
                                tar_count += 1
                    
                else:
                    try:
                        # Copy tar over
                        dbase2.add_tar(record=record, tar=tar)
                        tar_count += 1
                    except:
                        # Update existing tar
                        if overwrite:
                            dbase2.update_tar(record=record, tar=tar)
                            tar_count += 1
        
        print(record_count, 'records added/updated')
        if includetar:
            print(tar_count, 'tars added/updated')
    
    def destroy_records(self, record_style=None, records=None):
        """
        Permanently deletes multiple records and their associated tars all at
        once.
        
        Parameters
        ----------
        record_style : str, optional
            The record style to delete.  If given, all records of that style
            will be deleted. If neither record_style nor records given, then
            the available record styles will be listed and the user prompted
            to pick one.
        records : list, optional
            A list of pre-selected records to delete. 
        """
        # Select record_style if needed
        if record_style is None and records is None:
            record_style = self.select_record_style()

        # Get records by record_style
        if record_style is not None:
            if records is not None:
                raise ValueError('record_style and records cannot both be given')
            
            # Retrieve records with errors from self
            records = self.get_records(style=record_style) 
        
        elif records is None:
            # Set empty list if record_style is still None and no records given
            records = []

        print(f'{len(records)} records found to be destroyed')

        if len(records) > 0:
            test = screen_input('Delete records? (must type yes):')
            if test == 'yes':
                count = 0
                for record in records:
                    try:
                        self.delete_tar(record=record)
                    except:
                        pass
                    try:
                        self.delete_record(record=record)
                        count += 1
                    except:
                        pass
                
                print(count, 'records successfully deleted')
    
    def select_record_style(self):
        """
        Console prompt for selecting a record_style
        """
        # Build list of calculation records
        styles = recordmanager.loaded_style_names
        
        # Ask for selection
        print('Select record_style:')
        for i, style in enumerate(styles):
            print(i+1, style)
        choice = screen_input(':')
        try:
            choice = int(choice)
        except:
            record_style = choice
        else:
            record_style = styles[choice-1]
        print()
        
        return record_style
