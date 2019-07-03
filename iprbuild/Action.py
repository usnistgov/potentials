import datetime

from DataModelDict import DataModelDict as DM

class Action(object):

    def __init__(self, date=None, type='new posting', potentials=None, comment=None):
        self.build(date=date, type=type, potentials=potentials, comment=comment)
    
    def build(self, date=None, type='new posting', potentials=None, comment=None):
        """
        Creates a new Action record describing changes that have been made.
        
        Parameters
        ----------
        date : datetime.date, optional
            The date to assign to the action. If None (default), will assign today's date.
        type : str, optional
            The action type: 'new posting', 'updated posting', 'retraction', or 'site change'.
            Default value is 'new posting'.
        potentials : list of DataModelDict, optional
            Potential record models for potentials associated with the action.
        comment : str, optional
            Comments associated with the action.
        
        Returns
        -------
        DataModelDict
            Data model for the action record.
        """
        
        self.model = DM()
        self.model['action'] = DM()
        
        if date is not None:
            self.date = date
        else:
            self.date = datetime.date.today()
        
        self.type = type 
        
        if potentials is not None:
            for potential in potentials:
                self.append_potential(potential)

        if comment is not None:
            self.comment = comment

    @property
    def date(self):
        return self.model['action']['date']

    @date.setter
    def date(self, value):
        self.model['action']['date'] = str(value)

    @property
    def type(self):
        return self.model['action']['type']

    @type.setter
    def type(self, value):
        allowedtypes = ['new posting', 'updated posting', 'retraction', 'site change']
        if value in allowedtypes:
            self.model['action']['type'] = value 
        else:
            raise ValueError('Invalid action type')

    @property
    def comment(self):
        return self.model['action']['comment']
    
    @comment.setter
    def comment(self, value):
        self.model['action']['comment'] = str(value)
    
    def append_potential(self, potential):
        if 'potential' not in self.model['action'] and 'comment' in self.model['action']:
            reorder = True
        else:
            reorder = False

        potmodel = DM()
        potmodel['key'] = potential.key
        potmodel['id'] = potential.id
        
        try: potmodel['doi'] = potential.model.finds('citation')[0]['DOI']
        except: pass
        
        try: potmodel['element'] = potential.model['interatomic-potential']['element']
        except: pass
        try: potmodel['fictional-element'] = potential.model['interatomic-potential']['fictional-element']
        except: pass
        try: potmodel['other-element'] = potential.model['interatomic-potential']['other-element']
        except: pass
    
        self.model['action'].append('potential', potmodel)

        if reorder:
            self.model['action'].move_to_end('comment')
        