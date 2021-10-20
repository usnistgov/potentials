# coding: utf-8
# Standard Python libraries
from pathlib import Path
import shutil
import tarfile
from collections import OrderedDict

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://api.mongodb.com/python/current/
from pymongo import MongoClient
from gridfs import GridFS

from DataModelDict import DataModelDict as DM

# iprPy imports
from ..tools import aslist, iaslist
from . import Database
from .. import load_record, recordmanager

class MongoDatabase(Database):
    
    def __init__(self, host='localhost', port=27017, database='iprPy', **kwargs):
        """
        Initializes a connection to a Mongo database.
        
        Parameters
        ----------
        host : str
            The mongo host to connect to.  Default value is 'localhost'.
        port : int
            Then port to use in connecting to the mongo host.  Default value
            is 27017.
        database : str
            The name of the database in the mongo host to interact with.
            Default value is 'iprPy'
        **kwargs : dict, optional
            Any extra keyword arguments needed to initialize a
            pymongo.MongoClient object.
        """
        
        # Connect to underlying class
        self.__mongodb = MongoClient(host=host, port=port, document_class=DM, **kwargs)[database]
        
        # Define class host using client's host, port and database name
        host = self.mongodb.client.address[0]
        port =self.mongodb.client.address[1]
        database = self.mongodb.name
        host = f'{host}:{port}.{database}'
        
        # Pass host to Database initializer
        Database.__init__(self, host)
    
    @property
    def style(self):
        """str: The database style"""
        return 'mongo'

    @property
    def mongodb(self):
        """pymongo.Database : The underlying database API object."""
        return self.__mongodb
    
    def get_records(self, style=None, return_df=False, query=None, **kwargs):
        """
        Produces a list of all matching records in the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to search.  If not given, a prompt will ask for it.
        return_df : bool, optional
            If True, then the corresponding pandas.Dataframe of metadata
            will also be returned
        query : dict, optional
            A custom-built Mongo-style query to use for the record search.
            Alternative to passing in the record-specific metadata kwargs.
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
        # Set default search parameters
        if style is None:
            style = self.select_record_style()

        # Use given query
        if query is not None:
            assert len(kwargs) == 0, 'query cannot be given with kwargs'
        else:
            query = load_record(style).mongoquery(**kwargs)
        
        # Query the collection to construct records
        records = []
        collection = self.mongodb[style]
        for entry in collection.find(query):
            record = load_record(style, model=entry['content'],
                                 name=entry['name'])
            records.append(record)
        records = np.array(records)

        # Build df
        if len(records) > 0:
            df = []
            for record in records:
                df.append(record.metadata())
            df = pd.DataFrame(df)
        else:
            df = pd.DataFrame({'name':[]})

        # Sort by name
        df = df.sort_values('name')
        records = records[df.index.tolist()]

        # Return records (and df)
        if return_df:
            return records, df.reset_index(drop=True)
        else:
            return records

    def get_records_df(self, style=None, query=None, **kwargs):
        """
        Produces a pandas.Dataframe of all matching records in the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to search.
        query : dict, optional
            A custom-built Mongo-style query to use for the record search.
            Alternative to passing in the record-specific metadata keywords.
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for.
            
        Returns
        -------
        records_df : pandas.DataFrame
            The corresponding metadata values for the records.
        """
        return self.get_records(style, query=query, return_df=True, **kwargs)[1]
    
    def get_record(self, style=None, query=None, **kwargs):
        """
        Retrieves a single matching record from the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to search.
        query : dict, optional
            A custom-built Mongo-style query to use for the record search.
            Alternative to passing in the record-specific metadata keywords.
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for.
            
        Returns
        ------
        Record
            The record from the database matching the given parameters.
        
        Raises
        ------
        ValueError
            If multiple or no matching records found.
        """
        
        if style is None:
            styles = recordmanager.loaded_style_names
        else:
            styles = aslist(style)

        # Get records
        records = []
        for style in styles:
            records.append(self.get_records(style, query=query, **kwargs))
        records = np.hstack(records)
        
        # Verify that there is only one matching record
        if len(records) == 1:
            return records[0]
        elif len(records) == 0:
            raise ValueError('No matching records found')
        else:
            raise ValueError('Multiple matching records found')

    def add_record(self, record=None, style=None, name=None, model=None,
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
        ValueError
            If style, name and/or content given with record, or a matching record
            already exists.
        """

        # Create Record object if not given
        if record is None:
            record = load_record(style, model, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None or model is not None:
            raise ValueError('kwargs style, name, and content cannot be given with kwarg record')

        # Verify that there isn't already a record with a matching name
        if len(self.get_records(name=record.name, style=record.style)) > 0:
            raise ValueError(f'Record {record.name} already exists')

        # Retrieve/build model contents
        try:
            assert build is False
            model = record.model
        except:
            model = record.build_model()

        # Create meta mongo entry
        entry = OrderedDict()
        entry['name'] = record.name
        entry['content'] = model
        
        # Upload to mongodb
        self.mongodb[record.style].insert_one(entry)

        if verbose:
            print(f'{record} added to {self.host}')

        return record

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
        TypeError
            If no new content is given.
        ValueError
            If style and/or name content given with record.
        """
        
        # Create Record object if not given
        if record is None:
            if model is None:
                raise TypeError('no new model given')
            oldrecord = self.get_record(name=name, style=style)
            record = load_record(oldrecord.style, model, name=oldrecord.name)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Replace model in record object
        elif model is not None:
            oldrecord = record
            record = load_record(oldrecord.style, model, name=oldrecord.name)
            
        # Find oldrecord matching record
        else:
            oldrecord = self.get_record(name=record.name, style=record.style)
        
        # Delete oldrecord
        self.delete_record(record=oldrecord)
        
        # Add new record
        self.add_record(record=record, build=build)
        
        if verbose:
            print(f'{record} updated in {self.host}')

        return record
    
    def delete_record(self, record=None, name=None, style=None, verbose=False):
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
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.

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

        # Build delete query
        query = {}
        query['name'] = record.name

        # Delete record 
        self.mongodb[record.style].delete_one(query)

        if verbose:
            print(f'{record} deleted from {self.host}')

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
        
        # Define mongofs
        mongofs = GridFS(self.mongodb, collection=record.style)
        
        # Check if an archive already exists
        if mongofs.exists({"recordname": record.name}):
            raise ValueError('Record already has an archive')
        
        if tar is None:
            if root_dir is None:
                root_dir = Path.cwd()
                
            # Make archive
            basename = Path(root_dir, record.name)
            filename = Path(root_dir, record.name + '.tar.gz')
            shutil.make_archive(basename, 'gztar', root_dir=root_dir,
                                base_dir=record.name)
        
            # Upload archive
            with open(filename, 'rb') as f:
                tries = 0
                while tries < 2:
                    if True:
                        mongofs.put(f, recordname=record.name)
                        break
                    else:
                        tries += 1
                if tries == 2:
                    raise ValueError('Failed to upload archive 2 times')
        
            # Remove local archive copy
            filename.unlink()
            
        elif root_dir is None:
            # Upload archive
            tries = 0
            while tries < 2:
                if True:
                    mongofs.put(tar, recordname=record.name)
                    break
                else:
                    tries += 1
            if tries == 2:
                raise ValueError('Failed to upload archive 2 times')
        else:
            raise ValueError('tar and root_dir cannot both be given')
        
    def get_tar(self, record=None, name=None, style=None, raw=False):
        """
        Retrives the tar archive associated with a record in the database.
                
        Parameters
        ----------
        record : Record, optional
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
        
        # Issue a TypeError for competing kwargs
        elif style is not None or name is not None:
            raise TypeError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)
        
        # Define mongofs
        mongofs = GridFS(self.mongodb, collection=record.style)
        
        # Build query
        query = {}
        query['recordname'] = record.name
        
        # Get tar
        matches = list(mongofs.find(query))
        if len(matches) == 1:
            tar = matches[0]
        elif len(matches) == 0:
            raise ValueError('No tar found for the record')
        else:
            raise ValueError('Multiple tars found for the record')

        # Return content
        if raw is True:
            return tar.read()
        else:
            return tarfile.open(fileobj=tar)

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
        
        # Define mongofs
        mongofs = GridFS(self.mongodb, collection=record.style)
        
        # Build query
        query = {}
        query['recordname'] = record.name
        
        # Get tar
        matches = list(mongofs.find(query))
        if len(matches) == 1:
            tar = matches[0]
        elif len(matches) == 0:
            raise ValueError('No tar found for the record')
        else:
            raise ValueError('Multiple tars found for the record')
        
        # Delete tar
        mongofs.delete(tar._id)
    
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
        """
        
        # Delete the existing tar archive stored in the database
        self.delete_tar(record=record, name=name, style=style)
        
        # Add the new tar archive
        self.add_tar(record=record, name=name, style=style, tar=tar, root_dir=root_dir)