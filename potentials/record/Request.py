import datetime

from DataModelDict import DataModelDict as DM 

from datamodelbase.record import Record
from datamodelbase import query 

from ..tools import aslist

modelroot = 'request'

class System():
    def __init__(self, model=None, formula=None, elements=None):
        if model is not None:
            try:
                assert formula is None
                assert elements is None
            except:
                raise ValueError('model cannot be given with any other arguments')
            self.load_model(model)
        else:
            self.formula = formula
            self.elements = elements

    @property
    def formula(self):
        return self.__formula

    @formula.setter
    def formula(self, value):
        if value is None:
            self.__formula = None
        else:
            self.__formula = str(value)

    @property
    def elements(self):
        return self.__elements

    @elements.setter
    def elements(self, value):
        if value is None:
            self.__elements = None
        else:
            self.__elements = aslist(value)

    def load_model(self, model):
        model = DM(model).find('system')
        self.formula = model.get('chemical-formula', None)
        self.elements = model.get('element', None)

    def build_model(self):
        model = DM()
        model['system'] = DM()
        if self.formula is not None:
            model['system']['chemical-formula'] = self.formula
        if self.elements is not None:
            for element in self.elements:
                model['system'].append('element', element)
        return model

    def metadata(self):
        return {
            'formula':self.formula,
            'elements':self.elements}

    #def html(self):
    #    htmlstr = ''
    #    if self.formula is not None:
    #        htmlstr += self.formula
    #    elif self.elements is not None:
    #        htmlstr += '-'.join(self.elements)

    #    return htmlstr
        
class Request(Record):
    
    @property
    def style(self):
        """str: The record style"""
        return 'Request'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return modelroot
    
    @property
    def xsl_filename(self):
        return ('potentials.xsl', 'Request.xsl')

    @property
    def xsd_filename(self):
        return ('potentials.xsd', 'Request.xsd')

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
    def comment(self):
        return self.__comment

    @comment.setter
    def comment(self, value):
        if value is None:
            self.__comment = None
        else:
            self.__comment = str(value)

    @property
    def systems(self):
        return self.__systems

    def set_values(self, name=None, date=None, comment=None, systems=None):
        if date is None:
            date = datetime.date.today()
        self.date = date
        self.comment = comment
        self.__systems = []
        if systems is not None:
            for system in aslist(systems):
                if isinstance(system, System):
                    self.systems.append(system)
                else:
                    self.add_system(**system)

        if name is not None:
            self.name = name
        else:
            elements = []
            for system in self.systems:
                elements.extend(system.elements)
            self.name = f'{self.date} {" ".join(elements)}'

    def load_model(self, model, name=None):
        
        super().load_model(model, name=name)
        req = DM(model).find('request')
        self.date = req['date']
        self.comment = req.get('comment', None)
        self.__systems = []
        for system in req.aslist('system'):
            self.add_system(model=DM([('system',system)]))

        if name is not None:
            self.name = name
        else:
            elements = []
            for system in self.systems:
                elements.extend(system.elements)
            self.name = f'{self.date} {" ".join(elements)}'

    def build_model(self):
        model = DM()
        model['request'] = DM()
        model['request']['date'] = str(self.date)
        for system in self.systems:
            model['request'].append('system', system.build_model()['system'])
        if self.comment is not None:
            model['request']['comment'] = self.comment

        return model

    def metadata(self):
        data = {}
        data['name'] = self.name
        data['date'] = self.date
        data['comment'] = self.comment
        
        data['systems'] = []
        for system in self.systems:
            data['systems'].append(system.metadata())
        
        return data

    #def html(self):
    #    htmlstr = ''
    #    htmlsystems = []
        
    #    for system in self.systems:
    #        htmlsystems.append(system.html())
    #    if len(htmlsystems) > 0:
    #        htmlstr += f'<b>{", ".join(htmlsystems)}</b> '
        
    #    if self.comment is not None:
    #        htmlstr += self.comment + ' '
        
    #    htmlstr += f'({self.date})'

    #    return htmlstr.strip()


    def add_system(self, model=None, formula=None, elements=None):
        self.systems.append(System(model=model, formula=formula, elements=elements))