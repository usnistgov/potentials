# Standard Python libraries
from pathlib import Path
import shutil
import tarfile
from io import BytesIO

from cdcs import CDCS

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# iprPy imports
from ..tools import aslist, iaslist
from . import Database
from .. import load_record, recordmanager

class CDCSDatabase(Database):
    
    def __init__(self, host, username=None, password=None, cert=None, verify=True):
        """
        Initializes a database of style curator.
        
        Parameters
        ----------
        host : str
            The host name (url) for the database.
        username : str or tuple of two str
            The username to use for accessing the database.  Alternatively, a
            tuple of (username, password).
        password : str, optional
            The password associated with username to use for accessing the database.
            This can either be the password as a str, or a str path to a file
            containing only the password. If not given, a prompt will ask for the
            password.
        cert : str, optional
            The path to a certification file if needed for accessing the database.
        verify : bool, optional
            Indicates if verifications for the site are used
        """
        
        # Fetch password from file if needed
        try:
            with open(password) as f:
                password = f.read().strip()
        except:
            pass
        
        # Pass parameters to cdcs object
        self.cdcs = CDCS(host, username=username, password=password,
                         cert=cert, verify=verify)
        
        # Pass host to Database initializer
        Database.__init__(self, host)
    
    @property
    def style(self):
        """str: The database style"""
        return 'cdcs'

    def get_records(self, style=None, name=None, return_df=False,
                    query=None, keyword=None, **kwargs):
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
        """
        # Set default search parameters
        if style is None:
            style = self.select_record_style()

        # Setup keyword search
        if keyword is not None:
            assert len(kwargs) == 0, 'keyword cannot be given with kwargs'
            assert query is None, 'keyword cannot be given with query'

        # Setup query
        elif query is not None:
            assert len(kwargs) == 0, 'query cannot be given with kwargs'
        else:
            query = load_record(style).cdcsquery(**kwargs)

        def build_records(series):
            return load_record(series.template_title, model=series.xml_content,
                               name=series.title)
        
        # Build records by querying for each record name (or None)
        records = []
        for n in iaslist(name):
            data = self.cdcs.query(title=n, template=style, mongoquery=query, keyword=keyword)
            records.extend(data.apply(build_records, axis=1))
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
    
    def get_records_df(self, style=None, name=None, query=None, keyword=None, **kwargs):
        """
        Produces a list of all matching records in the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to search. If not given, a prompt will ask for it.
        name : str or list, optional
            Record name(s) to delimit by. 
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
        -------
        records_df : pandas.DataFrame
            The corresponding metadata values for the records.
        """
        return self.get_records(style, name=name, query=query, keyword=keyword, return_df=True, **kwargs)[1]
    
    def get_record(self, style=None, name=None, query=None, keyword=None, **kwargs):
        """
        Returns a single matching record from the database.
        
        Parameters
        ----------
        style : str, optional
            Record style(s) to limit the search by.
        name : str or list, optional
            Record name(s) to delimit by. 
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
        Record
            The single record from the database matching the given parameters.
        
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
            records.append(self.get_records(style, name=name, query=query, keyword=keyword, **kwargs))
        records = np.hstack(records)

        # Verify that there is only one matching record
        if len(records) == 1:
            return records[0]
        elif len(records) == 0:
            raise ValueError('No matching records found')
        else:
            raise ValueError('Multiple matching records found')
    
    def add_record(self, record=None, style=None, name=None, model=None,
                   build=False, workspace=None, verbose=False):
        """
        Adds a new record to the database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
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
        workspace : str or pandas.Series, optional
            The name of a workspace to assign the record to.  If not given
            then the record is not assigned to a workspace and will only be
            accessible to the user who uploaded it.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.

        Returns
        ------
        Record
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
            
        # Retrieve/build model contents
        try:
            assert build is False
            content = record.model.xml()
        except:
            content = record.build_model().xml()

        # Upload to database
        self.cdcs.upload_record(template=record.style, content=content,
                                title=record.name)
        if verbose:
            print(f'{record} added to {self.host}')

        if workspace is not None:
            self.assign_records(record, workspace, verbose=verbose)

        return record
    
    def update_record(self, record=None, style=None, name=None, model=None,
                      build=False, workspace=None, verbose=False):
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
        workspace : str or pandas.Series, optional
            The name of a workspace to assign the record to.  If not given
            then the record is not assigned to a workspace and will only be
            accessible to the user who uploaded it.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.

        Returns
        ------
        Record
            Either the given record or a record composed of the name, style, 
            and model.
            
        Raises
        ------
        TypeError
            If no new content is given.
        ValueError
            If style, model, and/or name given with record.
        """
        
        # Create Record object if not given
        if record is None:
            if model is None:
                raise TypeError('no new model given')
            oldrecord = self.get_record(name=name, style=style)
            record = load_record(oldrecord.style, model, name=oldrecord.name)
        
        # Use given record object
        else:
            if style is not None or name is not None:
                raise ValueError('kwargs style and name cannot be given with kwarg record')
            
            # Replace model in record object
            if model is not None:
                record = load_record(record.style, model, name=record.name)
        
        # Retrieve/build model contents
        try:
            assert build is False
            content = record.model.xml()
        except:
            content = record.build_model().xml()

        # Upload to database
        self.cdcs.update_record(template=record.style, content=content,
                                title=record.name)
        
        if verbose:
            print(f'{record} updated in {self.host}')

        if workspace is not None:
            self.assign_records(record, workspace, verbose=verbose)

        return record
    
    def delete_record(self, record=None, name=None, style=None, verbose=False):
        """
        Permanently deletes a record from the database.  Will issue an error 
        if exactly one matching record is not found in the database.
        
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
        
        # Extract values from Record object if given
        if record is not None:
            if style is not None or name is not None:
                raise ValueError('kwargs style and name cannot be given with kwarg record')
            name = record.name
            style = record.style
         
        # Delete record
        self.cdcs.delete_record(template=style, title=name)

        if verbose:
            print(f'{record} deleted from {self.host}')

    def assign_records(self, records, workspace, verbose=False):
        """
        Assigns one or more records to a CDCS workspace.

        Parameters
        ----------
        records : Record or list
            The record(s) to assign to the workspace.
        workspace : str
            The workspace to assign the records to.
        verbose : bool, optional
            Setting this to True will print extra status messages.  Default
            value is False.
        """
        ids = []
        for record in aslist(records):
            self.cdcs.assign_records(workspace, template=record.style,
                                     title=record.name)
            if verbose:
                print(f'{record} assigned to workspace {workspace}')

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
        
        # Get Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        else:
            # Issue a ValueError for competing kwargs
            if style is not None or name is not None:
                raise ValueError('kwargs style and name cannot be given with kwarg record')

            # Verify that record exists
            record = self.get_record(name=record.name, style=record.style)
        
        # Check if an archive already exists
        blobs = self.cdcs.get_blobs(filename=record.name)
        if len(blobs) > 0:
            raise ValueError('Record already has an archive')
        
        # Create directory archive and upload
        if tar is None: 
            if root_dir is None:
                root_dir = Path.cwd()
                
            # Make archive
            basename = Path(root_dir, record.name)
            filename = Path(root_dir, record.name + '.tar.gz')
            shutil.make_archive(basename, 'gztar', root_dir=root_dir,
                                base_dir=record.name)
            
            # Upload archive
            tries = 0
            while tries < 2:
                if True:
                    url = self.cdcs.upload_blob(filename.as_posix())
                    break
                else:
                    tries += 1
            if tries == 2:
                raise ValueError('Failed to upload archive 2 times')
            
            # Remove local archive copy
            filename.unlink()
        
        # Upload pre-existing tar object
        elif root_dir is None:
            filename = Path(record.name + '.tar.gz')

            # Upload archive
            tries = 0
            while tries < 2:
                if True:
                    url = self.cdcs.upload_blob(filename=filename, blobbytes=BytesIO(tar))
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
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
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
        
        filename = Path(record.name + '.tar.gz')

        # Download tar file
        tardata = self.cdcs.get_blob_contents(filename=filename)
        
        # Return contents
        if raw is True:
            return tardata
        else:
            return tarfile.open(fileobj = BytesIO(tardata))
    
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
        
        filename = Path(record.name + '.tar.gz')

        self.cdcs.delete_blob(filename=filename)

    def update_tar(self, record=None, name=None, style=None, tar=None, root_dir=None):
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
        
        self.delete_tar(record=record, name=name, style=style)
        self.add_tar(record=record, name=name, style=style, tar=tar, root_dir=root_dir)