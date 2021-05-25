# coding: utf-8
# Standard Python libraries
from pathlib import Path
import ast
import shutil
import tarfile

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# iprPy imports
from ..tools import aslist, iaslist
from . import Database
from .. import load_record, recordmanager

class LocalDatabase(Database):
    
    def __init__(self, host, format='json', indent=None):
        """
        Initializes a connection to a local database of JSON/XML records
        stored in a local directory.
        
        Parameters
        ----------
        host : str
            The host name (local directory path) for the database.
        format : str, optional
            The format that the model records are saved as.  Can be either
            JSON or XML.  Default value is JSON.
        indent : int or None, optional
            The indentation used when saving the records.  If None (default)
            then the saved records are compact.  Otherwise, the lines in the
            file will be indented by multiples of this value based on the
            model's element recursion.
        """
        # Get absolute path to host
        host = Path(host).resolve()
        
        # Make the path if needed
        if not host.is_dir():
            host.mkdir(parents=True)
        
        # Pass host to Database initializer
        Database.__init__(self, host)

        # Set default format and indent values
        self.__format = format
        self.__indent = indent
    
    @property
    def style(self):
        """str: The database style"""
        return 'local'

    @property
    def format(self):
        """str: The format that records are saved as: 'json' or 'xml'"""
        return self.__format
    
    @property
    def indent(self):
        """int or None: The record indentation setting to use when saving records."""
        return self.__indent

    def cache(self, style, refresh=False, addnew=True):
        
        recordmanager.assert_style(style)
        
        cachefile = Path(self.host, f'{style}.csv')

        if cachefile.is_file() and refresh is False:
            # Load cachefile
            cache = pd.read_csv(cachefile)

            def interpret(series, key):
                """Safely convert dict and list elements from str"""
                try:
                    assert series[key][0] in '{['
                    return ast.literal_eval(series[key])
                except:
                    return series[key]
            
            # Interpret dict and list elements
            for key in cache.keys():
                cache[key] = cache.apply(interpret, axis=1, args=[key])

        else:
            # Initialize new cache
            cache = pd.DataFrame({'name':[]})

        # Search local directory
        if addnew is True:
            newrecords = []
            currentnames = cache.name.to_list()
            for fname in Path(self.host, style).glob(f'*.{self.format}'):
                name = fname.stem

                # Add new entries
                if name not in currentnames:
                    
                    record = load_record(style, fname)
                    newrecords.append(record.metadata())
                
            # Update cache if needed
            if len(newrecords) > 0:
                newrecords = pd.DataFrame(newrecords)

                cache = cache.append(newrecords, sort=False).sort_values('name').reset_index(drop=True)
                cache.to_csv(cachefile, index=False)

        return cache

    def get_records(self, style=None, return_df=False, **kwargs):
        """
        Produces a list of all matching records in the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to search.
        return_df : bool, optional
            If True, then the corresponding pandas.Dataframe of metadata
            will also be returned
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
        """
        # Get df
        df = self.get_records_df(style, **kwargs)
        
        # Load only the matching records
        records = []
        if len(df) > 0:
            for name in df.name:
                fname = Path(self.host, style, f'{name}.{self.format}')
                records.append(recordmanager.init(style, model=fname))
        
        records = np.array(records)
        
        if return_df:
            return records, df
        else:
            return records
    
    def get_records_df(self, style=None, **kwargs):
        """
        Produces a table of metadata for matching records in the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to limit the search by.
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for.
        
        Returns
        ------
        records_df : pandas.DataFrame
            The corresponding metadata values for the records.
        """
        
       # Set default search parameters
        if style is None:
            style = self.select_record_style()
        
        # Load cache file for the record style
        cache = self.cache(style)
        
        # Construct mask of records to return
        mask = recordmanager.pandasfilter(style, cache, **kwargs)
        df = cache[mask].reset_index(drop=True)
        
        return df

    def get_record(self, style=None, **kwargs):
        """
        Returns a single matching record from the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to limit the search by.
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for.
        
        Returns
        ------
        iprPy.Record
            The single record from the database matching the given parameters.
        
        Raises
        ------
        ValueError
            If multiple or no matching records found.
        """
        
        # Get records
        record = self.get_records(style, **kwargs)
        
        # Verify that there is only one matching record
        if len(record) == 1:
            return record[0]
        elif len(record) == 0:
            raise ValueError(f'No matching record found')
        else:
            raise ValueError('Multiple matching records found')

    def add_record(self, record=None, style=None, name=None, model=None, verbose=False):
        """
        Adds a new record to the database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The new record to add to the database.  If not given, then name,
            style and model are required.
        name : str, optional
            The name to assign to the new record.  Required if record is not
            given.
        style : str, optional
            The record style for the new record.  Required if record is not
            given.
        model : str, optional
            The xml content of the new record.  Required if record is not
            given.
            
        Returns
        ------
        iprPy.Record
            Either the given record or a record composed of the name, style,
            and model.
        
        Raises
        ------
        ValueError
            If style, name and/or model given with record, or a matching record
            already exists.
        """
        
        # Create Record object if not given
        if record is None:
            record = load_record(style, model, name=name)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None or model is not None:
            raise ValueError('kwargs style, name, and model cannot be given with kwarg record')

        # Verify that there isn't already a record with a matching name
        style_dir = Path(self.host, record.style)
        fname = Path(style_dir, f'{record.name}.{self.format}')
        if fname.is_file():
            raise ValueError(f'Record {record.name} already exists')
        
        # Make record style directory if needed
        if not style_dir.is_dir():
            style_dir.mkdir()
        
        with open(fname, 'w', encoding='UTF-8') as f:
            if self.format == 'json':
                record.build_model().json(fp=f, indent=self.indent, ensure_ascii=False)
            elif self.format == 'xml':
                record.build_model().xml(fp=f, indent=self.indent)
        
        if verbose:
            print(f'{record} added to {self.host}')

        return record

    def update_record(self, record=None, style=None, name=None, model=None, verbose=False):
        """
        Replaces an existing record with a new record of matching name and
        style, but new content.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record with new content to update in the database.  If not
            given, content is required along with name and/or style to
            uniquely define a record to update.
        name : str, optional
            The name to uniquely identify the record to update.
        style : str, optional
            The style of the record to update.
        model : str, optional
            The new xml content to use for the record.  Required if record is
            not given.
        
        Returns
        ------
        iprPy.Record
            Either the given record or a record composed of the name, style,
            and content.
        
        Raises
        ------
        TypeError
            If no new content is given.
        ValueError
            If style and/or name content given with record.
        """
        
        # Create Record object if not given
        if record is None:
            if model is None:
                raise TypeError('no new model given')
            
            record = load_record(style, model, name=name)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Replace content in record object
        elif model is not None:
            record = load_record(record.style, model, name=record.name)
            
        # Check if record already exists
        style_dir = Path(self.host, record.style)
        fname = Path(style_dir, f'{record.name}.{self.format}')
        if not fname.is_file():
            raise ValueError(f'No existing record {record.name} found')
        
        with open(fname, 'w', encoding='UTF-8') as f:
            if self.format == 'json':
                record.build_model().json(fp=f, indent=self.indent, ensure_ascii=False)
            elif self.format == 'xml':
                record.build_model().xml(fp=f, indent=self.indent)
        
        if verbose:
            print(f'{record} updated in {self.host}')

        return record
    
    def delete_record(self, record=None, name=None, style=None, verbose=False):
        """
        Permanently deletes a record from the database.  Will issue an error 
        if exactly one matching record is not found in the database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record to delete from the database.  If not given, name and/or
            style are needed to uniquely define the record to delete.
        name : str, optional
            The name of the record to delete.
        style : str, optional
            The style of the record to delete.
        
        Raises
        ------
        ValueError
            If style and/or name given with record.
        """
        
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
         # Delete record file
        fname = Path(self.host, record.style, f'{record.name}.{self.format}')
        if fname.is_file():
            fname.unlink()
        else:
            raise ValueError(f'No existing {record.style} record {record.name} found')

        if verbose:
            print(f'{record} deleted from {self.host}')

    def add_tar(self, record=None, name=None, style=None, tar=None, root_dir=None):
        """
        Archives and stores a folder associated with a record.  Issues an
        error if exactly one matching record is not found in the database, or
        the associated record already has a tar archive.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record to associate the tar archive with.  If not given, then
            name and/or style necessary to uniquely identify the record are
            needed.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
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
        
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)
        
        # Build path to record
        record_path = Path(self.host, record.style, record.name)
        tar_path = Path(self.host, record.style, f'{record.name}.tar.gz')
        
        # Check if an archive already exists
        if tar_path.is_file():
            raise ValueError('Record already has an archive')
        
        # Make archive
        if tar is None:
            if root_dir is None:
                root_dir = '.'
            target = Path(root_dir, record.name)

            tar = tarfile.open(tar_path, 'w:gz')
            tar.add(target, target.name)
            tar.close()
            
        elif root_dir is None:
            with open(tar_path, 'wb') as f:
                f.write(tar)
        else:
            raise ValueError('tar and root_dir cannot both be given')
    
    def get_tar(self, record=None, name=None, style=None, raw=False):
        """
        Retrives the tar archive associated with a record in the database.
        Issues an error if exactly one matching record is not found in the 
        database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record to retrive the associated tar archive for.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
        raw : bool, optional
            If True, return the archive as raw binary content. If 
            False, return as an open tarfile. (Default is False)
        
        Returns
        -------
        tarfile or str
            The tar archive as an open tarfile if raw=False, or as a binary str if
            raw=True.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record.
        """
        
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)
        
        # Build path to record
        tar_path = Path(self.host, record.style, record.name+'.tar.gz')
        
        # Return content
        if raw is True:
            with open(tar_path, 'rb') as f:
                return f.read()
        else:
            return tarfile.open(tar_path)

    def delete_tar(self, record=None, name=None, style=None):
        """
        Deletes a tar file from the database.  Issues an error if exactly one
        matching record is not found in the database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record associated with the tar archive to delete.  If not
            given, then name and/or style necessary to uniquely identify
            the record are needed.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record.
        """
        
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)
        
        # Build path to tar file
        tar_path = Path(self.host, record.style, record.name+'.tar.gz')
        
        # Delete record if it exists
        if tar_path.is_file():
            tar_path.unlink()

    def update_tar(self, record=None, name=None, style=None, tar=None, root_dir=None):
        """
        Replaces an existing tar archive for a record with a new one.  Issues
        an error if exactly one matching record is not found in the database.
        The record's name must match the name of the directory being archived.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record to associate the tar archive with.  If not given, then 
            name and/or style necessary to uniquely identify the record are 
            needed.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
        tar : bytes, optional
            The bytes content of a tar file to save.  tar cannot be given
            with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  tar cannot be given
            with root_dir.
        """
        
        # Delete the existing tar archive stored in the database
        self.delete_tar(record=record, name=name)
        
        # Add the new tar archive
        self.add_tar(record=record, name=name, style=style, tar=tar, root_dir=root_dir)