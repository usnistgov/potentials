# coding: utf-8
# Standard Python libraries
from typing import Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record
from yabadaba.tools import iaslist

# Local imports
from . import Potential

__all__ = ['Action']

class PotInfo(Record):
    """
    Component class designed to represent a subset of data from a Potential
    record for inclusion in an Action record.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'PotInfo'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'potential-info'

    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('str', 'potential_key',
                        modelpath='key', metadatakey='key')
        self._add_value('str', 'potential_id',
                        modelpath='id', metadatakey='id')
        self._add_value('strlist', 'dois',
                        modelpath='doi')
        self._add_value('strlist', 'fictionalelements',
                        modelpath='fictional-element')
        self._add_value('strlist', 'elements',
                        modelpath='element')
        self._add_value('str', 'othername',
                        modelpath='other-element')
        
    
    @classmethod
    def from_potential(cls, potential: Union[str, DM, Potential.Potential]):
        """
        Builds a PotInfo component class from a Potential record object

        Parameters
        ----------
        potential : Potential
            A Potential record object.
        """
        
        dois = []
        for citation in potential.citations:
            if citation.doi is not None:
                dois.append(citation.doi)

        return cls(potential_key=potential.key,
                   potential_id=potential.id,
                   dois=dois,
                   fictionalelements=potential.fictionalelements,
                   elements=potential.elements,
                   othername=potential.othername)

class Action(Record):
    """
    Class for representing Action records that document changes to the
    Interatomic Potentials Repository.
    """
    ########################## Basic metadata fields ##########################

    @property
    def style(self) -> str:
        """str: The record style"""
        return 'Action'

    @property
    def modelroot(self) -> str:
        """str: The root element of the content"""
        return 'action'

    @property
    def xsl_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'Action.xsl')

    @property
    def xsd_filename(self) -> Tuple[str, str]:
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'Action.xsd')

    ####################### Define Values and attributes #######################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        
        self._add_value('date', 'date',
                        description='the date of the action')
        self._add_value('str', 'type',
                        allowedvalues=['new posting', 'updated posting',
                                       'retraction', 'site change'],
                        description='the website action type')
        self._add_value('record', 'potentials',
                        recordclass=PotInfo, modelpath='potential')
        self._add_value('longstr', 'comment')

    @property
    def defaultname(self) -> str:
        if self.comment is None:
            return f"{self.date}"
        else:
            return f"{self.date} {self.comment[:90]}"

    def add_potential(self, **kwargs):
        """
        Initializes a new PotInfo object and appends it to the potentials list.
        """
        self.get_value('potentials').append(**kwargs)

    def set_values(self, **kwargs):
        """
        Set multiple object attributes at the same time.

        Parameters
        ----------
        **kwargs: any
            Any parameters for the record that you wish to set values for.
        """
        if 'potentials' in kwargs:
            potentials = []
            for potential in iaslist(kwargs['potentials']):
                if not isinstance(potential, PotInfo):
                    potential = PotInfo.from_potential(potential)
                potentials.append(potential)
            kwargs['potentials'] = potentials

        super().set_values(**kwargs)