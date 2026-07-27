from importlib.metadata import version
__version__ = version('yabadaba')

from . import typing
from . import tools

from .Settings import settings

from . import value

# Import records and load local record styles
from . import record
from .record import recordmanager, load_record

# Import database methods
from .Database import Database, load_database

from . import buildrecord
from .buildrecord import build_lammps_potential

from . import paramfile

__all__ = ['__version__', 'tools', 'settings', 'paramfile', 'value',
           'record', 'load_record', 'recordmanager', 'buildrecord',
           'Database', 'load_database',  'build_lammps_potential',
           'typing']
__all__.sort()
