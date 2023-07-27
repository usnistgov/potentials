# coding: utf-8
# Standard Python libraries
from importlib import resources

# Read version from VERSION file
if hasattr(resources, 'files'):
    __version__ = resources.files('potentials').joinpath('VERSION').read_text(encoding='UTF-8')
else:
    __version__ = resources.read_text('potentials', 'VERSION', encoding='UTF-8').strip()

from . import tools
from .Settings import settings

# Import records and load local record styles
from . import record
from .record import recordmanager, load_record

# Import database methods
from .Database import Database, load_database

from . import buildrecord
from .buildrecord import build_lammps_potential

from . import paramfile

__all__ = ['__version__', 'tools', 'settings', 'paramfile',
           'record', 'load_record', 'recordmanager', 'buildrecord',
           'Database', 'load_database',  'build_lammps_potential',]
__all__.sort()
