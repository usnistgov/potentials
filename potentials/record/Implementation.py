# coding: utf-8
# Standard libraries
import io
import uuid
from typing import Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

# Local imports
from .Artifact import Artifact
from .Parameter import Parameter
from .Link import Link

class Implementation(Record):
    """
    Class for representing Implementation metadata records. . Note that this is
    meant as a component class for other record objects.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self):
        """str: The record style"""
        return 'implementation'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'implementation'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'implementation.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'implementation.xsd')

    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'key', valuerequired=True,
                        defaultvalue=str(uuid.uuid4()))
        self._add_value('str', 'id')
        self._add_value('str', 'status', valuerequired=True,
                        defaultvalue='active',
                        allowedvalues=['active', 'superseded', 'retracted'])
        self._add_value('date', 'date')
        self._add_value('str', 'type')
        self._add_value('str', 'notes', modelpath='notes.text')
        self._add_value('record', 'artifacts', recordclass=Artifact,
                        modelpath='artifact')
        self._add_value('record', 'parameters', recordclass=Parameter,
                        modelpath='parameter')
        self._add_value('record', 'links', recordclass=Link,
                        modelpath='link')

    def add_artifact(self,
                     model: Union[str, io.IOBase, DM, None] = None,
                     **kwargs):
        """
        Initializes an Artifact object and adds it to the artifacts list.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Model content or file path to model content.
        filename : str, optional
            The name of the file without path information.
        label : str, optional
            A short description label.
        url : str, optional
            URL for file where downloaded, if available.
        """
        self.get_value('artifacts').append(model=model, **kwargs)

    def add_link(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 **kwargs):
        """
        Initializes a Link object and adds it to the links list.
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Model content or file path to model content.
        url : str, optional
            URL for the link.
        label : str, optional
            A short description label.
        linktext : str, optional
            The text for the link, i.e. what gets clicked on.
        """
        self.get_value('links').append(model=model, **kwargs)

    def add_parameter(self,
                      model: Union[str, io.IOBase, DM, None] = None,
                      **kwargs):
        """
        Initializes a Parameter object and adds it to the parameters list.
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Data model content to load.
        name : str, optional
            The name of the parameter or string parameter line.
        value : float, optional
            The value of the parameter.
        unit : str, optional
            Units associated with value.
        """
        self.get_value('parameters').append(model=model, **kwargs)
