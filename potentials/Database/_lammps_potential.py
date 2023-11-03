# coding: utf-8
# Standard libraries
from pathlib import Path
import shutil
import tempfile
from typing import Optional, Tuple, Union

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/yabadaba
from yabadaba.record import Record

# Local imports
from .. import settings

def get_lammps_potentials(self,
                          name: Union[str, list, None] = None,
                          key: Union[str, list, None] = None,
                          id: Union[str, list, None] = None,
                          potid: Union[str, list, None] = None,
                          potkey: Union[str, list, None] = None,
                          units: Union[str, list, None] = None,
                          atom_style: Union[str, list, None] = None,
                          pair_style: Union[str, list, None] = None,
                          status: Union[str, list, None] = None,
                          symbols: Union[str, list, None] = None,
                          elements: Union[str, list, None] = None,
                          pot_dir_style: Optional[str] = None, 
                          kim_models: Union[str, list, None] = None,
                          kim_api_directory: Optional[Path] = None,
                          kim_models_file: Optional[Path] = None, 
                          local: Optional[bool] = None,
                          remote: Optional[bool] = None,
                          refresh_cache: bool = False,
                          return_df: bool = False,
                          verbose: bool = False
                          ) -> Union[np.ndarray, Tuple[np.ndarray, pd.DataFrame]]:
    """
    Gets all matching LAMMPS potentials from the database.

    Parameters
    ----------
    name : str or list, optional
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list, optional
        The unique UUID4 record key(s) to parse by. 
    id : str or list
        The unique record id(s) labeling the records to parse by.
    potkey : str or list, optional
        The unique UUID4 record key(s) for the associated potential records to
        parse by.
    potid : str or list, optional
        The unique record id(s) labeling the associated potential records to
        parse by.
    units : str or list, optional
        LAMMPS units option(s) to parse by.
    atom_style : str or list, optional
        LAMMPS pair_style(s) to parse by.
    pair_style : str or list, optional
        LAMMPS pair_style(s) to parse by.
    status : None, str or list, optional
        Limits the search by the status of the LAMMPS implementations:
        "active", "superseded" and/or "retracted".
    symbols : str or list, optional
        Model symbol(s) to parse by.  Typically correspond to elements for
        atomic potential models.
    elements : str or list, optional
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
    kim_models : list, optional
        A list of full KIM model ids to build LAMMPS potentials for.
    kim_api_directory : str, optional
        The path to the directory containing a kim-api-collections-management
        executable to use to identify which KIM models are installed.
    kim_models_file : str, optional
        The path to a file containing a list of full KIM model ids to build
        LAMMPS potentials for.
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
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
    
    Returns
    -------
    numpy.NDArray of Record subclasses
        The retrived records.
    pandas.DataFrame
        A table of the records' metadata.  Returned if return_df = True.
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
    records, df = self.get_records(
        style='potential_LAMMPS', name=name, local=local, remote=remote,
        refresh_cache=refresh_cache, return_df=True, verbose=verbose,
        key=key, id=id, potid=potid, potkey=potkey, units=units,
        atom_style=atom_style, pair_style=pair_style, status=status,
        symbols=symbols, elements=elements)

    # Set pot_dir values based on pot_dir_style
    if pot_dir_style == 'id':
        for record in records:
            record.pot_dir = record.id
    elif pot_dir_style == 'local':
        for record in records:
            record.pot_dir = Path(self.local_database.host, 'potential_LAMMPS', record.id)

    # Get KIM LAMMPS records
    krecords, kdf = self.get_kim_lammps_potentials(
        name=name, key=key, id=id, potid=potid, potkey=potkey, units=units,
        atom_style=atom_style, pair_style=pair_style, status=status,
        symbols=symbols, elements=elements, kim_models=kim_models,
        kim_api_directory=kim_api_directory, kim_models_file=kim_models_file, 
        local=local, remote=remote, return_df=True,
        refresh_cache=refresh_cache, verbose=verbose)

    # Add KIM LAMMPS records to the lists
    if len(krecords) > 0:
        records = np.hstack([records, krecords])
        df = pd.concat([df, kdf], ignore_index=True, sort=False)

    # Sort by name
    if len(records) > 0:
        df = df.sort_values('name')
        records = records[df.index.tolist()]
        df = df.reset_index(drop=True)

    # Return records (and df)
    if return_df:
        return records, df
    else:
        return records

def promptfxn(df):
    """Generates a prompt list based on id field."""
    
    js = df.sort_values('id').index
    for i, j in enumerate(js):
        print(f"{i+1} {df.loc[j, 'id']} {'-'.join(df.loc[j, 'elements'])}")
    i = int(input('Please select one:')) - 1

    if i < 0 or i >= len(js):
        raise ValueError('Invalid selection')

    return js[i]

def get_lammps_potential(self,
                         name: Union[str, list, None] = None,
                         key: Union[str, list, None] = None,
                         id: Union[str, list, None] = None,
                         potid: Union[str, list, None] = None,
                         potkey: Union[str, list, None] = None,
                         units: Union[str, list, None] = None,
                         atom_style: Union[str, list, None] = None,
                         pair_style: Union[str, list, None] = None,
                         status: Union[str, list, None] = None,
                         symbols: Union[str, list, None] = None,
                         elements: Union[str, list, None] = None,
                         pot_dir_style: Optional[str] = None, 
                         kim_models: Union[str, list, None] = None,
                         kim_api_directory: Optional[Path] = None,
                         kim_models_file: Optional[Path] = None, 
                         local: Optional[bool] = None,
                         remote: Optional[bool] = None, 
                         prompt: bool = True,
                         refresh_cache: bool = False,
                         verbose: bool = False) -> Record:
    """
    Gets a single matching LAMMPS potential from the database.

    Parameters
    ----------
    name : str or list, optional
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list, optional
        The unique UUID4 record key(s) to parse by. 
    id : str or list, optional
        The unique record id(s) labeling the records to parse by.
    potkey : str or list, optional
        The unique UUID4 record key(s) for the associated potential records to
        parse by.
    potid : str or list, optional
        The unique record id(s) labeling the associated potential records to
        parse by.
    units : str or list, optional
        LAMMPS units option(s) to parse by.
    atom_style : str or list, optional
        LAMMPS pair_style(s) to parse by.
    pair_style : str or list, optional
        LAMMPS pair_style(s) to parse by.
    status : None, str or list, optional
        Limits the search by the status of the LAMMPS implementations:
        "active", "superseded" and/or "retracted".
    symbols : str or list, optional
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
    kim_models : list, optional
        A list of full KIM model ids to build LAMMPS potentials for.
    kim_api_directory : str, optional
        The path to the directory containing a kim-api-collections-management
        executable to use to identify which KIM models are installed.
    kim_models_file : str, optional
        The path to a file containing a list of full KIM model ids to build
        LAMMPS potentials for.
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    prompt : bool, optional
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

    # Check local first
    if local:
        records, df = self.get_lammps_potentials(
            name=name, key=key, id=id, potid=potid, potkey=potkey, units=units,
            atom_style=atom_style, pair_style=pair_style, status=status,
            symbols=symbols, elements=elements, pot_dir_style=pot_dir_style,
            kim_models=kim_models, kim_api_directory=kim_api_directory,
            kim_models_file=kim_models_file, local=True, remote=False,
            return_df=True, refresh_cache=refresh_cache, verbose=verbose)

        if len(records) == 1:
            if verbose:
                print('Matching record retrieved from local')
            return records[0]
        
        elif len(records) > 1:
            if prompt:
                print('Multiple matching records retrieved from local')
                index = promptfxn(df)
                return records[index]
            else:
                raise ValueError('Multiple matching records found')
            
    # Check remote next
    if remote:
        records, df = self.get_lammps_potentials(
            name=name, key=key, id=id, potid=potid, potkey=potkey, units=units,
            atom_style=atom_style, pair_style=pair_style, status=status,
            symbols=symbols, elements=elements, pot_dir_style=pot_dir_style,
            kim_models=kim_models, kim_api_directory=kim_api_directory,
            kim_models_file=kim_models_file, local=False, remote=True, 
            return_df=True, verbose=verbose)

        if len(records) == 1:
            if verbose:
                print('Matching record retrieved from remote')
            return records[0]
        
        elif len(records) > 1:
            if prompt:
                print('Multiple matching records retrieved from remote')
                index = promptfxn(df)
                return records[index]
            else:
                raise ValueError('Multiple matching records found')

    raise ValueError('No matching LAMMPS potentials found')

def retrieve_lammps_potential(self,
                              name: Union[str, list, None] = None,
                              dest: Optional[Path] = None,
                              key: Union[str, list, None] = None,
                              id: Union[str, list, None] = None,
                              potid: Union[str, list, None] = None,
                              potkey: Union[str, list, None] = None,
                              units: Union[str, list, None] = None,
                              atom_style: Union[str, list, None] = None,
                              pair_style: Union[str, list, None] = None,
                              status: Union[str, list, None] = None,
                              symbols: Union[str, list, None] = None,
                              elements: Union[str, list, None] = None,
                              pot_dir_style: Optional[str] = None, 
                              kim_models: Union[str, list, None] = None,
                              kim_api_directory: Optional[Path] = None,
                              kim_models_file: Optional[Path] = None, 
                              getfiles: bool = False, 
                              local: Optional[bool] = None,
                              remote: Optional[bool] = None, 
                              prompt: bool = True,
                              format: str = 'json',
                              indent: int = 4, 
                              refresh_cache: bool = False,
                              verbose: bool = False):
    """
    Gets a single matching PotentialLAMMPS or PotentialLAMMPSKIM record from
    the database and saves it to a file based on the record's name.  Any
    associated parameter files can also be downloaded.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    dest : path, optional
        The destination directory where the record is to be saved.  If not
        given will use the current working directory.
    key : str or list
        The unique UUID4 record key(s) to parse by. 
    id : str or list
        The unique record id(s) labeling the records to parse by.
    potkey : str or list, optional
        The unique UUID4 record key(s) for the associated potential records to
        parse by.
    potid : str or list, optional
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
    getfiles : bool, optional
        If True, then the parameter files for the matching potentials
        will also be copied/downloaded to the potential directory.
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    format : str, optional
        The file format to save the record in: 'json' or 'xml'.  Default
        is 'json'.
    indent : int, optional
        The number of space indentation spacings to use in the saved
        record for the different tiered levels.  Default is 4.  Giving None
        will create a compact record.
    prompt : bool
        If prompt=True (default) then a screen input will ask for a selection
        if multiple matching potentials are found.  If prompt=False, then an
        error will be thrown if multiple matches are found.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    # Set default dest
    if dest is None:
        dest = Path.cwd()

    # Get the record
    lmppot = self.get_lammps_potential(
        name=name, key=key, id=id, potid=potid, potkey=potkey, units=units,
        atom_style=atom_style, pair_style=pair_style, status=status,
        symbols=symbols, elements=elements, pot_dir_style=pot_dir_style,
        kim_models=kim_models, kim_api_directory=kim_api_directory,
        kim_models_file=kim_models_file, local=local, remote=remote,
        prompt=prompt, refresh_cache=refresh_cache, verbose=verbose)

    # Save as json
    if format == 'json':
        fname = Path(dest, f'{lmppot.name}.json')
        with open(fname, 'w', encoding='UTF-8') as f:
            lmppot.model.json(fp=f, indent=indent, ensure_ascii=False)
        if verbose:
            print(f'{fname} saved')

    # Save as xml
    elif format == 'xml':
        fname = Path(dest, f'{lmppot.name}.xml')
        with open(fname, 'w', encoding='UTF-8') as f:
            lmppot.model.xml(fp=f, indent=indent)
        if verbose:
            print(f'{fname} saved')

    else:
        raise ValueError('Invalid format: must be json or xml.')

    if getfiles is True:

        # Adjust pot_dir if not absolute
        pot_dir = Path(lmppot.pot_dir)
        if not pot_dir.is_absolute():
            pot_dir = Path(dest, pot_dir)

        # Download parameter files
        self.get_lammps_potential_files(lmppot, local=local, remote=remote,
                                        pot_dir=pot_dir, verbose=verbose)
    
def download_lammps_potentials(self,
                               name: Union[str, list, None] = None,
                               key: Union[str, list, None] = None,
                               id: Union[str, list, None] = None,
                               potid: Union[str, list, None] = None,
                               potkey: Union[str, list, None] = None,
                               units: Union[str, list, None] = None,
                               atom_style: Union[str, list, None] = None,
                               pair_style: Union[str, list, None] = None,
                               status: Union[str, list, None] = None,
                               symbols: Union[str, list, None] = None,
                               elements: Union[str, list, None] = None,
                               include_kim: bool = True,
                               overwrite: bool = False,
                               return_records: bool = False,
                               downloadfiles: bool = False,
                               verbose: bool = False) -> Optional[np.ndarray]:
    """
    Downloads PotentialLAMMPS and PotentialLAMMPSKIM records and any associated
    parameter files from the database.

    Parameters
    ----------
    name : str or list, optional
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list, optional
        The unique UUID4 record key(s) to parse by. 
    id : str or list, optional
        The unique record id(s) labeling the records to parse by.
    potkey : str or list, optional
        The unique UUID4 record key(s) for the associated potential records to
        parse by.
    potid : str or list, optional
        The unique record id(s) labeling the associated potential records to
        parse by.
    units : str or list, optional
        LAMMPS units option(s) to parse by.
    atom_style : str or list, optional
        LAMMPS pair_style(s) to parse by.
    pair_style : str or list, optional
        LAMMPS pair_style(s) to parse by.
    status : None, str or list, optional
        Limits the search by the status of the LAMMPS implementations:
        "active", "superseded" and/or "retracted".
    symbols : str or list, optional
        Model symbol(s) to parse by.  Typically correspond to elements for
        atomic potential models.
    elements : str or list, optional
        Element(s) in the model to parse by.
    include_kim : bool, optional
        If True (default) both PotentialLAMMPS and PotentialLAMMPSKIM records
        will be downloaded.  If False, only PotentialLAMMPS records will be
        downloaded.
    overwrite : bool, optional
        Flag indicating if any existing local records and parameter files with
        names matching remote records and files are updated (True) or left
        unchanged (False).  Default value is False.
    return_records : bool, optional
        If True, the retrieved record objects are also returned.  Default
        value is False.
    downloadfiles : bool, optional
        If True, then any parameter files associated with the potentials will
        also be downloaded.  Default value is False.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """

    # Download and get matching potential_LAMMPS records
    records = self.download_records(
        style='potential_LAMMPS', name=name, overwrite=overwrite,
        return_records=True, verbose=verbose, 
        key=key, id=id, potid=potid, potkey=potkey, units=units,
        atom_style=atom_style, pair_style=pair_style, status=status,
        symbols=symbols, elements=elements)
    
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
                    #tar_name = Path(tmpdirname, f'{pot_id}.tar.gz')
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
        kimrecords = self.download_records(
            style='potential_LAMMPS_KIM', name=name, overwrite=overwrite,
            return_records=return_records, verbose=verbose,
            key=key, id=id, potid=potid, potkey=potkey, units=units,
            atom_style=atom_style, pair_style=pair_style,
            status=status, symbols=symbols, elements=elements)

        if return_records:
            return np.hstack([records, kimrecords])
    
    elif return_records:
        return records

def get_lammps_potential_files(self,
                               lammps_potential: Record,
                               local: Optional[bool] = None,
                               remote: Optional[bool] = None,
                               download: bool = True,
                               pot_dir: Optional[Path] = None,
                               overwrite: bool = False,
                               verbose: bool = False):
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

def save_lammps_potential(self,
                          lammps_potential: Record,
                          filenames: Optional[list] = None,
                          downloadfiles: bool = False,
                          overwrite: bool = False,
                          verbose: bool = False):
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
                    print('files saved to local folder')
            except:
                if overwrite is True:
                    self.local_database.update_folder(record=lammps_potential,
                                                      filenames=filenames, clear=True)
                    if verbose:
                        print('files updated in local folder')
                else:
                    if verbose:
                        print('files skipped as local folder exists')

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
                        print('files saved to local archive')
                except:
                    if overwrite is True:
                        self.local_database.update_tar(record=lammps_potential, root_dir=tmpdirname)
                        if verbose:
                            print('files updated in local archive')
                    else:
                        if verbose:
                            print('files skipped as local archive exists')

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
                        print('files downloaded and saved to local folder')
                except:
                    if overwrite is True:
                        self.local_database.update_folder(record=lammps_potential,
                                                          root_dir=tmpdirname)
                        if verbose:
                            print('files downloaded and updated in local folder')
                    else:
                        if verbose:
                            print('files skipped as local folder exists')
            else:
                try:
                    self.local_database.add_tar(record=lammps_potential, root_dir=tmpdirname)
                    if verbose:
                        print('files downloaded and saved to local archive')
                except:
                    if overwrite is True:
                        self.local_database.update_tar(record=lammps_potential, root_dir=tmpdirname)
                        if verbose:
                            print('files downloaded and updated in local archive')
                    else:
                        if verbose:
                            print('files skipped as local archive exists')

def upload_lammps_potential(self,
                            lammps_potential: Record,
                            workspace: Union[str, pd.Series, None] = None,
                            auto_set_pid_off: bool = False,
                            overwrite: bool = False,
                            verbose: bool = False):
    """
    Uploads a LAMMPS potential to the remote database.
    
    Parameters
    ----------
    lammps_potential : PotentialLAMMPS
        The record to upload.
    workspace : str, optional
        The workspace to assign the record to. If not given, no workspace will
        be assigned (only accessible to user who submitted it).
    auto_set_pid_off : bool, optional
        If True then the CDCS auto_set_pid setting will be turned off during
        the upload and automatically turned back on afterwards.  Use this if
        your records contain PID URL values and you are only uploading one
        entry.  For multiple records with PIDs, manually turn the setting off
        or use the CDCS.auto_set_pid_off() context manager. 
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the remote
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.upload_record(record=lammps_potential, workspace=workspace,
                       auto_set_pid_off=auto_set_pid_off,
                       overwrite=overwrite, verbose=verbose)

def delete_lammps_potential(self,
                            lammps_potential: Record,
                            local: bool = True,
                            remote: bool = False,
                            verbose: bool = False):
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

@property
def bad_lammps_potentials(self) -> list:
    """list: ids of potential_LAMMPS records that are invalid and should fail with LAMMPS"""
    return [
        # Listings with invalid parameter files that do not work in LAMMPS
        '1990--Ackland-G-J--Cu--LAMMPS--ipr1',
        '2009--Zhakhovskii-V-V--Al--LAMMPS--ipr1',
        '2009--Zhakhovskii-V-V--Au--LAMMPS--ipr1',
        '2015--Broqvist-P--Ce-O--LAMMPS--ipr1',

        # Listings with incorrect record info that generates invalid LAMMPS commands
        '2009--Kim-H-K--Fe-Ti-C--LAMMPS--ipr1',
        '2012--Jelinek-B--Al-Si-Mg-Cu-Fe--LAMMPS--ipr1',
        '2013--Gao-H--AgTaO3--LAMMPS--ipr1',
        '2014--Liyanage-L-S-I--Fe-C--LAMMPS--ipr1',
        '2015--Ko-W-S--Ni-Ti--LAMMPS--ipr1',
        '2015--Pascuet-M-I--Al-U--LAMMPS--ipr1',
    ]
