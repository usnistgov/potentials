# coding: utf-8

from DataModelDict import DataModelDict as DM

from datamodelbase.record import Record

class Parameter(Record):
    """
    Class for describing parameter values
    """
    def __init__(self, model=None, name=None, value=None, unit=None):
        """
        Initializes a Parameter object to describe parameter values.

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
                self.load_model(model)
        else:
            self.set_values(name=name, value=value, unit=unit)

    @property
    def modelroot(self):
        return 'parameter'

    @property
    def xsl_filename(self):
        return ('potentials.xsl', 'parameter.xsl')

    @property
    def xsd_filename(self):
        return ('potentials.xsd', 'parameter.xsd')


    @property
    def name(self):
        """str: The name of the parameter, or a string parameter line"""
        return self.__name
    
    @name.setter
    def name(self, v):
        if v is None:
            self.__name = None
        else:
            self.__name = str(v)
    
    @property
    def value(self):
        """str or None: The value of the parameter"""
        return self.__value
    
    @value.setter
    def value(self, v):
        if v is None:
            self.__value = None
        else:
            self.__value = float(v)

    @property
    def unit(self):
        """str or None: The unit that the value is in"""
        return self.__unit
    
    @unit.setter
    def unit(self, v):
        if v is None:
            self.__unit = None
        else:
            self.__unit = float(v)

    def set_values(self, name=None, value=None, unit=None):
        """
        Sets a Parameter object's attributes

        Parameters
        ----------
        name : str, optional
            The name of the parameter or string parameter line.
        value : float, optional
            The value of the parameter.
        unit : str, optional
            Units associated with value.
        """
        self.name = name
        self.value = value
        self.unit = unit

    def load_model(self, model):
        """
        Loads the object info from data model content
        
        Parameters
        ----------
        model : str or DataModelDict
            Model content or file path to model content.
        """
        parameter = model.find('parameter')
        self.value = parameter.get('value', None)
        self.unit = parameter.get('unit', None)
        self.name = parameter.get('name', None)
        
    def build_model(self):
        """
        Returns the object info as data model content
        
        Returns
        ----------
        DataModelDict: The data model content.
        """
        model = DM()
        model['parameter'] = DM()
        if self.value is not None:
            model['parameter']['value'] = self.value
        if self.unit is not None:
            model['parameter']['unit'] = self.unit
        if self.name is not None:
            model['parameter']['name'] = self.name
        
        return model

    def metadata(self):
        """Returns a flat dict representation of the object"""
        meta = {}
        meta['value'] = self.value
        meta['unit'] = self.unit
        meta['name'] = self.name

        return meta