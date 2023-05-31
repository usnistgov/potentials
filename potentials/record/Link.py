# coding: utf-8
# Standard Python libraries
import io
from typing import Optional, Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

class Link(Record):
    """
    Class for describing website link
    """
    def __init__(self,
                 model: Union[str, io.IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 **kwargs):
        """
        Initializes a Link object providing a hyperlink to content. Note that
        this is meant as a component class for other record objects.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            A JSON/XML data model for the content.
        name : str, optional
            The name to assign to the record.  Not used by this class.
        database : yabadaba.Database, optional
            Allows for a default database to be associated with the record.
        url : str, optional
            URL for the link.
        label : str, optional
            A short description label.
        linktext : str, optional
            The text for the link, i.e. what gets clicked on.
        """
        assert name is None, 'name is not used by this class'
        assert database is None, 'database is not used by this class'
        super().__init__(model=model, name=name, database=database, **kwargs)

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'link'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'link.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'link.xsd')

    @property
    def url(self) -> Optional[str]:
        """str: URL for the link"""
        return self.__url
    
    @url.setter
    def url(self, v: Optional[str]):
        if v is None:
            self.__url = None
        else:
            self.__url = str(v)

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
    def linktext(self) -> Optional[str]:
        """str or None: text to show for the link"""
        return self.__linktext
    
    @linktext.setter
    def linktext(self, v: Optional[str]):
        if v is None:
            self.__linktext = None
        else:
            self.__linktext = str(v)

    def set_values(self,
                   name: Optional[str] = None,
                   **kwargs):
        """
        Sets an Artifact object's attributes

        Parameters
        ----------
        name : str, optional
            The name to assign to the record.  Not used by this class.
        url : str, optional
            URL for the link.
        label : str, optional
            A short description label.
        linktext : str, optional
            The text for the link, i.e. what gets clicked on.
        """
        assert name is None, 'name is not used by this class'
        self.linktext = kwargs.get('linktext', None)
        self.label = kwargs.get('label', None)
        self.url = kwargs.get('url', None)

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
        link = DM(model).find('link')
        self.url = link['web-link'].get('URL', None)
        self.label = link['web-link'].get('label', None)
        self.linktext = link['web-link'].get('link-text', None)
        
    def build_model(self) -> DM:
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict: The data model content.
        """
        model = DM()
        model['link'] = DM()
        model['link']['web-link'] = DM()
        if self.url is not None:
            model['link']['web-link']['URL'] = self.url
        if self.label is not None:
            model['link']['web-link']['label'] = self.label
        if self.linktext is not None:
            model['link']['web-link']['link-text'] = self.linktext
        
        return model
    
    def metadata(self) -> dict:
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        meta = {}
        meta['linktext'] = self.linktext
        meta['label'] = self.label
        meta['url'] = self.url

        return meta