# Standard Python libraries
from pathlib import Path
import sys

from importlib import resources

from IPython.core.display import display, HTML

# https://lxml.de/
import lxml.etree as ET

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

class Record():
    """
    Class for handling different record styles in the same fashion.  The
    base class defines the common methods and attributes.
    """
    
    def __init__(self, model=None, name=None, **kwargs):
        """
        Initializes a Record object for a given style.
        
        Parameters
        ----------
        model : str, file-like object, DataModelDict
            The contents of the record.
        name : str, optional
            The unique name to assign to the record.  If model is a file
            path, then the default record name is the file name without
            extension.
        """
        self.__model = None
        self.__name = None
        # Check that object is a subclass
        if self.__module__ == __name__:
            raise TypeError("Don't use Record itself, only use derived classes")
        
        if model is not None:
            assert len(kwargs) == 0
            self.load_model(model, name=name)
        else:
            self.set_values(name=name, **kwargs)

    def load_model(self, model, name=None):
        """
        Loads model contents  
        """
        # Get name if model is a filename
        if name is None:
            try:
                if Path(model).is_file():
                    self.name = Path(model).stem
            except:
                pass
        else:
            self.name = name

        self._set_model(model)

    def set_values(self, name=None, **kwargs):
        """
        Sets multiple object values
        """
        raise NotImplementedError('Not defined for this class')

    def __str__(self):
        """str: The string representation of the record"""
        return f'{self.style} record named {self.name}'
    
    @property
    def style(self):
        """str: The record style"""
        raise NotImplementedError('Not defined for base class')
    
    @property
    def xsd_filename(self):
        """tuple: The module path and file name of the record's xsd schema"""
        raise NotImplementedError('Not implemented')

    @property
    def xsd(self):
        """bytes: The xml schema for the record style."""
        return resources.read_binary(*self.xsd_filename)

    @property
    def xsl_filename(self):
        """tuple: The module path and file name of the record's xsl html transformer"""
        raise NotImplementedError('Not implemented')

    @property
    def xsl(self):
        """BytesIO: The xml schema for the record style."""
        return resources.read_binary(*self.xsl_filename)

    @property
    def name(self):
        """str: The record's name."""
        if self.__name is not None:
            return self.__name
        else:
            raise AttributeError('record name not set')
    
    @name.setter
    def name(self, value):
        if value is not None:
            self.__name = str(value)
        else:
            self.__name = None
    
    @property
    def modelroot(self):
        """str : The name of the root element in the model contents."""
        raise NotImplementedError('Specific to subclasses')

    @property
    def model(self):
        """DataModelDict: The record's model content."""
        if self.__model is not None:
            return self.__model
        else:
            raise AttributeError('model content has not been loaded or built')
    
    def reload_model(self):
        """
        Reloads the record based on the model content.  This allows for direct
        changes to the model to be updated to the object. 
        """
        self.load_model(model=self.model, name=self.name)

    def _set_model(self, model):
        """
        Sets model content - called by build_model() and load_model() to update
        content.  Use load_model() if you are passing in an external model.
        """
        
        # Load model as DataModelDict
        content = DM(model).find(self.modelroot)
        self.__model = DM([(self.modelroot, content)])

    def build_model(self):
        """
        Generates and returns model content based on the values set to object.
        """
        raise NotImplementedError('Not defined for this class')

    def metadata(self):
        """
        Returns a dict of simple values for easy comparison.
        """
        raise NotImplementedError('Specific to subclasses')
    
    @staticmethod
    def pandasfilter(dataframe, **kwargs):
        """
        Filters a pandas.DataFrame based on kwargs values for the record style.
        
        Parameters
        ----------
        dataframe : pandas.DataFrame
            A table of metadata for multiple records of the record style.
        **kwargs : any
            Any of the record style-specific search parameters.
        
        Returns
        -------
        pandas.Series, numpy.NDArray?
            Boolean map of matching values
        """
        return [True for i in range(len(dataframe))]

    @staticmethod
    def mongoquery(**kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        root : str, optional
            Any extra model root(s) to prefix the model paths with.  Used by the
            different database styles.
        **kwargs : any
            Any of the record style-specific search parameters.
        
        Returns
        -------
        dict
            The Mongo-style query
        """
        return {}

    @staticmethod
    def cdcsquery(**kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        root : str, optional
            Any extra model root(s) to prefix the model paths with.  Used by the
            different database styles.
        **kwargs : any
            Any of the record style-specific search parameters.
        
        Returns
        -------
        dict
            The Mongo-style query
        """
        return {}

    def html(self, render=False):
        """Returns an HTML representation of the object"""

        # Build xml content
        xml_content = self.model.xml()
        
        xml = ET.fromstring(xml_content.encode('UTF-8'))

        # Read xsl content
        xsl = ET.fromstring(self.xsl)
        
        # Transform to html
        transform = ET.XSLT(xsl)
        html = transform(xml)
        html_content = ET.tostring(html).decode('UTF-8')

        if render:
            display(HTML(html_content))
        else:
            return html_content

    def valid_xml(self, xml_content=None):
        """
        Tests if XML content is valid with schema.
        
        Parameters
        ----------
        xml_content : str, optional
            XML content to test against the record's schema.
            If not given, will generate the xml using build_model.
        
        Returns
        -------
        bool
            Indicating if XML is valid.
        """

        # Build xml content
        if xml_content is None:
            xml_content = self.model.xml()
            
        xml = ET.fromstring(xml_content.encode('UTF-8'))

        # Read xsd content
        xsd = ET.fromstring(self.xsd)
        
        schema = ET.XMLSchema(xsd)
        return schema.validate(xml)
