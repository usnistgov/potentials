from DataModelDict import DataModelDict as DM

class Parameter():

    def __init__(self, model=None, name=None, value=None, unit=None):
        """
        Initializes a Parameter object to describe potential parameter values.

        Parameters
        ----------
        model : str or DataModelDict.DataModelDict, optional
            Data model content to load.
        name : str, optional
            The name of the parameter or string parameter line.
        value : float, optional
            The value of the parameter.
        unit : str, optional
            Units associated with value.
        """
        if model is not None:
            try:
                assert name is None
                assert value is None
                assert unit is None
            except:
                raise TypeError('model cannot be given with any other parameter')
            else:
                self.load(model)
        else:
            self.name = name
            self.value = value
            self.unit = unit

    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, v):
        if v is None:
            self.__name = None
        else:
            self.__name = str(v)
    
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, v):
        if v is None:
            self.__value = None
        else:
            self.__value = float(v)

    @property
    def unit(self):
        return self.__unit
    
    @unit.setter
    def unit(self, v):
        if v is None:
            self.__unit = None
        else:
            self.__unit = float(v)

    def load(self, model):
        parameter = model.find('parameter')
        self.value = parameter.get('value', None)
        self.unit = parameter.get('unit', None)
        self.name = parameter.get('name', None)
        
    def asmodel(self):
        model = DM()
        model['parameter'] = DM()
        if self.value is not None:
            model['parameter']['value'] = self.value
        if self.unit is not None:
            model['parameter']['unit'] = self.unit
        if self.name is not None:
            model['parameter']['name'] = self.name
        
        return model

    def html(self):
        htmlstr = f'{self.name}'
        if self.value is not None:
            htmlstr += f' {self.value}'
            if self.unit is not None:
                htmlstr += f' {self.unit}'
        
        return htmlstr