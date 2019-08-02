# Standard libraries
import uuid
import datetime

from DataModelDict import DataModelDict as DM

from .Citation import Citation
from .Potential import Potential
from ..tools import aslist

from .Artifact import Artifact
from .Parameter import Parameter
from .WebLink import WebLink



class Implementation():
    """
    Class for representing the implementation portion of Potential metadata
    records.
    """
    def __init__(self, model=None, potential=None, style=None, key=None,
                 id=None, status=None, date=None, notes=None,
                 artifacts=None, parameters=None, weblinks=None):
        """
        Parameters
        ----------
        model
        potential
        style
        key
        id
        status
        date
        notes
        """
        if model is not None:
            # Load existing record
            try:
                assert potential is None
                assert style is None
                assert key is None
                assert id is None
                assert status is None
                assert date is None
                assert notes is None
                assert artifacts is None
                assert parameters is None
                assert weblinks is None
            except:
                raise TypeError('model cannot be given with any other parameter')
            else:
                self.load(model)
        else:
            # Build new record
            self.potential = potential
            self.style = style
            self.key = key
            self.id = id
            self.status = status
            self.date = date
            self.notes = notes
            
            self.artifacts = []
            if artifacts is not None:
                for artifact in aslist(artifacts):
                    self.add_artifact(**artifact)
            
            self.parameters = []
            if parameters is not None:
                for parameter in aslist(parameters):
                    self.add_parameter(**parameter)
            
            self.weblinks = []
            if weblinks is not None:
                for weblink in aslist(weblinks):
                    self.add_weblink(**weblink)

    @property
    def potential(self):
        return self.__potential
    
    @potential.setter
    def potential(self, v):
        if v is None:
            self.__potential = None
        elif isinstance(v, Potential):
            self.__potential = v
        #elif isinstance(v, str):
            #FIND POTENTIAL FROM STR VALUE
        else:
            raise TypeError('Invalid potential type')

    @property
    def style(self):
        return self.__style
    
    @style.setter
    def style(self, v):
        if v is None:
            self.__style = None
        else:
            self.__style = str(v)

    @property
    def key(self):
        return self.__key
    
    @key.setter
    def key(self, v):
        if v is None:
            self.__key = str(uuid.uuid4())
        else:
            self.__key = str(v)
            
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, v):
        if v is None:
            self.__id = None
        else:
            self.__id = str(v)

    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, v):
        if v is None:
            self.__status = 'active'
        else:
            self.__status = str(v)

    @property
    def date(self):
        return self.__date
    
    @date.setter
    def date(self, v):
        if v is None:
            self.__date = datetime.date.today()
        elif isinstance(v, datetime.date):
            self.__date = v
        elif isinstance(v, str):
            self.__date = datetime.datetime.strptime(v, '%Y-%m-%d').date()
        else:
            raise TypeError('Invalid date type')
    
    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, v):
        if v is None:
            self.__notes = None
        else:
            self.__notes = str(v)

    def load(self, model):
        imp = model.find('interatomic-potential-implementation')
        self.key = imp['key']
        self.id = imp.get('id', None)
        self.status = imp['status']
        self.date = imp['date']
        self.style = imp.get('style', None)
        self.notes = imp.get('notes', None)

        self.artifacts = []
        for artifact in imp.iteraslist('artifact'):
            self.add_artifact(model=DM([('artifact', artifact)]))

        self.parameters = []
        for parameter in imp.iteraslist('parameter'):
            self.add_parameter(model=DM([('parameter', parameter)]))

        self.weblinks = []
        for weblink in imp.iteraslist('web-link'):
            self.add_weblink(model=DM([('web-link', weblink)]))

    def build(self):
        """
        """
        model = DM()
        model['interatomic-potential-implementation'] = imp = DM()
        imp['key'] = self.key
        if self.id is not None:
            imp['id'] = self.id
        imp['status'] = self.status
        imp['date'] = str(self.date)
        if self.style is not None:
            imp['style'] = self.style
        if self.notes is not None:
            imp['notes'] = DM([('text', self.notes)])
        for artifact in self.artifacts:
            model.append('artifact', artifact['artifact'])
        for parameter in self.parameters:
            model.append('parameter', parameter['parameter'])
        for weblink in self.weblinks:
            model.append('web-link', weblink['web-link'])

    def add_artifact(self, model=None, filename=None, label=None, url=None):
        self.artifacts.append(Artifact(model=model, filename=filename, label=label, url=url))

    def add_weblink(self, model=None, url=None, label=None, linktext=None):
        self.weblinks.append(WebLink(model=model, url=url, label=label, linktext=linktext))

    def add_parameter(self, model=None, name=None, value=None, unit=None):
        self.artifacts.append(Parameter(model=model, name=name, value=value, unit=unit))
