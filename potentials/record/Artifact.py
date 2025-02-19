# coding: utf-8
# Standard Python libraries
from pathlib import Path
from typing import Tuple, Union

# https://requests.readthedocs.io/en/master/
import requests

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

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

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'url', modelpath='web-link.URL')
        self._add_value('longstr', 'label', modelpath='web-link.label')
        self._add_value('longstr', 'filename', modelpath='web-link.link-text')

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
