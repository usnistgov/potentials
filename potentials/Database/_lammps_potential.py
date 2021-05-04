from .. import settings
from ..tools import aslist
from pathlib import Path
import shutil

import numpy as np
import pandas as pd

from .. import load_record

def get_lammps_potentials(self, local=None, remote=None, 
                          name=None, key=None, id=None,
                          potid=None, potkey=None, units=None,
                          atom_style=None, pair_style=None, status='active',
                          symbols=None, elements=None, pot_dir_style=None,
                          kim_models=None, kim_api_directory=None, kim_models_file=None, 
                          return_df=False, verbose=False):
    """
    Get LAMMPS potential objects for native LAMMPS potentials and openKIM
    models
    
    Parameters
    ----------

    pot_dir_style : str, optional
        Specifies how the pot_dir values will be set for the loaded lammps
        potentials.  Allowed values are 'working', 'id', and 'local'.
        'working' will set all pot_dir = '', meaning parameter files
        are expected in the working directory when the potential is accessed.
        'id' sets the pot_dir values to match the potential's id.
        'local' sets the pot_dir values to the corresponding local database
        paths where the files are expected to be found.  Default value is
        controlled by settings.
    """
    # Check pot_dir_style values
    if pot_dir_style is None:
        pot_dir_style = settings.pot_dir_style
    elif pot_dir_style not in ['working', 'id', 'local']:
        raise ValueError('Invalid pot_dir_style value')
    if pot_dir_style == 'local' and self.local_databse is None:
        raise ValueError('local pot_dir_style requires local_database to be set')

    # Get native LAMMPS potentials
    records, df = self.get_records('potential_LAMMPS', local=local, remote=remote,
                                   name=name, key=key, id=id,
                                   potid=potid, potkey=potkey, units=units,
                                   atom_style=atom_style, pair_style=pair_style, status=status,
                                   symbols=symbols, elements=elements,
                                   return_df=True, verbose=verbose)

    # Set pot_dir values based on pot_dir_style
    if pot_dir_style == 'id':
        for record in records:
            record.pot_dir = record.id
    elif pot_dir_style == 'local':
        for record in records:
            record.pot_dir = Path(self.local_database.host, 'potential_LAMMPS', record.id)

    # Get KIM LAMMPS records
    krecords, kdf = self.get_kim_lammps_potentials(local=local, remote=remote, 
                                                   name=name, key=key, id=id,
                                                   potid=potid, potkey=potkey, units=units,
                                                   atom_style=atom_style, pair_style=pair_style, status=status,
                                                   symbols=symbols, elements=elements, kim_models=kim_models,
                                                   kim_api_directory=kim_api_directory, kim_models_file=kim_models_file, 
                                                   return_df=True, verbose=verbose)

    records = np.hstack([records, krecords])
    df = pd.concat([df, kdf], ignore_index=True, sort=False)

    # Sort by name
    df = df.sort_values('name')
    records = records[df.index.tolist()]

    # Return records (and df)
    if return_df:
        return records, df.reset_index(drop=True)
    else:
        return records

def get_lammps_potential(self, local=None, remote=None, 
                         name=None, key=None, id=None,
                         potid=None, potkey=None, units=None,
                         atom_style=None, pair_style=None, status='active',
                         symbols=None, elements=None, pot_dir_style=None,
                         kim_models=None, kim_api_directory=None, kim_models_file=None, 
                         prompt=True, verbose=False):
    
    # Handle local and remote
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    # Check local first
    if local:
        records = self.get_lammps_potentials(local=True, remote=False, 
                                             name=name, key=key, id=id,
                                             potid=potid, potkey=potkey, units=units,
                                             atom_style=atom_style, pair_style=pair_style, status='active',
                                             symbols=symbols, elements=elements, pot_dir_style=pot_dir_style,
                                             kim_models=kim_models, kim_api_directory=kim_api_directory, kim_models_file=kim_models_file, 
                                             verbose=verbose)
        if len(records) == 1:
            if verbose:
                print('Matching record retrieved from local')
            return records[0]
        
        elif len(records) > 1:
            if prompt:
                print('Multiple matching LAMMPS potentials found')
                for i, record in enumerate(records):
                    print(i+1, record.id)
                index = int(input('Please select one:')) - 1
                return records[index]
            else:
                raise ValueError('Multiple matching records found')
            
    # Check remote next
    if remote:
        records = self.get_lammps_potentials(local=False, remote=True, 
                                             name=name, key=key, id=id,
                                             potid=potid, potkey=potkey, units=units,
                                             atom_style=atom_style, pair_style=pair_style, status='active',
                                             symbols=symbols, elements=elements, pot_dir_style=pot_dir_style,
                                             kim_models=kim_models, kim_api_directory=kim_api_directory, kim_models_file=kim_models_file, 
                                             verbose=verbose)

        if len(records) == 1:
            if verbose:
                print('Matching record retrieved from remote')
            return records[0]
        
        elif len(records) > 1:
            if prompt:
                print('Multiple matching LAMMPS potentials found')
                for i, record in enumerate(records):
                    print(i+1, record.id)
                index = int(input('Please select one:')) - 1
                return records[index]
            else:
                raise ValueError('Multiple matching records found')

        raise ValueError('No matching LAMMPS potentials found')

def download_lammps_potentials(self, name=None, key=None, id=None,
                               potid=None, potkey=None, units=None,
                               atom_style=None, pair_style=None, status=None,
                               symbols=None, elements=None, pot_dir_style=None,
                               include_kim=True, overwrite=False, downloadfiles=False,
                               verbose=False):

    # Test that the respective databases have been set
    if self.local_database is None:
        raise ValueError('local database info not set: initialize with local=True or call set_local_database')
    if self.remote_database is None:
        raise ValueError('remote database info not set: initialize with remote=True or call set_remote_database')
    
    # Get matching remote potential_LAMMPS records
    style = 'potential_LAMMPS'
    records = self.remote_database.get_records(style, name=name, key=key, id=id,
                                               potid=potid, potkey=potkey, units=units,
                                               atom_style=atom_style, pair_style=pair_style, status=status,
                                               symbols=symbols, elements=elements)
    if verbose:
        print(f'Found {len(records)} matching {style} records in remote library')
    
    num_added = 0
    num_changed = 0
    num_skipped = 0
    num_files = 0
    num_files_skipped = 0

    for lammps_potential in records:
        self.save_lammps_potential(lammps_potential, downloadfiles=downloadfiles,
                                   overwrite=overwrite, verbose=verbose)
    
    if verbose:
        print(num_added, 'new records added to local')
        if num_changed > 0:
            print(num_changed, 'existing records changed in local')
        if num_skipped > 0:
            print(num_skipped, 'existing records skipped')

    if include_kim:
        self.download_records('potential_LAMMPS_KIM',
                            name=name, key=key, id=id,
                            potid=potid, potkey=potkey, units=units,
                            atom_style=atom_style, pair_style=pair_style, status=status,
                            symbols=symbols, elements=elements, 
                            overwrite=overwrite, verbose=verbose)

def get_lammps_potential_files(self, lammps_potential, localpath=None,
                               local=None, remote=None, pot_dir=None,
                               verbose=False):
    """
    Retrieves the potential parameter files for a LAMMPS potential and saves
    them to the pot_dir of the potential object.  If local is True and the
    files are already in the localpath, they will be copied from there.  If
    remote is True and no files are found in local, then the files will be
    downloaded.
    
    Parameters
    ----------
    lammps_potential : PotentialLAMMPS
        The LAMMPS potential to retrieve parameter files for.
    local : bool, optional
        Indicates if the parameter files are to be retrieved from the localpath
        if copies exist there.  If not given, will use the local value set
        during initialization.
    remote : bool, optional
        Indicates if the parameter files are to be downloaded if local is False
        or copies are not found in the localpath.  If not given, will use the
        remote value set during initialization.
    pot_dir : path-like object, optional
        The path to the directory where the files are to be saved.  If not
        given, will use whatever pot_dir value was previously set.  If
        given here, will change the pot_dir value so that the pair_info
        lines properly point to the copied/downloaded files.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    # Do nothing for KIM potentials
    if lammps_potential.pair_style == 'kim':
        if verbose:
            print('KIM models have no files to copy')
        return None

    # Set local, and remote as given here or during init
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    # Change or get pot_dir value for the potential
    if pot_dir is not None:
        lammps_potential.pot_dir = pot_dir
    pot_dir = Path(lammps_potential.pot_dir)
    if not pot_dir.is_dir():
        pot_dir.mkdir(parents=True)

    # Check local first
    copied = False
    num_copied = 0
    if local is True:
        local_dir = Path(self.local_database.host, 'potential_LAMMPS', lammps_potential.id)
        if local_dir.is_dir():
            
            # Do nothing if the source and target directories are the same
            if pot_dir == local_dir:
                if verbose:
                    print('No files copied - pot_dir is the local database path for the files')
                return None

            # Copy files from source to target
            for filename in local_dir.glob('*'):
                shutil.copy(filename, pot_dir)
                num_copied += 1
                copied = True
    
    if copied:
        if verbose:
            print(f'{num_copied} files copied')
        return None
    
    # Check remote
    if remote is True and copied is False:
        num_downloaded = lammps_potential.download_files()
        
        if num_downloaded > 0:
            if verbose:
                print(f'{num_downloaded} files downloaded')
            return None
    
    if verbose:
        print(f'No files copied or downloaded')

def upload_lammps_potential(self):
    pass

def save_lammps_potential(self, lammps_potential, name=None, model=None,
                          filenames=None, downloadfiles=False, overwrite=False,
                          verbose=False):
    
    if filenames is not None and downloadfiles is True:
        raise ValueError('Cannot give filenames with downloadfiles=True')
    
    
    if lammps_potential is None:
        lammps_potential = load_record('potential_LAMMPS', model, name=name)
    
    try:
        self.local_database.add_record(record=lammps_potential) 
        if verbose:
            print(f'record {lammps_potential.id} added')
    except:
        if overwrite:
            self.local_database.update_record(record=lammps_potential)
            if verbose:
                print(f'record {lammps_potential.id} updated')
        else:
            if verbose:
                print(f'record {lammps_potential.id} already exists: use overwrite=True to change it')

    if filenames is not None:
        for filename in aslist(filenames):
            newname = Path(self.local_database.host, 'potential_LAMMPS', lammps_potential.id, filename.name)
            if overwrite or not newname.exists():
                shutil.copy(filename, newname)
                if verbose:
                    print(filename.name, 'copied to local database')
            elif verbose:
                print(filename.name, 'already exists: use overwrite=True to change it')

    if downloadfiles:
        pot_dir = Path(self.local_database.host, 'potential_LAMMPS', lammps_potential.id)
        count = lammps_potential.download_files(pot_dir=pot_dir, overwrite=overwrite, verbose=verbose)

def delete_lammps_potential(self):
    pass