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
from datamodelbase import load_database, databasemanager
from .Database import Database

from . import build
from .build_lammps_potential import build_lammps_potential

__all__ = sorted([
    '__version__', 'tools', 'settings',
    'record', 'load_record', 'recordmanager',
    'load_database', 'databasemanager', 'Database',
    'build', 'build_lammps_potential',
])