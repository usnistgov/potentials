import datetime

from DataModelDict import DataModelDict as DM 


from .tools import aslist

class System():
    def __init__(self, model=None, formula=None, elements=None):
        if model is not None:
            try:
                assert formula is None
                assert elements is None
            except:
                raise ValueError('model cannot be given with any other arguments')
            self.load(model)
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

    def load(self, model):
        model = DM(model).find('system')
        self.formula = model.get('chemical-formula', None)
        self.elements = model.get('element', None)

    def asmodel(self):
        model = DM()
        model['system'] = DM()
        if self.formula is not None:
            model['system']['chemical-formula'] = self.formula
        if self.elements is not None:
            for element in self.elements:
                model['system'].append('element', element)
        return model

    def asdict(self):
        return {'formula':self.formula, 'elements':self.elements}

    def html(self):
        htmlstr = ''
        if self.formula is not None:
            htmlstr += self.formula
        elif self.elements is not None:
            htmlstr += '-'.join(self.elements)

        return htmlstr
        


class Request():

    def __init__(self, model=None, date=None, comment=None, systems=None):

        if model is not None:
            try:
                assert date is None
                assert comment is None
                assert systems is None
            except:
                raise ValueError('model cannot be given with any other arguments')
            self.load(model)
        else:
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

    def load(self, model):
        model = DM(model).find('request')
        self.date = model['date']
        self.comment = model.get('comment', None)
        self.__systems = []
        for system in model.aslist('system'):
            self.add_system(model=DM([('system',system)]))

    def asmodel(self):
        model = DM()
        model['request'] = DM()
        model['request']['date'] = str(self.date)
        for system in self.systems:
            model['request'].append('system', system.asmodel()['system'])
        if self.comment is not None:
            model['request']['comment'] = self.comment

        return model

    def asdict(self):

        return {'date': self.date,
                'systems': self.systems,
                'comment': self.comment}

    def html(self):
        htmlstr = ''
        htmlsystems = []
        
        for system in self.systems:
            htmlsystems.append(system.html())
        if len(htmlsystems) > 0:
            htmlstr += f'<b>{", ".join(htmlsystems)}</b> '
        
        if self.comment is not None:
            htmlstr += self.comment + ' '
        
        htmlstr += f'({self.date})'

        return htmlstr.strip()


    def add_system(self, model=None, formula=None, elements=None):
        self.systems.append(System(model=model, formula=formula, elements=elements))