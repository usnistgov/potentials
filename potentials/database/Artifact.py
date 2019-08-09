from DataModelDict import DataModelDict as DM

class Artifact():

    def __init__(self, model=None, filename=None, label=None, url=None):
        """
        Initializes an Artifact object to describe a file stored in the
        potentials github repository.

        Parameters
        ----------
        filename : str
            The name of the file without path information.
        label : str, optional
            A short description label.
        url : str, optional
            URL for file where downloaded, if available.
        """
        if model is not None:
            try:
                assert filename is None
                assert label is None
                assert url is None
            except:
                raise TypeError('model cannot be given with any other parameter')
            else:
                self.load(model)
        else:
            self.filename = filename
            self.label = label
            self.url = url

    def __str__(self):
        return f'Artifact {self.filename}'

    @property
    def filename(self):
        return self.__filename
    
    @filename.setter
    def filename(self, v):
        if v is None:
            self.__filename = None
        else:
            self.__filename = str(v)

    @property
    def label(self):
        return self.__label
    
    @label.setter
    def label(self, v):
        if v is None:
            self.__label = None
        else:
            self.__label = str(v)
    
    @property
    def url(self):
        return self.__url
    
    @url.setter
    def url(self, v):
        if v is None:
            self.__url = None
        else:
            self.__url = str(v)

    def load(self, model):
        artifact = model.find('artifact')
        self.url = artifact['web-link'].get('URL', None)
        self.label = artifact['web-link'].get('label', None)
        self.filename = artifact['web-link'].get('link-text', None)
        
    def asmodel(self):
        model = DM()
        model['artifact'] = DM()
        model['artifact']['web-link'] = DM()
        if self.url is not None:
            model['artifact']['web-link']['URL'] = self.url
        if self.label is not None:
            model['artifact']['web-link']['label'] = self.label
        if self.filename is not None:
            model['artifact']['web-link']['link-text'] = self.filename
        
        return model

    def html(self):
        htmlstr = ''
        if self.label is not None:
            htmlstr += f'{self.label}: '
        if self.url is not None:
            htmlstr += f'<a href="{self.url}">{self.filename}</a>'
        else:
            htmlstr += f'{self.filename}'
        
        return htmlstr