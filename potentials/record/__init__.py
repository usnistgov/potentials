# coding: utf-8

__all__ = ['load_record', 'Record',  'recordmanager']
__all__.sort()

from yabadaba.record import Record, load_record, recordmanager

# Add the modular Record styles
recordmanager.import_style('Citation', '.Citation', __name__)
recordmanager.import_style('Potential', '.Potential', __name__)
recordmanager.import_style('potential_LAMMPS', '.PotentialLAMMPS', __name__)
recordmanager.import_style('potential_LAMMPS_KIM', '.PotentialLAMMPSKIM', __name__)
recordmanager.import_style('Action', '.Action', __name__)
recordmanager.import_style('Request', '.Request', __name__)
recordmanager.import_style('FAQ', '.FAQ', __name__)
