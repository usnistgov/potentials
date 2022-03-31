# coding: utf-8
import datetime

from DataModelDict import DataModelDict as DM 

from yabadaba.record import Record
from yabadaba import load_query 

from ..tools import aslist

class System():
    """
    Component class for representing an elemental system being requested.
    """
    def __init__(self, model=None, formula=None, elements=None):
        """
        Class initializer.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            The contents of the record associated with the system info.
        formula : str, optional
            A specific chemical formula being requested.
        elements : list, optional
            A set of elements for the elemental system being requested.
        """
        if model is not None:
            try:
                assert formula is None
                assert elements is None
            except AssertionError as e:
                raise ValueError('model cannot be given with any other arguments') from e
            self.load_model(model)
        else:
            self.formula = formula
            self.elements = elements

    @property
    def formula(self):
        """str : A specific chemical formula being requested."""
        return self.__formula

    @formula.setter
    def formula(self, value):
        if value is None:
            self.__formula = None
        else:
            self.__formula = str(value)

    @property
    def elements(self):
        """list : A combination of elements being requested."""
        return self.__elements

    @elements.setter
    def elements(self, value):
        if value is None:
            self.__elements = []
        else:
            self.__elements = aslist(value)

    def load_model(self, model):
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        """
        model = DM(model).find('system')
        self.formula = model.get('chemical-formula', None)
        self.elements = model.get('element', None)

    def build_model(self):
        """
        Generates and returns model content based on the values set to object.
        """
        model = DM()
        model['system'] = DM()
        if self.formula is not None:
            model['system']['chemical-formula'] = self.formula
        if self.elements is not None:
            for element in self.elements:
                model['system'].append('element', element)
        return model

    def metadata(self):
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        return {
            'formula':self.formula,
            'elements':self.elements}

class Request(Record):
    """
    Class for representing Request records that are associated with user
    requests to the NIST Interatomic Potentials Repository for new potentials.
    """
    def __init__(self, model=None, name=None, **kwargs):
        """
        Initializes a Record object for a given style.
        
        Parameters
        ----------
        model : str, file-like object, DataModelDict
            The contents of the record.
        name : str, optional
            The unique name to assign to the record.  If model is a file
            path, then the default record name is the file name without
            extension.
        date : datetime.date, optional
            The date the request was made.
        comment : str, optional
            Any additional comments for the request, often what type of study
            the requested potential is wanted for.
        systems : list, optional
            The System component objects or associated content to describe
            the elemental system being requested.
        """
        # Set default values
        self.__systems = []
        self.date = datetime.date.today()
        self.comment = None

        super().__init__(model=model, name=name, **kwargs)

    @property
    def style(self):
        """str: The record style"""
        return 'Request'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'request'
    
    @property
    def xsl_filename(self):
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'Request.xsl')

    @property
    def xsd_filename(self):
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'Request.xsd')

    @property
    def date(self):
        """datetime.date : The date that the request was submitted."""
        return self.__date

    @date.setter
    def date(self, value):
        if isinstance(value, datetime.date):
            self.__date = value
        else:
            self.__date = datetime.datetime.strptime(value, '%Y-%m-%d').date()

    @property
    def comment(self):
        """str: Any additional comments associated with the request."""
        return self.__comment

    @comment.setter
    def comment(self, value):
        if value is None:
            self.__comment = None
        else:
            self.__comment = str(value)

    @property
    def systems(self):
        """list: The System component objects associated with the request."""
        return self.__systems

    def set_values(self, name=None, date=None, comment=None, systems=None):
        """
        Set multiple object attributes at the same time.
        
        Parameters
        ----------
        name : str, optional
            The unique name to assign to the record.  If model is a file
            path, then the default record name is the file name without
            extension.
        date : datetime.date, optional
            The date the request was made.
        comment : str, optional
            Any additional comments for the request, often what type of study
            the requested potential is wanted for.
        systems : list, optional
            The System component objects or associated content to describe
            the elemental system being requested.
        """
        
        if date is not None:
            self.date = date
        if comment is not None:
            self.comment = comment
        if systems is not None:
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
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
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
        """
        Generates and returns model content based on the values set to object.
        """
        model = DM()
        model['request'] = DM()
        model['request']['date'] = str(self.date)
        for system in self.systems:
            model['request'].append('system', system.build_model()['system'])
        if self.comment is not None:
            model['request']['comment'] = self.comment

        self._set_model(model)
        return model

    def metadata(self):
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        data = {}
        data['name'] = self.name
        data['date'] = self.date
        data['comment'] = self.comment
        
        data['systems'] = []
        for system in self.systems:
            data['systems'].append(system.metadata())
        
        return data

    def add_system(self, model=None, formula=None, elements=None):
        """
        Initializes a System component class and appends it to the systems list.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            The contents of the record associated with the system info.
        formula : str, optional
            A specific chemical formula being requested.
        elements : list, optional
            A set of elements for the elemental system being requested.
        """
        self.systems.append(System(model=model, formula=formula, elements=elements))

    @property
    def queries(self):
        """dict: Query objects and their associated parameter names."""
        return {
            'date': load_query(
                style='date_match',
                name='date', 
                path=f'{self.modelroot}.date'),
            'element': load_query(
                style='list_contains',
                name='elements', parent='systems',
                path=f'{self.modelroot}.system.element'),
            'comment': load_query(
                style='str_contains',
                name='comment',
                path=f'{self.modelroot}.comment'),
        }

    def pandasfilter(self, dataframe, name=None, date=None, element=None,
                     comment=None):
        """
        Filters a pandas.DataFrame based on kwargs values for the record style.
        
        Parameters
        ----------
        dataframe : pandas.DataFrame
            A table of metadata for multiple records of the record style.
        name : str or list
            The record name(s) to parse by.
        date : str or list
            The date associated with the record.
        element : str or list
            Element(s) to search for in the request.
        comment : str or list
            Term(s) to search for in the action's comment field.
        
        Returns
        -------
        pandas.Series, numpy.NDArray
            Boolean map of matching values
        """
        matches = super().pandasfilter(dataframe, name=name, date=date,
                                       element=element, comment=comment)

        return matches

    def mongoquery(self, name=None, date=None,  element=None, comment=None):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        name : str or list
            The record name(s) to parse by.
        date : str or list
            The date associated with the record.
        element : str or list
            Element(s) to search for in the request.
        comment : str or list
            Term(s) to search for in the action's comment field.
        
        Returns
        -------
        dict
            The Mongo-style query
        """     
        mquery = super().mongoquery(name=name, date=date,
                                    element=element, comment=comment)
        return mquery

    def cdcsquery(self, date=None,  element=None, comment=None):
        """
        Builds a CDCS-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        date : str or list
            The date associated with the record.
        element : str or list
            Element(s) to search for in the request.
        comment : str or list
            Term(s) to search for in the action's comment field.
        
        Returns
        -------
        dict
            The CDCS-style query
        """
        mquery = super().cdcsquery(date=date,
                                   element=element, comment=comment)
        return mquery