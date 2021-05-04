import sys

from .Database import Database
from ..tools import ModuleManager
databasemanager = ModuleManager('Database')
from .load_database import load_database

__all__ = ['Database', 'databasemanager', 'load_database']

# Import LocalDatabase
try:
    from .LocalDatabase import LocalDatabase
except Exception as e:
    databasemanager.failed_styles['local'] = '%s: %s' % sys.exc_info()[:2]
else:
    databasemanager.loaded_styles['local'] = LocalDatabase
    __all__.append('LocalDatabase')

# Import MongoDatabase
try:
    from .MongoDatabase import MongoDatabase
except Exception as e:
    databasemanager.failed_styles['mongo'] = '%s: %s' % sys.exc_info()[:2]
else:
    databasemanager.loaded_styles['mongo'] = MongoDatabase
    __all__.append('MongoDatabase')

# Import CDCSDatabase
try:
    from .CDCSDatabase import CDCSDatabase
except Exception as e:
    databasemanager.failed_styles['cdcs'] = '%s: %s' % sys.exc_info()[:2]
else:
    databasemanager.loaded_styles['cdcs'] = CDCSDatabase
    __all__.append('CDCSDatabase')

__all__.sort()