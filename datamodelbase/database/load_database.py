# coding: utf-8

from ..tools import screen_input
from . import databasemanager
from .. import settings as default_settings

__all__ = ['load_database']

def load_database(name=None, style=None, host=None, settings=None, **kwargs):
    """
    Loads a database object.  Can be either loaded from stored settings or
    by defining all needed access information.
    
    Parameters
    ----------
    name : str, optional
        The name assigned to a pre-defined database.  If given, can be the only
        parameter.
    style : str, optional
        The database style to use.
    host : str, optional
        The URL/file path where the database is hosted.
    settings : datamodelbase.Settings, optional
        A Settings object.  Allows for different settings files to be used
        by downstream packages.
    kwargs : dict, optional
        Any other keyword parameters defining necessary access information.
        Allowed keywords are database style-specific.
    
    Returns
    -------
    Subclass of datamodelbase.Database
        The database object.
    """
    
    if settings is None:
        settings = default_settings

    # Create new Database based on parameters
    if style is not None:
        assert name is None, 'name and style cannot both be given'

        return databasemanager.init(style, host=host, **kwargs)

    # Load Database from saved info
    else:
        assert host is None and len(kwargs) == 0, 'style must be given with host, kwargs'

        # Get information from settings file
        database_names = settings.list_databases
        
        # Ask for name if not given
        if name is None:
            if len(database_names) > 0:
                print('Select a database:')
                for i, database in enumerate(database_names):
                    print(i+1, database)
                choice = screen_input(':')
                try:
                    choice = int(choice)
                except:
                    name = choice
                else:
                    name = database_names[choice-1]
            else:
                raise KeyError('No databases currently set')
        
        try:
            kwargs = settings.databases[name]
        except:
            raise ValueError(f'database {name} not found')

        style = kwargs.pop('style')
        return load_database(style=style, **kwargs)
    