# coding: utf-8
# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from datamodelbase.record import Record

class Link(Record):
    """
    Class for describing website link
    """
    def __init__(self, model=None, url=None, label=None, linktext=None):
        """
        Initializes a Link object providing a hyperlink to content.

        Parameters
        ----------
        model : str or DataModelDict, optional
            Model content or file path to model content.
        url : str, optional
            URL for the link.
        label : str, optional
            A short description label.
        linktext : str, optional
            The text for the link, i.e. what gets clicked on.
        """
        if model is not None:
            try:
                assert linktext is None
                assert label is None
                assert url is None
            except:
                raise TypeError('model cannot be given with any other parameter')
            else:
                self.load_model(model)
        else:
            self.set_values(linktext=linktext, label=label, url=url)

    @property
    def modelroot(self):
        return 'link'

    @property
    def xsl_filename(self):
        return ('potentials.xsl', 'link.xsl')

    @property
    def xsd_filename(self):
        return ('potentials.xsd', 'link.xsd')

    @property
    def url(self):
        """str: URL for the link"""
        return self.__url
    
    @url.setter
    def url(self, v):
        if v is None:
            self.__url = None
        else:
            self.__url = str(v)

    @property
    def label(self):
        """str or None: short descriptive label"""
        return self.__label
    
    @label.setter
    def label(self, v):
        if v is None:
            self.__label = None
        else:
            self.__label = str(v)
    
    @property
    def linktext(self):
        """str or None: text to show for the link"""
        return self.__linktext
    
    @linktext.setter
    def linktext(self, v):
        if v is None:
            self.__linktext = None
        else:
            self.__linktext = str(v)

    def set_values(self, url=None, label=None, linktext=None):
        """
        Sets an Artifact object's attributes

        Parameters
        ----------
        url : str, optional
            URL for the link.
        label : str, optional
            A short description label.
        linktext : str, optional
            The text for the link, i.e. what gets clicked on.
        """
        self.linktext = linktext
        self.label = label
        self.url = url

    def load_model(self, model):
        """
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        """
        link = DM(model).find('link')
        self.url = link['web-link'].get('URL', None)
        self.label = link['web-link'].get('label', None)
        self.linktext = link['web-link'].get('link-text', None)
        
    def build_model(self):
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
    
    def metadata(self):
        """Returns a flat dict representation of the object"""
        meta = {}
        meta['linktext'] = self.linktext
        meta['label'] = self.label
        meta['url'] = self.url

        return meta