# coding: utf-8
# Standard Python libraries
from importlib import resources

# Read version from VERSION file
__version__ = resources.read_text('datamodelbase', 'VERSION').strip()

__all__ = ['__version__', 'tools', 'settings', 'record', 'load_record']
__all__.sort()

# iprPy imports
from . import tools
from .Settings import settings
from . import query

from . import record
from .record import recordmanager, load_record

from . import database
from .database import databasemanager, load_database
