from .. import settings
from ..tools import aslist
from pathlib import Path
import shutil
import tempfile

import numpy as np
import pandas as pd

from .. import load_record

def get_lammps_potentials(self, local=None, remote=None, 
                          name=None, key=None, id=None,
                          potid=None, potkey=None, units=None,
                          atom_style=None, pair_style=None, status='active',
                          symbols=None, elements=None, pot_dir_style=None,
                          kim_models=None, kim_api_directory=None, kim_models_file=None, 
                          refresh_cache=False, return_df=False, verbose=False):
    """
    Retrieves all matching LAMMPS potentials from the database.

    Parameters
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    name : str or list
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list
        The unique UUID4 record key(s) to parse by. 
    id : str or list
        The unique record id(s) labeling the records to parse by.
    potid : str or list
        The unique UUID4 record key(s) for the associated potential records to
        parse by.
    potkey : str or list
        The unique record id(s) labeling the associated potential records to
        parse by.
    units : str or list
        LAMMPS units option(s) to parse by.
    atom_style : str or list
        LAMMPS pair_style(s) to parse by.
    pair_style : str or list
        LAMMPS pair_style(s) to parse by.
    status : None, str or list
        Limits the search by the status of the LAMMPS implementations:
        "active", "superseded" and/or "retracted".  By default, only active
        implementations are returned.  Giving a value of None will return
        implementations of all statuses.
    symbols : str or list
        Model symbol(s) to parse by.  Typically correspond to elements for
        atomic potential models.
    elements : str or list
        Element(s) in the model to parse by.
    pot_dir_style : str, optional
        Specifies how the pot_dir values will be set for the retrieved LAMMPS
        potentials.  Allowed values are 'working', 'id', and 'local'.
        'working' will set all pot_dir = '', meaning parameter files
        are expected in the working directory when the potential is accessed.
        'id' sets the pot_dir values to match the potential's id.
        'local' sets the pot_dir values to the corresponding local database
        paths where the files are expected to be found.  Default value is
        controlled by settings.
    kim_models : list
        A list of full KIM model ids to build LAMMPS potentials for.
    kim_api_directory : str
        The path to the directory containing a kim-api-collections-management
        executable to use to identify which KIM models are installed.
    kim_models_file : str
        The path to a file containing a list of full KIM model ids to build
        LAMMPS potentials for.
    refresh_cache : bool, optional
        If the local database is of style "local", indicates if the metadata
        cache file is to be refreshed.  If False,
        metadata for new records will be added but the old record metadata
        fields will not be updated.  If True, then the metadata for all
        records will be regenerated, which is needed to update the metadata
        for modified records.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    # Check pot_dir_style values
    if pot_dir_style is None:
        pot_dir_style = settings.pot_dir_style
    elif pot_dir_style not in ['working', 'id', 'local']:
        raise ValueError('Invalid pot_dir_style value')
    if pot_dir_style == 'local':
        if self.local_database is None or self.local_database.style != 'local':
            raise ValueError("pot_dir_style 'local' requires local_database to be set and of style local")

    # Get native LAMMPS potentials
    records, df = self.get_records('potential_LAMMPS', local=local, remote=remote,
                                   name=name, key=key, id=id,
                                   potid=potid, potkey=potkey, units=units,
                                   atom_style=atom_style, pair_style=pair_style, status=status,
                                   symbols=symbols, elements=elements, refresh_cache=refresh_cache,
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
                                                   return_df=True, refresh_cache=refresh_cache, verbose=verbose)

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
                         prompt=True, refresh_cache=False, verbose=False):
    """
    Retrieves a single matching LAMMPS potential from the database.

    Parameters
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    name : str or list
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list
        The unique UUID4 record key(s) to parse by. 
    id : str or list
        The unique record id(s) labeling the records to parse by.
    potid : str or list
        The unique UUID4 record key(s) for the associated potential records to
        parse by.
    potkey : str or list
        The unique record id(s) labeling the associated potential records to
        parse by.
    units : str or list
        LAMMPS units option(s) to parse by.
    atom_style : str or list
        LAMMPS pair_style(s) to parse by.
    pair_style : str or list
        LAMMPS pair_style(s) to parse by.
    status : None, str or list
        Limits the search by the status of the LAMMPS implementations:
        "active", "superseded" and/or "retracted".  By default, only active
        implementations are returned.  Giving a value of None will return
        implementations of all statuses.
    symbols : str or list
        Model symbol(s) to parse by.  Typically correspond to elements for
        atomic potential models.
    elements : str or list
        Element(s) in the model to parse by.
    pot_dir_style : str, optional
        Specifies how the pot_dir values will be set for the retrieved LAMMPS
        potentials.  Allowed values are 'working', 'id', and 'local'.
        'working' will set all pot_dir = '', meaning parameter files
        are expected in the working directory when the potential is accessed.
        'id' sets the pot_dir values to match the potential's id.
        'local' sets the pot_dir values to the corresponding local database
        paths where the files are expected to be found.  Default value is
        controlled by settings.
    kim_models : list
        A list of full KIM model ids to build LAMMPS potentials for.
    kim_api_directory : str
        The path to the directory containing a kim-api-collections-management
        executable to use to identify which KIM models are installed.
    kim_models_file : str
        The path to a file containing a list of full KIM model ids to build
        LAMMPS potentials for.
    prompt : bool
        If prompt=True (default) then a screen input will ask for a selection
        if multiple matching potentials are found.  If prompt=False, then an
        error will be thrown if multiple matches are found.
    refresh_cache : bool, optional
        If the local database is of style "local", indicates if the metadata
        cache file is to be refreshed.  If False,
        metadata for new records will be added but the old record metadata
        fields will not be updated.  If True, then the metadata for all
        records will be regenerated, which is needed to update the metadata
        for modified records.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """

    # Handle local and remote
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    def promptfxn(df):
        """Generates a prompt list based on id field."""
        key = 'id'
        
        js = df.sort_values(key).index
        for i, j in enumerate(js):
            print(i+1, df.loc[j, key])
        i = int(input('Please select one:')) - 1

        if i < 0 or i >= len(js):
            raise ValueError('Invalid selection')

        return js[i]

    # Check local first
    if local:
        records, df = self.get_lammps_potentials(local=True, remote=False, 
                                             name=name, key=key, id=id,
                                             potid=potid, potkey=potkey, units=units,
                                             atom_style=atom_style, pair_style=pair_style, status='active',
                                             symbols=symbols, elements=elements, pot_dir_style=pot_dir_style,
                                             kim_models=kim_models, kim_api_directory=kim_api_directory, kim_models_file=kim_models_file, 
                                             return_df=True, refresh_cache=refresh_cache, verbose=verbose)
        if len(records) == 1:
            if verbose:
                print('Matching record retrieved from local')
            return records[0]
        
        elif len(records) > 1:
            if prompt:
                print('Multiple matching record retrieved from local')
                index = promptfxn(df)
                return records[index]
            else:
                raise ValueError('Multiple matching records found')
            
    # Check remote next
    if remote:
        records, df = self.get_lammps_potentials(local=False, remote=True, 
                                             name=name, key=key, id=id,
                                             potid=potid, potkey=potkey, units=units,
                                             atom_style=atom_style, pair_style=pair_style, status='active',
                                             symbols=symbols, elements=elements, pot_dir_style=pot_dir_style,
                                             kim_models=kim_models, kim_api_directory=kim_api_directory, kim_models_file=kim_models_file, 
                                             return_df=True, verbose=verbose)

        if len(records) == 1:
            if verbose:
                print('Matching record retrieved from remote')
            return records[0]
        
        elif len(records) > 1:
            if prompt:
                print('Multiple matching record retrieved from remote')
                index = promptfxn(df)
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

        if self.local_database.style == 'local':
            # Download directly to local style database
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
        
        else:
            # Download and then archive to other database styles
            with tempfile.TemporaryDirectory() as tmpdirname:
                for lammps_potential in records:
                    pot_id = lammps_potential.id
                    pot_dir = Path(tmpdirname, pot_id)
                    tar_name = Path(tmpdirname, f'{pot_id}.tar.gz')
                    lammps_potential.download_files(pot_dir=pot_dir)
                    try:
                        self.local_database.add_tar(record=lammps_potential, root_dir=tmpdirname)
                        num_downloaded += 1
                    except:
                        if overwrite is True:
                            self.local_database.update_tar(record=lammps_potential, root_dir=tmpdirname)
                            num_downloaded += 1
                        else:
                            num_skipped += 1
            if verbose:
                if num_downloaded > 0:
                    print(f'{num_downloaded} potentials had parameter files added')
                if num_skipped > 0:
                    print(f'{num_skipped} potentials were skipped for already having parameter files')

    # Download matching potential_LAMMPS_KIM records 
    if include_kim:
        self.download_records('potential_LAMMPS_KIM',
                              name=name, key=key, id=id, potid=potid, potkey=potkey,
                              units=units, atom_style=atom_style, pair_style=pair_style,
                              status=status, symbols=symbols, elements=elements, 
                              overwrite=overwrite, verbose=verbose)

def get_lammps_potential_files(self, lammps_potential, local=None, remote=None,
                               download=True, pot_dir=None, overwrite=False,
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
        Indicates if the parameter files are to be retrieved from the local
        if copies exist there.  If not given, will use the local value set
        during initialization.
    remote : bool, optional
        Indicates if the parameter files are to be retrieved from the remote
        if copies exist there and are not found in local.  If not given, will
        use the remote value set during initialization.
    download : bool, optional
        Indicates if the parameter files are to be downloaded from their urls
        if copies are not found in local or remote.  Default value is True.
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

        dirpath = None
        tar = None
        
        # Check if local has folder or tar for the potential
        if local is True:
            try:
                dirpath = self.local_database.get_folder(record=lammps_potential)
            except:
                try:
                    tar = self.local_database.get_tar(record=lammps_potential)
                except:
                    pass

        # Check if remote has folder or tar for the potential
        if remote is True and dirpath is None and tar is None:
            try:
                dirpath = self.remote_database.get_folder(record=lammps_potential)
            except:
                try:
                    tar = self.remote_database.get_tar(record=lammps_potential)
                except:
                    pass

        # Loop over listed artifacts
        for artifact in artifacts:
            dest_name = Path(pot_dir, artifact.filename)

            # Check if destination file already exists
            if overwrite is True or not dest_name.exists():
                copied = False

                # Check dirpath
                if dirpath is not None:
                    
                    # Copy from the local if it exists there
                    source_name = Path(dirpath, artifact.filename)
                    if source_name.is_file():
                        shutil.copy2(source_name, dest_name)
                        copied = True
                        if verbose:
                            print(f'{artifact.filename} copied to {pot_dir}')
                    else:
                        if verbose:
                            print(f'{artifact.filename} missing from database folder')

                # Check tar
                if tar is not None:
                    try:
                        fr = tar.extractfile(f'{lammps_potential.id}/{artifact.filename}')
                    except:
                        if verbose:
                            print(f'{artifact.filename} missing from database archive')
                    else:
                        with open(dest_name, 'wb') as fw:
                            fw.write(fr.read())
                        fr.close()
                        copied = True
                        if verbose:
                            print(f'{artifact.filename} copied to {pot_dir}')    

                # Download using the artifact's url
                if download is True and copied is False:
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

        # Add files to local-style databases
        if self.local_database.style == 'local':
            try:
                self.local_database.add_folder(record=lammps_potential,
                                               filenames=filenames)
                if verbose:
                    print(f'files saved to local folder')
            except:
                if overwrite is True:
                    self.local_database.update_folder(record=lammps_potential,
                                                      filenames=filenames, clear=True)
                    if verbose:
                        print(f'files updated in local folder')
                else:
                    if verbose:
                        print(f'files skipped as local folder exists')

        # Add files to other database styles
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                
                # Copy files to tmpdir
                pot_id = lammps_potential.id
                pot_dir = Path(tmpdirname, pot_id)
                pot_dir.mkdir()
                for filename in filenames:
                    shutil.copy2(filename, pot_dir)
                
                try:
                    self.local_database.add_tar(record=lammps_potential, root_dir=tmpdirname)
                    if verbose:
                        print(f'files saved to local archive')
                except:
                    if overwrite is True:
                        self.local_database.update_tar(record=lammps_potential, root_dir=tmpdirname)
                        if verbose:
                            print(f'files updated in local archive')
                    else:
                        if verbose:
                            print(f'files skipped as local archive exists')

    elif downloadfiles:
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            
            # Download files to tmpdir
            pot_id = lammps_potential.id
            pot_dir = Path(tmpdirname, pot_id)
            lammps_potential.download_files(pot_dir=pot_dir)

            # Add files to local style
            if self.local_database.style == 'local':
                try:
                    self.local_database.add_folder(record=lammps_potential,
                                                   root_dir=tmpdirname)
                    if verbose:
                        print(f'files downloaded and saved to local folder')
                except:
                    if overwrite is True:
                        self.local_database.update_folder(record=lammps_potential,
                                                          root_dir=tmpdirname)
                        if verbose:
                            print(f'files downloaded and updated in local folder')
                    else:
                        if verbose:
                            print(f'files skipped as local folder exists')
            else:
                try:
                    self.local_database.add_tar(record=lammps_potential, root_dir=tmpdirname)
                    if verbose:
                        print(f'files downloaded and saved to local archive')
                except:
                    if overwrite is True:
                        self.local_database.update_tar(record=lammps_potential, root_dir=tmpdirname)
                        if verbose:
                            print(f'files downloaded and updated in local archive')
                    else:
                        if verbose:
                            print(f'files skipped as local archive exists')
                
def delete_lammps_potential(self, lammps_potential, local=True, remote=False,
                            verbose=False):
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