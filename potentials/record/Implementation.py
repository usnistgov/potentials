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
    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 **kwargs):
        """
        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            A JSON/XML data model for the content.
        name : str, optional
            The name to assign to the record.  Not used by this class.
        database : yabadaba.Database, optional
            Allows for a default database to be associated with the record.
        type : str, optional
            Describes the format for the implementation.
        key : str, optional
            The UUID4 key to assign to the implementation.
        id : str, optional
            The unique id to assign to the implementation.
        status : str, optional
            Specifies the current status of the implementation.
        date : datetime.date, optional
            A date associated with the implementation listing.
        notes : str, optional
            Any notes associated with the implementation.
        artifacts : list, optional
            Any Artifact objects or data to associate with the implementation.
        parameters : list, optional
            Any Parameter objects or data to associate with the implementation.
        links : list, optional
            Any Link objects or data to associate with the implementation.
        """
        assert name is None, 'name is not used by this class'
        assert database is None, 'database is not used by this class'
        super().__init__(model=model, name=name, database=database, **kwargs)

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

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs):
        """
        Sets an Implementation object's attributes

        Parameters
        ----------
        name : str, optional
            The name to assign to the record.  Not used by this class.
        type : str, optional
            Describes the format for the implementation.
        key : str, optional
            The UUID4 key to assign to the implementation.
        id : str, optional
            The unique id to assign to the implementation.
        status : str, optional
            Specifies the current status of the implementation.
        date : datetime.date, optional
            A date associated with the implementation listing.
        notes : str, optional
            Any notes associated with the implementation.
        artifacts : list, optional
            Any Artifact objects or data to associate with the implementation.
        parameters : list, optional
            Any Parameter objects or data to associate with the implementation.
        links : list, optional
            Any Link objects or data to associate with the implementation.
        """    
        assert name is None, 'name is not used by this class'
        
        # Build new record
        self.type = kwargs.get('type', None)
        self.key = kwargs.get('key', None)
        self.id = kwargs.get('id', None)
        self.status = kwargs.get('status', None)
        self.date = kwargs.get('date', None)
        self.notes = kwargs.get('notes', None)
        
        self.artifacts = []
        if 'artifacts' in kwargs:
            for artifact in aslist(kwargs['artifacts']):
                if isinstance(artifact, Artifact):
                    self.artifacts.append(artifact)
                else:
                    self.add_artifact(**artifact)
        
        self.parameters = []
        if 'parameters' in kwargs:
            for parameter in aslist(kwargs['parameters']):
                if isinstance(parameter, Parameter):
                    self.parameters.append(parameter)
                else:
                    self.add_parameter(**parameter)
        
        self.links = []
        if 'links' in kwargs:
            for link in aslist(kwargs['links']):
                if isinstance(link, Link):
                    self.links.append(link)
                else:
                    self.add_link(**link)

    @property
    def type(self) -> Optional[str]:
        """str : The format of the implementation."""
        return self.__type
    
    @type.setter
    def type(self, v: Optional[str]):
        if v is None:
            self.__type = None
        else:
            self.__type = str(v)

    @property
    def key(self) -> Optional[str]:
        """str : The UUID4 key assigned to the implementation."""
        return self.__key
    
    @key.setter
    def key(self, v: Optional[str]):
        if v is None:
            self.__key = str(uuid.uuid4())
        else:
            self.__key = str(v)
            
    @property
    def id(self) -> Optional[str]:
        """str : The unique id assigned to the implementation."""
        return self.__id
    
    @id.setter
    def id(self, v: Optional[str]):
        if v is None:
            self.__id = None
        else:
            self.__id = str(v)

    @property
    def status(self) -> str:
        """str : The current status of the implementation."""
        return self.__status
    
    @status.setter
    def status(self, v: Optional[str]):
        if v is None:
            self.__status = 'active'
        else:
            self.__status = str(v)

    @property
    def date(self) -> datetime.date:
        """datetime.date : The date associated with the implementation listing"""
        return self.__date
    
    @date.setter
    def date(self, v: Union[datetime.date, str, None]):
        if v is None:
            self.__date = datetime.date.today()
        elif isinstance(v, datetime.date):
            self.__date = v
        elif isinstance(v, str):
            self.__date = datetime.datetime.strptime(v, '%Y-%m-%d').date()
        else:
            raise TypeError('Invalid date type')
    
    @property
    def notes(self) -> Optional[str]:
        """str : Any additional notes that describe details about the implementation."""
        return self.__notes

    @notes.setter
    def notes(self, v: Optional[str]):
        if v is None:
            self.__notes = None
        else:
            self.__notes = str(v)

    def load_model(self,
                   model: Union[str, io.IOBase, DM],
                   name: Optional[str] = None):
        """
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str, file-like object or DataModelDict
            A JSON/XML data model for the content.
        name : str, optional
            The name to assign to the record.  Not used by this class.
        """
        assert name is None, 'name is not used by this class'
        model = DM(model)
        imp = model.find('implementation')
        self.key = imp['key']
        self.id = imp.get('id', None)
        self.status = imp.get('status', None)
        self.date = imp.get('date', None)
        self.type = imp.get('type', None)
        if 'notes' in imp:
            self.notes = imp['notes']['text']
        else:
            self.notes = None

        self.artifacts = []
        for artifact in imp.iteraslist('artifact'):
            self.add_artifact(model=DM([('artifact', artifact)]))

        self.parameters = []
        for parameter in imp.iteraslist('parameter'):
            self.add_parameter(model=DM([('parameter', parameter)]))

        self.links = []
        for link in imp.iteraslist('link'):
            self.add_link(model=DM([('link', link)]))

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        data = {}
        
        # Copy class attributes to dict
        data['key'] = self.key
        data['id'] = self.id
        data['date'] = self.date.isoformat()
        data['status'] = self.status
        data['notes'] = self.notes
        data['type'] = self.type

        data['artifacts'] = []
        for artifact in self.artifacts:
            data['artifacts'].append(artifact.metadata())
        
        data['parameters'] = []
        for parameter in self.parameters:
            data['parameters'].append(parameter.metadata())
        
        data['links'] = []
        for link in self.links:
            data['links'].append(link.metadata())
            
        return data

    def build_model(self) -> DM:
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict: The data model content.
        """

        model = DM()
        model['implementation'] = imp = DM()
        imp['key'] = self.key
        if self.id is not None:
            imp['id'] = self.id
        imp['status'] = self.status
        imp['date'] = str(self.date)
        if self.type is not None:
            imp['type'] = self.type
        if self.notes is not None:
            imp['notes'] = DM([('text', self.notes)])
        for artifact in self.artifacts:
            imp.append('artifact', artifact.build_model()['artifact'])
        for parameter in self.parameters:
            imp.append('parameter', parameter.build_model()['parameter'])
        for link in self.links:
            imp.append('link', link.build_model()['link'])
        
        return model

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
        self.artifacts.append(Artifact(model=model, **kwargs))

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
        self.links.append(Link(model=model, **kwargs))

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
        self.parameters.append(Parameter(model=model, **kwargs))
