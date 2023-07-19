# coding: utf-8
# Standard Python libraries
import io
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

class Parameter(Record):
    """
    Class for describing parameter values. Note that this is
    meant as a component class for other record objects.
    """
    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 **kwargs):
        """
        Initializes a Parameter object to describe parameter values.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            A JSON/XML data model for the content.
        name : str, optional
            The name to assign to the record.  Not used by this class.
        database : yabadaba.Database, optional
            Allows for a default database to be associated with the record.
        paramname : str, optional
            The name of the parameter or string parameter line.
        value : float, optional
            The value of the parameter.
        unit : str, optional
            Units associated with value.
        """
        assert name is None, 'name is not used by this class'
        assert database is None, 'database is not used by this class'
        super().__init__(model=model, name=name, database=database, **kwargs)

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'parameter'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'parameter.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'parameter.xsd')


    @property
    def paramname(self) -> Optional[str]:
        """str: The name of the parameter, or a string parameter line"""
        return self.__paramname
    
    @paramname.setter
    def paramname(self, v: Optional[str]):
        if v is None:
            self.__paramname = None
        else:
            self.__paramname = str(v)
    
    @property
    def value(self) -> Optional[str]:
        """str or None: The value of the parameter"""
        return self.__value
    
    @value.setter
    def value(self, v: Optional[str]):
        if v is None:
            self.__value = None
        else:
            self.__value = float(v)

    @property
    def unit(self) -> Optional[str]:
        """str or None: The unit that the value is in"""
        return self.__unit
    
    @unit.setter
    def unit(self, v: Optional[str]):
        if v is None:
            self.__unit = None
        else:
            self.__unit = str(v)

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs):
        """
        Sets a Parameter object's attributes

        Parameters
        ----------
        name : str, optional
            The name to assign to the record.  Not used by this class.
        paramname : str, optional
            The name of the parameter or string parameter line.
        value : float, optional
            The value of the parameter.
        unit : str, optional
            Units associated with value.
        """
        assert name is None, 'name is not used by this class'
        self.paramname = kwargs.get('paramname', None)
        self.value = kwargs.get('value', None)
        self.unit = kwargs.get('unit', None)

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
        parameter = model.find('parameter')
        self.value = parameter.get('value', None)
        self.unit = parameter.get('unit', None)
        self.paramname = parameter.get('name', None)
        
    def build_model(self) -> DM:
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict: The data model content.
        """
        model = DM()
        model['parameter'] = DM()
        if self.value is not None:
            model['parameter']['value'] = self.value
        if self.unit is not None:
            model['parameter']['unit'] = self.unit
        if self.name is not None:
            model['parameter']['name'] = self.paramname
        
        return model

    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        meta = {}
        meta['value'] = self.value
        meta['unit'] = self.unit
        meta['paramname'] = self.paramname

        return meta