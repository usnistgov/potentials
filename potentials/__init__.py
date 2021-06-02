# coding: utf-8
# Standard Python libraries
from importlib import resources

# Read version from VERSION file
__version__ = resources.read_text('potentials', 'VERSION').strip()

from . import tools
from .Settings import settings


# Import records and load local record styles
from . import record
from .record import recordmanager, load_record

# Import database methods
#from datamodelbase import databasemanager
from .Database import Database, load_database

from . import buildrecord
from .buildrecord import build_lammps_potential

from . import paramfile

__all__ = sorted([
    '__version__', 'tools', 'settings',
    'record', 'load_record', 'recordmanager',
    'Database', 'load_database', 'buildrecord', 'build_lammps_potential',
])