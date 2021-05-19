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
                               symbols=None, elements=None, include_kim=True,
                               overwrite=False, downloadfiles=False, verbose=False):
    

    # Download and get matching potential_LAMMPS records
    records = self.download_records('potential_LAMMPS',  
                                    name=name, key=key, id=id, potid=potid, potkey=potkey,
                                    units=units, atom_style=atom_style, pair_style=pair_style,
                                    status=status, symbols=symbols, elements=elements,
                                    return_records=True, overwrite=overwrite, verbose=verbose)
    
    # Download artifacts
    if downloadfiles is True:
        num_downloaded = 0
        num_skipped = 0
        for lammps_potential in records:
            pot_dir = Path(self.local_database.host, 'potential_LAMMPS', lammps_potential.id)
            nd, ns = lammps_potential.download_files(pot_dir=pot_dir, overwrite=overwrite)
            num_downloaded += nd
            num_skipped += ns
        if verbose:
            if num_downloaded > 0:
                print(f'{num_downloaded} parameter files downloaded')
            if num_skipped > 0:
                print(f'{num_skipped} existing parameter files skipped')

    # Download matching potential_LAMMPS_KIM records 
    if include_kim:
        self.download_records('potential_LAMMPS_KIM',
                              name=name, key=key, id=id, potid=potid, potkey=potkey,
                              units=units, atom_style=atom_style, pair_style=pair_style,
                              status=status, symbols=symbols, elements=elements, 
                              overwrite=overwrite, verbose=verbose)

def get_lammps_potential_files(self, lammps_potential, local=None, remote=None,
                               pot_dir=None, overwrite=False, verbose=False):
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
    overwrite : bool, optional
        If False (default), then the files will not be copied/downloaded if
        similarly named files already exist in the pot_dir.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """

    # Set local, and remote as given here or during init
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    artifacts = lammps_potential.artifacts
    if len(artifacts) > 0:
    
        # Change or get pot_dir value for the potential
        if pot_dir is not None:
            lammps_potential.pot_dir = pot_dir
        pot_dir = Path(lammps_potential.pot_dir)
        if not pot_dir.is_dir():
            pot_dir.mkdir(parents=True)

        # Build local_dir path
        if local is True:
            localdir = Path(self.local_database.host, 'potential_LAMMPS', lammps_potential.id)

        # Loop over listed artifacts
        for artifact in artifacts:
            targetname = Path(pot_dir, artifact.filename)

            # Check if target file already exists
            if overwrite or not targetname.exists():
                copied = False

                # Check local first
                if local is True:
                    
                    # Copy from the local if it exists there
                    localname = Path(localdir, artifact.filename)
                    if localname.is_file():
                        shutil.copy(localname, targetname)
                        copied = True
                        if verbose:
                            print(f'{artifact.filename} copied to {pot_dir}')
                
                # Check remote second
                if remote is True and copied is False:
                    artifact.download(pot_dir, overwrite=overwrite, verbose=verbose)
            
            else:
                if verbose:
                    print(f'{artifact.filename} already in {pot_dir}')

def upload_lammps_potential(self, lammps_potential=None, workspace=None,
                            overwrite=False, verbose=False):
    """
    Uploads a LAMMPS potential to the remote database.
    
    Parameters
    ----------
    lammps_potential : PotentialLAMMPS
        The record to upload.
    workspace : str, optional
        The workspace to assign the record to. If not given, no workspace will
        be assigned (only accessible to user who submitted it).
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the remote
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.upload_record(record=lammps_potential, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def save_lammps_potential(self, lammps_potential, filenames=None,
                          downloadfiles=False, overwrite=False,
                          verbose=False):
    """
    Saves a LAMMPS potential to the local.

    Parameters
    ----------
    lammps_potential : PotentialLAMMPS
        The LAMMPS potential to save to the local.
    filenames : list, optional
        A list of file paths for the artifact files to be copied to the local
        location.  Cannot be given with downloadfiles = True.
    downloadfiles : bool, optional
        If True, then the artifacts associated with the LAMMPS potential
        will be downloaded to the local.  Cannot be True if filenames is given.
    overwrite : bool, optional
        If False (default), then any existing records/artifacts will be
        skipped.  If True, then the existing contents will be replaced.
    verbose : bool, optional
        If True, informational print statements will be generated.

    Returns
    -------
    added : int
        Number of artifacts copied/downloaded to the local location.
    skipped : int 
        Number of artifacts not copied/downloaded to the local location.
    """

    # Check for conflicting parameters
    if filenames is not None and downloadfiles is True:
        raise ValueError('Cannot give filenames with downloadfiles=True')
    
    self.save_record(record=lammps_potential, overwrite=overwrite,
                     verbose=verbose)
    
    if filenames is not None:
        pot_dir = Path(self.local_database.host, 'potential_LAMMPS', lammps_potential.id)
        if not pot_dir.is_dir():
            pot_dir.mkdir(parents=True)
        
        for filename in aslist(filenames):
            added = 0
            skipped = 0
            newname = Path(pot_dir, filename.name)
            if overwrite or not newname.exists():
                shutil.copy(filename, newname)
                added += 1
                if verbose:
                    print(f'{filename.name} copied to {pot_dir}')
            else:
                skipped += 1
                if verbose:
                    print(f'{filename.name} already in {pot_dir}')

    elif downloadfiles:
        pot_dir = Path(self.local_database.host, 'potential_LAMMPS', lammps_potential.id)
        added, skipped = lammps_potential.download_files(pot_dir=pot_dir,
                                                         overwrite=overwrite,
                                                         verbose=verbose)

def delete_lammps_potential(self, lammps_potential, local=True, remote=False,
                            localfiles=False, verbose=False):
    """ 
    Deletes a LAMMPS potential record from the local and/or remote locations.

    Parameters
    ----------
    lammps_potential : PotentialLAMMPS
        The LAMMPS potential to delete.
    local : bool, optional
        Indicates if the record will be deleted from the local location.
        Deleting the record also deletes the associated parameter files.
        Default value is True.
    remote : bool, optional
        Indicates if the record will be deleted from the remote location.
        Default value is False.  If True, requires an account for the remote
        location with write permissions.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    # Delete the record
    self.delete_record(record=lammps_potential, local=local, remote=remote,
                       verbose=verbose)
    
    # Delete the parameter files
    if local is True:
        pot_dir = Path(self.local_database.host, 'potential_LAMMPS', lammps_potential.id)
        shutil.rmtree(pot_dir)