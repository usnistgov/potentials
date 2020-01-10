# coding: utf-8

from DataModelDict import DataModelDict as DM

class WebLink():
    """
    Class for describing website link
    """
    def __init__(self, model=None, url=None, label=None, linktext=None):
        """
        Initializes an WebLink object providing a hyperlink to content.

        Parameters
        ----------
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
                self.load(model)
        else:
            self.linktext = linktext
            self.label = label
            self.url = url

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

    def load(self, model):
        """
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        """
        weblink = model.find('web-link')
        self.url = weblink.get('URL', None)
        self.label = weblink.get('label', None)
        self.linktext = weblink.get('link-text', None)
        
    def asmodel(self):
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict: The data model content.
        """
        model = DM()
        model['web-link'] = DM()
        if self.url is not None:
            model['web-link']['URL'] = self.url
        if self.label is not None:
            model['web-link']['label'] = self.label
        if self.linktext is not None:
            model['web-link']['link-text'] = self.linktext
        
        return model

    def html(self):
        """Returns an HTML representation of the object."""
        htmlstr = ''
        if self.label is not None:
            htmlstr += f'{self.label}: '
        htmlstr += f'<a href="{self.url}">{self.linktext}</a>'

        return htmlstr