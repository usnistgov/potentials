# Standard libraries
import uuid
import datetime
from pathlib import Path

from DataModelDict import DataModelDict as DM

import requests

from .Citation import Citation
from .Potential import Potential
from ..tools import aslist
from .. import rootdir

from .Artifact import Artifact
from .Parameter import Parameter
from .WebLink import WebLink

class Implementation():
    """
    Class for representing Implementation metadata records.
    records.
    """
    def __init__(self, model=None, potential=None, type=None, key=None,
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
                assert type is None
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
                self.load(model, potential=potential)
        else:
            # Build new record
            self.potential = potential
            self.type = type
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

    def __str__(self):
        return f'Implementation {self.id}'

    @property
    def potential(self):
        return self.__potential
    
    @potential.setter
    def potential(self, v):
        if v is None:
            self.__potential = None
        elif isinstance(v, Potential):
            self.__potential = v
        elif isinstance(v, str):
            self.__potential = Potential.fetch(v)
        else:
            raise TypeError('Invalid potential type')

    @property
    def type(self):
        return self.__type
    
    @type.setter
    def type(self, v):
        if v is None:
            self.__type = None
        else:
            self.__type = str(v)

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

    def html(self, full=True):
        htmlstr = ''
        if full:
            htmlstr += f'{self.potential.html()}<br/>\n'
        
        htmlstr += f'<b>{self.type}</b> ({self.id})<br/>\n'
        if self.status != 'active':
            htmlstr += f'<b>{self.status}</b><br/>\n'
        
        if self.notes is not None:
            htmlstr += f'<b>Notes:</b> {self.notes}</br>\n'
        
        if len(self.artifacts) > 0:
            htmlstr += '<b>Files:</b><br/>\n'
            for artifact in self.artifacts:
                htmlstr += f'{artifact.html()}<br/>\n'
        
        if len(self.parameters) > 0:
            htmlstr += '<b>Parameters:</b><br/>\n'
            for parameter in self.parameters:
                htmlstr += f'{parameter.html()}<br/>\n'
        
        if len(self.weblinks) > 0:
            htmlstr += '<b>Links:</b><br/>\n'
            for weblink in self.weblinks:
                htmlstr += f'{weblink.html()}<br/>\n'
        
        return htmlstr

    @classmethod
    def fetch(cls, key, localdir=None, verbose=True):
        """
        Fetches saved potential content.  First checks localdir, then
        potentials github.

        Parameters
        ----------
        key : str
            The potential key to load.
        localdir : Path, optional
            The local directory for the potential JSON files.  If not given,
            will use the default path in potentials/data/implementation directory.
        """
        if localdir is None:
            localdir = Path(rootdir, '..', 'data', 'implementation')
        localfile = Path(localdir, key, 'meta.json')
        
        if localfile.is_file():
            if verbose:
                print('implementation loaded from localdir')
            return cls(model=localfile)
            
        else:
            r = requests.get(f'https://github.com/usnistgov/potentials/raw/master/data/implementation/{key}/meta.json')
            try:
                r.raise_for_status()
            except:
                raise ValueError(f'no implementation with key {key} found')
            else:
                if verbose:
                    print('implementation downloaded from github')
                return cls(model=r.text)

    def save(self, localdir=None):
        """
        Saves content locally

        Parameters
        ----------
        localdir : Path, optional
            The local directory for the potential JSON files.  If not given,
            will use the default path in potentials/data/implementation directory.
        """
        if localdir is None:
            localdir = Path(rootdir, '..', 'data', 'implementation')
        impdir = Path(localdir, self.key)
        if not impdir.is_dir():
            impdir.mkdir(parents=True)
        localfile = Path(impdir, 'meta.json')

        with open(localfile, 'w', encoding='UTF-8') as f:
            self.asmodel().json(fp=f, indent=4)

    def load(self, model, potential=None):

        model = DM(model)
        imp = model.find('interatomic-potential-implementation')
        self.key = imp['key']
        self.id = imp.get('id', None)
        self.status = imp.get('status', None)
        self.date = imp.get('date', None)
        self.type = imp.get('type', None)
        if 'notes' in imp:
            self.notes = imp['notes']['text']
        else:
            self.notes = None
        
        try:
            pot_key = imp['interatomic-potential-key']
            if potential is not None:
                match = False
                for pot in aslist(potential):
                    if pot.key == pot_key:
                        self.potential = pot
                        match = True
                        break
                if match is False:
                    self.potential = pot_key
        
        except:
            print(f'No pot key {self.id} {self.key}')

        self.artifacts = []
        for artifact in imp.iteraslist('artifact'):
            self.add_artifact(model=DM([('artifact', artifact)]))

        self.parameters = []
        for parameter in imp.iteraslist('parameter'):
            self.add_parameter(model=DM([('parameter', parameter)]))

        self.weblinks = []
        for weblink in imp.iteraslist('web-link'):
            self.add_weblink(model=DM([('web-link', weblink)]))

    def asdict(self):
        """
        Builds flat dictionary representation of the potential.
        """
        data = {}
        
        # Copy class attributes to dict
        data['key'] = self.key
        data['id'] = self.id
        data['date'] = self.date
        data['potential'] = self.potential
        data['status'] = self.status
        data['notes'] = self.notes
        data['type'] = self.type
        data['artifacts'] = self.artifacts
        data['parameters'] = self.parameters
        data['weblinks'] = self.weblinks
        
        return data

    def asmodel(self):
        """
        Builds data model (tree-like JSON/XML) representation for the potential.
        """

        model = DM()
        model['interatomic-potential-implementation'] = imp = DM()
        imp['key'] = self.key
        if self.id is not None:
            imp['id'] = self.id
        imp['status'] = self.status
        imp['date'] = str(self.date)
        imp['interatomic-potential-key'] = self.potential.key
        if self.type is not None:
            imp['type'] = self.type
        if self.notes is not None:
            imp['notes'] = DM([('text', self.notes)])
        for artifact in self.artifacts:
            model.append('artifact', artifact.asmodel()['artifact'])
        for parameter in self.parameters:
            model.append('parameter', parameter.asmodel()['parameter'])
        for weblink in self.weblinks:
            model.append('web-link', weblink.asmodel()['web-link'])
        
        return model

    def add_artifact(self, model=None, filename=None, label=None, url=None):
        self.artifacts.append(Artifact(model=model, filename=filename, label=label, url=url))

    def add_weblink(self, model=None, url=None, label=None, linktext=None):
        self.weblinks.append(WebLink(model=model, url=url, label=label, linktext=linktext))

    def add_parameter(self, model=None, name=None, value=None, unit=None):
        self.parameters.append(Parameter(model=model, name=name, value=value, unit=unit))
