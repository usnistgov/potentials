# coding: utf-8
# Standard Python libraries
import io
from pathlib import Path
from typing import Optional, Tuple, Union

# https://requests.readthedocs.io/en/master/
import requests

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

class Artifact(Record):
    """
    Class for describing artifacts (files accessible online). Note that this is
    meant as a component class for other record objects.
    """
    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 **kwargs):
        """
        Initializes an Artifact object to describe a file accessible online

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            A JSON/XML data model for the content.
        name : str, optional
            The name to assign to the record.  Not used by this class.
        database : yabadaba.Database, optional
            Allows for a default database to be associated with the record.
            Not used by this class.
        filename : str, optional
            The name of the file without path information.
        label : str, optional
            A short description label.
        url : str, optional
            URL for file where downloaded, if available.
        """
        assert name is None, 'name is not used by this class'
        assert database is None, 'database is not used by this class'
        super().__init__(model=model, name=name, database=database, **kwargs)

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'artifact'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'artifact.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'artifact.xsd')

    @property
    def filename(self) -> Optional[str]:
        """str or None: name of the file"""
        return self.__filename
    
    @filename.setter
    def filename(self, v: Optional[str]):
        if v is None:
            self.__filename = None
        else:
            self.__filename = str(v)

    @property
    def label(self) -> Optional[str]:
        """str or None: short descriptive label"""
        return self.__label
    
    @label.setter
    def label(self, v: Optional[str]):
        if v is None:
            self.__label = None
        else:
            self.__label = str(v)
    
    @property
    def url(self) -> Optional[str]:
        """str or None: URL where file can be downloaded"""
        return self.__url
    
    @url.setter
    def url(self, v: Optional[str]):
        if v is None:
            self.__url = None
        else:
            self.__url = str(v)

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs):
        """
        Sets an Artifact object's attributes

        Parameters
        ----------
        name : str, optional
            The name to assign to the record.  Not used by this class.
        filename : str, optional
            The name of the file without path information.
        label : str, optional
            A short description label.
        url : str, optional
            URL for file where downloaded, if available.
        """
        assert name is None, 'name is not used by this class'
        self.filename = kwargs.get('filename', None)
        self.label = kwargs.get('label', None)
        self.url = kwargs.get('url', None)

    def load_model(self,
                   model: Union[str, io.IOBase, DM],
                   name: Optional[str] = None):
        """"
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        name : str, optional
            The name to assign to the record.  Not used by this class.
        """
        assert name is None, 'name is not used by this class'
        artifact = DM(model).find('artifact')
        self.url = artifact['web-link'].get('URL', None)
        self.label = artifact['web-link'].get('label', None)
        self.filename = artifact['web-link'].get('link-text', None)
    
    def build_model(self) -> DM:
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict
            The data model content.
        """

        model = DM()
        model['artifact'] = DM()
        model['artifact']['web-link'] = DM()
        if self.url is not None:
            model['artifact']['web-link']['URL'] = self.url
        if self.label is not None:
            model['artifact']['web-link']['label'] = self.label
        if self.filename is not None:
            model['artifact']['web-link']['link-text'] = self.filename
        
        self._set_model(model)
        return model

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        meta = {}
        meta['filename'] = self.filename
        meta['label'] = self.label
        meta['url'] = self.url

        return meta

    def download(self,
                 targetdir: Union[str, Path],
                 overwrite: bool = False,
                 verbose: bool = False):
        """
        Downloads the artifact from its URL to the given target directory.

        Parameters
        ----------
        targetdir : path-like object
            The directory where the artifact is downloaded to.
        overwrite : bool, optional
            If False (default), then the file will not be downloaded if
            a similarly named file already exists in targetdir.
        verbose : bool, optional
            If True, info statements will be printed.  Default
            value is False.
        
        Returns
        -------
        bool
            True if the file was downloaded, False otherwise.
        """
        targetname = Path(targetdir, self.filename)
        
        # Check if targetname exists
        if overwrite or not targetname.exists():
            
            # Get the URL
            r = requests.get(self.url)
            
            # Print message if URL does not exist
            if r.status_code == 404:
                print(f'File URL not found: {self.url}')
                return False
            
            else:
                # Raise any other request errors
                r.raise_for_status()

                # Save downloaded content
                with open(targetname, 'wb') as f:
                    f.write(r.content)
                if verbose:
                    print(f'{self.filename} downloaded to {targetdir}')
                return True
        else:
            # Skip files that already exist
            if verbose:
                print(f'{self.filename} already in {targetdir}')
            return False