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
from yabadaba import load_value

class Artifact(Record):
    """
    Class for describing artifacts (files accessible online). Note that this is
    meant as a component class for other record objects.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'implementation_artifact'

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

    ####################### Define Values and attributes #######################

    def _init_value_objects(self) -> list:
        """
        Method that defines the value objects for the Record.  This should
        1. Call the method's super() to get default Value objects.
        2. Use yabadaba.load_value() to build Value objects that are set to
           private attributes of self.
        3. Append the list returned by the super() with the new Value objects.

        Returns
        -------
        value_objects: A list of all value objects.
        """
        value_objects = super()._init_value_objects()
        
        self.__url = load_value('str', 'url', self,
                                modelpath='web-link.URL')
        self.__label = load_value('longstr', 'label', self,
                                  modelpath='web-link.label')
        self.__filename = load_value('longstr', 'filename', self,
                                     modelpath='web-link.link-text')
        
        value_objects.extend([self.__url, self.__label, self.__filename])

        return value_objects

    @property
    def url(self) -> Optional[str]:
        """str or None: URL where file can be downloaded"""
        return self.__url.value
    
    @url.setter
    def url(self, val: Optional[str]):
        self.__url.value = val

    @property
    def label(self) -> Optional[str]:
        """str or None: short descriptive label"""
        return self.__label.value
    
    @label.setter
    def label(self, val: Optional[str]):
        self.__label.value = val
    
    @property
    def filename(self) -> Optional[str]:
        """str or None: name of the file"""
        return self.__filename.value
    
    @filename.setter
    def filename(self, val: Optional[str]):
        self.__filename.value = val

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
