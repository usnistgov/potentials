import sys

from datamodelbase.record import Record, load_record, recordmanager
__all__ = ['Record', 'load_record', 'recordmanager']

#### Full record styles - include in recordmanager ####

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

# Import PotentialLAMMPS
try:
    from .PotentialLAMMPS import PotentialLAMMPS
except Exception as e:
    recordmanager.failed_styles['potential_LAMMPS'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['potential_LAMMPS'] = PotentialLAMMPS
    __all__.append('PotentialLAMMPS')

# Import PotentialLAMMPSKIM
try:
    from .PotentialLAMMPSKIM import PotentialLAMMPSKIM
except Exception as e:
    recordmanager.failed_styles['potential_LAMMPS_KIM'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['potential_LAMMPS_KIM'] = PotentialLAMMPSKIM
    __all__.append('PotentialLAMMPSKIM')

# Import Action
try:
    from .Action import Action
except Exception as e:
    recordmanager.failed_styles['Action'] = '%s: %s' % sys.exc_info()[:2]
else:
    recordmanager.loaded_styles['Action'] = Action
    __all__.append('Action')

#### Component record styles - only import for shortcut names ####

# Import Implementation
try:
    from .Implementation import Implementation
except:
    pass

# Import Artifact
try:
    from .Artifact import Artifact
except:
    pass

# Import Parameter
try:
    from .Parameter import Parameter
except:
    pass

# Import Link
try:
    from .Link import Link
except:
    pass

__all__.sort()