import sys

from datamodelbase.record import Record, load_record, recordmanager
__all__ = ['Record', 'load_record', 'recordmanager']


# Import Citation
try:
    from .Citation import Citation
except Exception as e:
    recordmanager.failed_styles['Citation'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['Citation'] = Citation
    __all__.append('Citation')

# Import Potential
try:
    from .Potential import Potential
except Exception as e:
    recordmanager.failed_styles['Potential'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['Potential'] = Potential
    __all__.append('Potential')

__all__.sort()

# Import PotentialLAMMPS
try:
    from .PotentialLAMMPS import PotentialLAMMPS
except Exception as e:
    recordmanager.failed_styles['potential_LAMMPS'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['potential_LAMMPS'] = PotentialLAMMPS
    __all__.append('PotentialLAMMPS')

__all__.sort()

# Import PotentialLAMMPSKIM
try:
    from .PotentialLAMMPSKIM import PotentialLAMMPSKIM
except Exception as e:
    recordmanager.failed_styles['potential_LAMMPS_KIM'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['potential_LAMMPS_KIM'] = PotentialLAMMPSKIM
    __all__.append('PotentialLAMMPSKIM')

__all__.sort()