import datetime

from DataModelDict import DataModelDict as DM

from datamodelbase.record import Record
from datamodelbase import query 

from . import Potential

__all__ = ['Action']

class PotInfo():
    """
    Component class for connecting information from a Potential Record to the
    Action record.
    """
    def __init__(self, potential):
        """
        Builds a PotInfo component class.

        Parameters
        ----------
        potential : Potential, str or DataModelDict
            A Potential record object or DataModelDict contents for a Potential
            record.  This prodives the information to link the Potential to the
            Action.
        """
        if isinstance(potential, Potential):
            
            # Extract relevant properties from the Potential object
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
            
        else:

            # Extract relevant properties from potential record contents
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
    
    @property
    def id(self):
        """str: The Potential's id"""
        return self.__id

    @property
    def key(self):
        """str: The Potential's key"""
        return self.__key

    @property
    def dois(self):
        """list: The Potential's DOIs"""
        return self.__dois

    @property
    def elements(self):
        """list: The elements modeled by the Potential"""
        return self.__elements
    
    @property
    def othername(self):
        """str or None: The Potential's othername"""
        return self.__othername
    
    @property
    def fictional(self):
        """bool: Flag indicating if the Potential is classified as fictional."""
        return self.__fictional

    def build_model(self):
        """
        Generates and returns model content based on the values set to object.
        """
        # Build core elements
        model = DM()
        model['potential'] = DM()
        model['potential']['key'] = self.key
        model['potential']['id'] = self.id
        
        # Append DOIs
        for doi in self.dois:
            model['potential'].append('doi', doi)

        # Add elements or fictional elements
        if self.fictional:
            for element in self.elements:
                model['potential'].append('fictional-element', element)
        else:
            for element in self.elements:
                model['potential'].append('element', element)
        
        # Add othername if set
        if self.othername is not None:
            model['potential']['other-element'] = self.othername

        self._set_model(model)
        return model

    def metadata(self):
        return {'id': self.id,
                'key': self.key,
                'dois': self.dois,
                'elements': self.elements,
                'othername': self.othername,
                'fictional': self.fictional}

class Action(Record):
    """
    Class for representing Action records that document changes to the
    Interatomic Potentials Repository.
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
        date : str or datetime.date, optional
            The date to assign to the record.
        type : str, optional
            The Action type to assign to the record.
        potentials : list, optional
            Potential or model contents for Potential records to associate
            with the action.
        comment : str, optional
            Any additional comments to assign to the record.
        """
        # Set default values
        self.type = 'new posting'
        self.__potentials = []
        self.date = datetime.date.today()
        self.comment = None

        super().__init__(model=model, name=name, **kwargs)

    @property
    def style(self):
        """str: The record style"""
        return 'Action'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'action'
    
    @property
    def xsl_filename(self):
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'Action.xsl')

    @property
    def xsd_filename(self):
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'Action.xsd')

    @property
    def date(self):
        """datetime.date: The date associated with the action."""
        return self.__date

    @date.setter
    def date(self, value):
        if isinstance(value, datetime.date):
            self.__date = value
        else:
            self.__date = datetime.datetime.strptime(value, '%Y-%m-%d').date()

    @property
    def allowedtypes(self):
        """list: The allowed values that the Action's type can be."""
        return ['new posting', 'updated posting', 'retraction', 'site change']

    @property
    def type(self):
        """str: Broad category describing what the Action did."""
        return self.__type

    @type.setter
    def type(self, value):
        value = str(value)
        if value not in self.allowedtypes:
            raise ValueError('Invalid action type')
        self.__type = str(value)

    @property
    def comment(self):
        """str: Any comments further describing the Action."""
        return self.__comment

    @comment.setter
    def comment(self, value):
        if value is None:
            self.__comment = None
        else:
            self.__comment = str(value)

    @property
    def potentials(self):
        """list: Any potentials associated with the action as PotInfo objects"""
        return self.__potentials

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
        act = self.model[self.modelroot]

        self.date = act['date']
        self.type = act['type']
        self.comment = act.get('comment', None)
        self.__potentials = []
        for potential in act.aslist('potential'):
            self.potentials.append(PotInfo(DM([('potential',potential)])))

        if name is not None:
            self.name = name
        else:
            self.build_name()

    def set_values(self, name=None, date=None, type=None, potentials=None,
                   comment=None):
        """
        Set multiple object attributes at the same time.

        Parameters
        ----------
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        date : str or datetime.date, optional
            The date to assign to the record.
        type : str, optional
            The Action type to assign to the record.
        potentials : list, optional
            Potential or model contents for Potential records to associate
            with the action.
        comment : str, optional
            Any additional comments to assign to the record.
        """
        if date is not None:
            self.date = date
        if type is not None:
            self.type = type
        if comment is not None:
            self.comment = comment
        if potentials is not None:
            self.__potentials = []
            for potential in potentials:
                self.potentials.append(PotInfo(potential))

        if name is not None:
            self.name = name
        elif date is not None or comment is not None:
            self.build_name()

    def build_name(self):
        """Builds a name for the record based on date + comment"""
        if self.comment is None:
            self.name = f"{self.date}"
        else:
            self.name = f"{self.date} {self.comment[:90]}"

    def build_model(self):
        """
        Generates and returns model content based on the values set to object.
        """
        # Add Action's date and type
        model = DM()
        model['action'] = DM()
        model['action']['date'] = str(self.date)
        model['action']['type'] = self.type 
        
        # Add any related potentials
        for potential in self.potentials:
            model['action'].append('potential', potential.build_model()['potential'])

        # Add comments
        if self.comment is not None:
            model['action']['comment'] = self.comment

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
        data['type'] = self.type
        data['comment'] = self.comment
        
        data['potentials'] = []
        for pot in self.potentials:
            data['potentials'].append(pot.metadata())
        
        return data

    def pandasfilter(self, dataframe, name=None, date=None, type=None,
                     potential_id=None, potential_key=None, element=None,
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
        type : str or list
            The type of action: 'new posting', 'updated posting', 'retraction',
            or 'site change'.
        potential_id : str or list
            Limits results to entries related to the given potential id.
        potential_key : str or list
            Limits results to entries related to the given potential key.
        element : str or list
            Limits results to entries related to potentials with the given
            element(s).
        comment : str or list
            Term(s) to search for in the action's comment field.
        
        Returns
        -------
        pandas.Series, numpy.NDArray
            Boolean map of matching values
        """
        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.date_match.pandas(dataframe, 'date', date)
            &query.str_match.pandas(dataframe, 'type', type)
            &query.str_match.pandas(dataframe, 'id', potential_id, parent='potentials')
            &query.str_match.pandas(dataframe, 'key', potential_key, parent='potentials')
            &query.in_list.pandas(dataframe, 'element', element, parent='potentials')
            &query.str_contains.pandas(dataframe, 'comment', comment)
        )
        return matches

    def mongoquery(self, name=None, date=None, type=None, potential_id=None,
                   potential_key=None, element=None, comment=None):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        name : str or list
            The record name(s) to parse by.
        date : str or list
            The date associated with the record.
        type : str or list
            The type of action: 'new posting', 'updated posting', 'retraction',
            or 'site change'.
        potential_id : str or list
            Limits results to entries related to the given potential id.
        potential_key : str or list
            Limits results to entries related to the given potential key.
        element : str or list
            Limits results to entries related to potentials with the given
            element(s).
        comment : str or list
            Term(s) to search for in the action's comment field.
        
        Returns
        -------
        dict
            The Mongo-style query
        """        
        mquery = {}
        query.str_match.mongo(mquery, f'name', name)

        root = f'content.{self.modelroot}'
        query.date_match.mongo(mquery, f'{root}.date', date)
        query.str_match.mongo(mquery, f'{root}.type', type)
        query.str_match.mongo(mquery, f'{root}.potential.id', potential_id)
        query.str_match.mongo(mquery, f'{root}.potential.key', potential_key)
        query.in_list.mongo(mquery, f'{root}.potential.element', element)
        query.str_contains.mongo(mquery, f'{root}.comment', comment)
        
        return mquery

    def cdcsquery(self, date=None, type=None, potential_id=None, potential_key=None,
                  element=None, comment=None):
        """
        Builds a CDCS-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        date : str or list
            The date associated with the record.
        type : str or list
            The type of action: 'new posting', 'updated posting', 'retraction',
            or 'site change'.
        potential_id : str or list
            Limits results to entries related to the given potential id.
        potential_key : str or list
            Limits results to entries related to the given potential key.
        element : str or list
            Limits results to entries related to potentials with the given
            element(s).
        comment : str or list
            Term(s) to search for in the action's comment field.
        
        Returns
        -------
        dict
            The CDCS-style query
        """
        
        mquery = {}
        root = self.modelroot
        query.date_match.mongo(mquery, f'{root}.date', date)
        query.str_match.mongo(mquery, f'{root}.type', type)
        query.str_match.mongo(mquery, f'{root}.potential.id', potential_id)
        query.str_match.mongo(mquery, f'{root}.potential.key', potential_key)
        query.in_list.mongo(mquery, f'{root}.potential.element', element)
        query.str_contains.mongo(mquery, f'{root}.comment', comment)
        return mquery