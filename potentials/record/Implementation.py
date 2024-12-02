# coding: utf-8
# Standard libraries
import io
import uuid
import datetime
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba import load_value

# Local imports
from ..tools import aslist
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
        
        self.__key = load_value('str', 'key', self,
                                valuerequired=True,
                                defaultvalue=str(uuid.uuid4()))
        self.__id = load_value('str', 'id', self)
        self.__status = load_value('str', 'status', self,
                                   valuerequired=True,
                                   defaultvalue='active',
                                   allowedvalues=['active', 'superseded', 'retracted'])
        self.__date = load_value('date', 'date', self)
        self.__type = load_value('str', 'type', self)
        self.__notes = load_value('str', 'notes', self,
                                  modelpath='notes.text')
        self.__artifacts = load_value('record', 'artifacts', self, recordclass=Artifact,
                                  modelpath='artifact')
        self.__parameters = load_value('record', 'parameters', self, recordclass=Parameter,
                                  modelpath='parameter')
        self.__links = load_value('record', 'links', self, recordclass=Link,
                                  modelpath='link')
        
        value_objects.extend([self.__key, self.__id, self.__status, self.__date,
                              self.__type, self.__notes, self.__artifacts,
                              self.__parameters, self.__links])

        return value_objects

    @property
    def key(self) -> Optional[str]:
        """str : The UUID4 key assigned to the implementation."""
        return self.__key.value
    
    @key.setter
    def key(self, val: Optional[str]):
        self.__key.value = val
            
    @property
    def id(self) -> Optional[str]:
        """str : The unique id assigned to the implementation."""
        return self.__id.value
    
    @id.setter
    def id(self, val: Optional[str]):
        self.__id.value = val

    @property
    def status(self) -> str:
        """str : The current status of the implementation."""
        return self.__status.value
    
    @status.setter
    def status(self, val: Optional[str]):
        self.__status.value = val

    @property
    def date(self) -> datetime.date:
        """datetime.date : The date associated with the implementation listing"""
        return self.__date.value
    
    @date.setter
    def date(self, val: Union[datetime.date, str, None]):
        self.__date.value = val
        
    @property
    def type(self) -> Optional[str]:
        """str : The format of the implementation."""
        return self.__type.value
    
    @type.setter
    def type(self, val: Optional[str]):
        self.__type.value = val
    
    @property
    def notes(self) -> Optional[str]:
        """str : Any additional notes that describe details about the implementation."""
        return self.__notes.value

    @notes.setter
    def notes(self, val: Optional[str]):
        self.__notes.value = val

    @property
    def artifacts(self) -> list:
        """list: The Artifact component objects associated with the implementation."""
        return self.__artifacts.value

    @artifacts.setter
    def artifacts(self, val: Union[Record, list]):
        self.__artifacts.value = val

    @property
    def parameters(self) -> list:
        """list: The Parameter component objects associated with the implementation."""
        return self.__parameters.value

    @parameters.setter
    def parameters(self, val: Union[Record, list]):
        self.parameters.value = val

    @property
    def links(self) -> list:
        """list: The Link component objects associated with the implementation."""
        return self.__links.value

    @links.setter
    def links(self, val: Union[Record, list]):
        self.__links.value = val

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
        self.__artifacts.append(model=model, **kwargs)

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
        self.__links.append(model=model, **kwargs)

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
        self.__parameters.append(model=model, **kwargs)
