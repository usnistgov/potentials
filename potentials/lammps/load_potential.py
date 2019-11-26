from pathlib import Path

from .. import rootdir
from . import Potential
from . import get_model
def load_potential(name, pot_dir='database', status='active', database_dir=None):
    """
    Function that creates a lammps.Potential object by loading an existing data
    model.

    """
    model = get_model(name, status=status, database_dir=database_dir)

    if pot_dir == 'database':
        imp_id = model[['potential-LAMMPS', 'id']]
        pot_dir = Path(rootdir, '..', 'data', 'atomman.lammps.Potential models', 'NIST IPR', imp_id).resolve()

    return Potential(model, pot_dir=pot_dir)

