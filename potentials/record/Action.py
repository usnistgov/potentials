import datetime

from DataModelDict import DataModelDict as DM

from datamodelbase.record import Record
from datamodelbase import query 

from . import Potential

modelroot = 'action'

__all__ = ['Action']

class PotInfo():
    def __init__(self, potential):

        if isinstance(potential, Potential):
            self.__id = potential.id
            self.__key = potential.key
            self.__dois = []
            for citation in potential.citations:
                try:
                    self.__dois.append(citation.doi)
                except:
                    pass
            self.__fictional = potential.fictional
            self.__elements = potential.elements
            self.__othername = potential.othername
            
        elif isinstance(potential, DM):
            model = DM(potential).find('potential')
            self.__id = model['id']
            self.__key = model['key']
            self.__dois = model.aslist('doi')

            felements = model.aslist('fictional-element')
            oelements = model.aslist('other-element')
            elements = model.aslist('element')
            
            if len(felements) > 0:
                assert len(elements) == 0
                self.__fictional = True
                self.__elements = felements
            else:
                assert len(elements) > 0
                self.__fictional = False
                self.__elements = elements
            if len(oelements) > 0:
                assert len(oelements) == 1
                self.__othername = oelements[0]
            else:
                self.__othername = None

        else:
            raise TypeError('Invalid potential content')
    
    @property
    def id(self):
        return self.__id

    @property
    def key(self):
        return self.__key

    @property
    def dois(self):
        return self.__dois

    @property
    def elements(self):
        return self.__elements
    
    @property
    def othername(self):
        return self.__othername
    
    @property
    def fictional(self):
        return self.__fictional
    
    #def html(self):
    #    return f'<a href="https://www.ctcms.nist.gov/potentials/entry/{self.id}">{self.id}</a>'

    def build_model(self):
        model = DM()
        model['potential'] = DM()
        model['potential']['key'] = self.key
        model['potential']['id'] = self.id
        for doi in self.dois:
            model['potential'].append('doi', doi)

        if self.fictional:
            for element in self.elements:
                model['potential'].append('fictional-element', element)
        else:
            for element in self.elements:
                model['potential'].append('element', element)
        if self.othername is not None:
            model['potential']['other-element'] = self.othername

        return model

    def metadata(self):
        return {'id': self.id,
                'key': self.key,
                'dois': self.dois,
                'elements': self.elements,
                'othername': self.othername,
                'fictional': self.fictional}

class Action(Record):

    @property
    def style(self):
        """str: The record style"""
        return 'Action'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return modelroot
    
    @property
    def xsl_filename(self):
        return ('potentials.xsl', 'Action.xsl')

    @property
    def xsd_filename(self):
        return ('potentials.xsd', 'Action.xsd')

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, value):
        if isinstance(value, datetime.date):
            self.__date = value
        else:
            self.__date = datetime.datetime.strptime(value, '%Y-%m-%d').date()

    @property
    def allowedtypes(self):
        return ['new posting', 'updated posting', 'retraction', 'site change']

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        value = str(value)
        if value not in self.allowedtypes:
            raise ValueError('Invalid action type')
        self.__type = str(value)

    @property
    def comment(self):
        return self.__comment

    @comment.setter
    def comment(self, value):
        if value is None:
            self.__comment = None
        else:
            self.__comment = str(value)

    @property
    def potentials(self):
        return self.__potentials

    def load_model(self, model, name=None):

        super().load_model(model, name=name)
        act = self.model[modelroot]

        self.date = act['date']
        self.type = act['type']
        self.comment = act.get('comment', None)
        self.__potentials = []
        for potential in act.aslist('potential'):
            self.potentials.append(PotInfo(DM([('potential',potential)])))

        if name is not None:
            self.name = name
        else:
            self.name = f"{self.date} {self.comment[:90]}"

    def set_values(self, name=None, date=None, type=None, potentials=None,
                   comment=None):
        if date is None:
            date = datetime.date.today()
        self.date = date
        self.type = type
        self.comment = comment
        self.__potentials = []
        for potential in potentials:
            self.potentials.append(PotInfo(potential))

        if name is not None:
            self.name = name
        else:
            self.name = f"{self.date} {self.comment[:90]}"

    def build_model(self):
        
        model = DM()
        model['action'] = DM()
        model['action']['date'] = str(self.date)
        model['action']['type'] = self.type 
        
        for potential in self.potentials:
            model['action'].append('potential', potential.build_model()['potential'])

        if self.comment is not None:
            model['action']['comment'] = self.comment

        return model

    def metadata(self):
        data = {}
        data['name'] = self.name
        data['date'] = self.date
        data['type'] = self.type
        data['comment'] = self.comment
        
        data['potentials'] = []
        for pot in self.potentials:
            data['potentials'].append(pot.metadata())
        
        return data

    #def html(self):
    #    htmlstr = ''
    #    htmlstr += f'<b>{self.type} ({self.date})</b>'
    #    if self.comment is not None:
    #        htmlstr += ' ' + self.comment
    #    for potential in self.potentials:
    #        htmlstr += '\n<br/>' + potential.html()
    #    return htmlstr