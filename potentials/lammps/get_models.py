from pathlib import Path

from DataModelDict import DataModelDict as DM

from .. import rootdir
from ..tools import aslist

def get_models(name=None, status='active', database_dir=None):
    """
    Gets all matching lammps.Potential models from a database directory
    based on delimiting keys.

    Parameters
    ----------
    name : str or list, optional
        Potential or implementation ids or keys to identify the data models.
    status : str or None, optional
        Allows for potentials to be limited based on their status.  Allowed
        status values are 'active', 'retracted', and 'superceded'.  If status
        is set to None, all potential versions are explored.  Default value is
        'active'.
    database_dir : Path, optional
        Specifies the directory path for the data model directory.  If not
        given will use the default potentials database path.

    Returns
    -------
    list of DataModelDict.DataModelDict
        The lammps.Potential data models.
    """
    # Set default potentials database path
    if database_dir is None:
        database_dir = Path(rootdir, '..', 'data', 'potential_LAMMPS').resolve()

    if name is not None:
        name = aslist(name)

    models = []
    for modelfile in database_dir.glob('*.json'):
        model = DM(modelfile)
        imp_key = model[['potential-LAMMPS', 'key']]
        imp_id = model[['potential-LAMMPS', 'id']]
        pot_key = model[['potential-LAMMPS', 'potential', 'key']]
        pot_id = model[['potential-LAMMPS', 'potential', 'id']]
        pot_status = model['potential-LAMMPS'].get('status', 'active')

        if name is None or imp_key in name or imp_id in name or pot_key in name or pot_id in name:
            if status is None or status == pot_status:
                models.append(model)
    
    return models

def get_model(name, status='active', database_dir=None):
    """
    Gets exactly one matching lammps.Potential model from a database directory
    based on delimiting keys.

    Parameters
    ----------
    name : str, optional
        A potential or implementation id or key to identify the data model
    status : str or None, optional
        Allows for potentials to be limited based on their status.  Allowed
        status values are 'active', 'retracted', and 'superceded'.  If status
        is set to None, all potential versions are explored.  Default value is
        'active'.
    database_dir : Path, optional
        Specifies the directory path for the data model directory.  If not
        given will use the default potentials database path.

    Returns
    -------
    DataModelDict.DataModelDict
        The lammps.Potential data model.
    
    Raises
    ------
    ValueError if no or multiple matching models are found.
    """

    assert isinstance(name, str), 'Name cannot be a list for get_model'

    models = get_models(name=name, status=status, database_dir=database_dir)
    
    if len(models) == 1:
        return models[0]
    elif len(models) > 0:
        print('Multiple matching implementations found.')
        for i, model in enumerate(models):
            print(i+1, model[['potential-LAMMPS', 'id']])
        i = int(input('Enter selection:')) - 1
        return models[i]
    else:
        raise ValueError('No matching potential models found')