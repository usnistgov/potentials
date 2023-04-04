# coding: utf-8
# Standard Python libraries
from pathlib import Path
import subprocess
from copy import deepcopy
from typing import Optional, Tuple, Union

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/yabadaba
from yabadaba import load_query

# Local imports
from ..tools import aslist
from .. import settings, load_record

@property
def kim_models(self) -> list:
    """list: The full KIM ids of the installed KIM models"""
    return self.__kim_models

def get_kim_lammps_potentials(self, 
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
    Builds LAMMPS potential entries for KIM models.  The returned entries
    depend both on the parsing parameters and the list of installed kim models
    to consider.  Unless you only want KIM models, use get_lammps_potentials()
    instead.

    Parameters
    ----------
    name : str or list, optional
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list, optional
        The unique UUID4 record key(s) to parse by. 
    id : str or list
        The unique record id(s) labeling the records to parse by.
    potid : str or list, optional
        The unique UUID4 record key(s) for the associated potential records to
        parse by.
    potkey : str or list, optional
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
    kim_models : str or list, optional
        Allows for the list of KIM models to be explicitly given.
    kim_api_directory : path-like object, optional
        The directory containing the kim api to use to build the list.
    kim_models_file : path-like object, optional
        The path to a whitespace-delimited file that lists KIM models.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    local : bool, optional
        Indicates if records in localpath are to be loaded.  If not given,
        will use the local value set during initialization.
    remote : bool, optional
        Indicates if the records in the remote database are to be loaded.
        Setting this to be False is useful/faster if a local copy of the
        database exists.  If not given, will use the local value set during
        initialization.
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
    # Change kim models list if any related parameter is given
    if (kim_models is not None
     or kim_api_directory is not None
     or kim_models_file is not None):
        self.init_kim_models(kim_models=kim_models, kim_api_directory=kim_api_directory,
                             kim_models_file=kim_models_file)
    kim_models = self.kim_models

    # Return empty fields if no kim models found
    if len(kim_models) == 0:
        if verbose:
            print('No KIM potentials added: list of models is empty')
        if return_df:
            return np.array([]), pd.DataFrame({'name':[]})
        else:
            return np.array([])

    # Get potential_LAMMPS_KIM records
    records1, df1 = self.get_records(
        style='potential_LAMMPS_KIM', name=name, local=local, remote=remote,
        refresh_cache=refresh_cache, return_df=True, verbose=verbose,
        key=key, id=id, potid=potid, potkey=potkey, units=units,
        atom_style=atom_style, pair_style=pair_style, status=status,
        symbols=symbols, elements=elements)
    
    # Build list of records based on kim_models and expand potentials
    records2 = []
    df2 = []
    if len(records1) > 0:
        for fullid in kim_models:
            if '__MO_' in fullid:
                shortcode = '_'.join(fullid.split('_')[-3:-1])

                matches = df1[df1.name == shortcode]
                if len(matches) == 1:
                    dbrecord = records1[matches.index.tolist()[0]]
                    record = load_record('potential_LAMMPS_KIM', model=dbrecord.model, id=fullid)

                    # Capture records as is if associated with one potential
                    if len(record.potkeys) == 1:
                        records2.append(record)
                        df2.append(record.metadata())

                    else:
                        # Loop over potential keys
                        for pkey in record.potkeys:
                            record.select_potential(potkey=pkey)

                            # Limit based on search parameters
                            if potkey is not None and record.potkey not in aslist(potkey):
                                continue
                            if potid is not None and record.potid not in aslist(potid):
                                continue
                            if symbols is not None:
                                nomatch = False
                                for symbol in aslist(symbols):
                                    if symbol not in record.symbols:
                                        nomatch = True
                                        break
                                if nomatch:
                                    continue
                            if elements is not None:
                                nomatch = False
                                record_elements = record.elements()
                                for element in aslist(elements):
                                    if element not in record_elements:
                                        nomatch = True
                                        break
                                if nomatch:
                                    continue

                            # Capture copy of the record
                            records2.append(deepcopy(record))
                            df2.append(record.metadata())

    records2 = np.array(records2)
    df2 = pd.DataFrame(df2)

    # Filter by key and id if needed
    if len(records2) > 0:
        matches = (
            load_query('str_match', name='key').pandas(df2, key)
            &load_query('str_match', name='id').pandas(df2, id)
        )
        df2 = df2[matches]
        records2 = records2[matches]
        df2.reset_index(drop=True)

    if verbose:
        print(f'Built {len(records2)} lammps potentials for KIM models')

    if return_df:
        return records2, df2
    else:
        return records2

def init_kim_models(self,
                    kim_models: Union[str, list, None] = None,
                    kim_api_directory: Optional[Path] = None,
                    kim_models_file: Optional[Path] = None):
    """
    Initializes the list of installed kim models.  If any one of the parameters
    are given, then the list will be based on that.  Otherwise, will first
    check the default kim settings file, then the default kim api location.

    Parameters
    ----------
    kim_models : str or list, optional
        Allows for the list of KIM models to be explicitly given.
        Cannot be given with the other parameters.
    kim_api_directory : path-like object, optional
        The directory containing the kim api to use to build the list.
    kim_models_file : path-like object, optional
        The path to a whitespace-delimited file that lists KIM models.
    """

    # Directly set list
    if kim_models is not None:
        assert kim_api_directory is None, 'kim_api_directory and kim_models cannot both be given'
        assert kim_models_file is None, 'kim_models and kim_models_file cannot both be given'
        self.set_kim_models(kim_models)
    
    # Identify using specified kim api
    elif kim_api_directory is not None:
        assert kim_models_file is None, 'kim_api_directory and kim_models_file cannot both be given'
        self.find_kim_models(kim_api_directory)
    
    # Load from specified settings file
    elif kim_models_file is not None:
        self.load_kim_models_file(kim_models_file)
    
    # Load from default settings file
    elif settings.kim_models_file.exists():
        self.load_kim_models_file()

    # Identify using default kim api
    elif settings.kim_api_directory is not None:
        self.find_kim_models()

    # If all else fails use fire, I mean create empty list
    else:
        self.__kim_models = []

def find_kim_models(self, kim_api_directory: Optional[Path] = None):
    """
    Uses the kim api to discover the installed KIM models.

    Parameters
    ----------
    kim_api_directory : path-like object, optional
        The path to the directory associated with the kim api version to
        use to build the list of installed models.
    """
    # Check kim_api_directory values
    if kim_api_directory is None:
        kim_api_directory = settings.kim_api_directory
    if kim_api_directory is None:
        raise ValueError('No kim_api_directory given or found in the settings')
    else:
        kim_api_directory = Path(kim_api_directory)
        assert kim_api_directory.is_dir(), 'kim_api_directory does not exist'

    # Build bash commands to list kim api collections
    commands = f'source {kim_api_directory}/kim-api-activate\n'
    commands += 'kim-api-collections-management list'
    
    # Run commands as a subprocess
    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out = process.communicate(commands)[0]

    # Parse output to extract installed KIM models
    self.__kim_models = []
    capture = False
    for line in out.split('\n'):
        line = line.strip()
        
        if capture:
            if line == '' or line == '--empty--':
                capture=False
            else:
                self.__kim_models.append(line)
        
        elif 'Portable Models:' in line:
            capture=True

def set_kim_models(self, kim_models: Union[str, list]):
    """
    Allows for the list of KIM models to be directly set.  Useful if
    the kim api is on a different machine or if the list should include models
    associated with different kim api versions.

    Parameters
    ----------
    kim_models : str or list
        The list of kim models to use.
    """
    self.__kim_models = aslist(kim_models)

def save_kim_models_file(self, kim_models_file: Optional[Path] = None):
    """
    Saves the current list of kim models so that they can be retrieved later.

    Parameters
    ----------
    kim_models_file : path-like object, optional.
        The path to the file to save the list of kim models to.  If not given,
        will use the default file location in the settings directory.
    """
    settings.set_kim_models(self.kim_models, kim_models_file=kim_models_file)
    
def delete_kim_models_file(self):
    """
    Deletes the default kim models file if it exists.  Deleting the file allows
    for the list of kim models to be built from the default kim-api path, if
    set.
    """
    settings.unset_kim_models()

def load_kim_models_file(self, kim_models_file: Optional[Path] = None):
    """
    Loads the list of kim models from a whitespace-delimited file.

    Parameters
    ----------
    kim_settings_file : path-like object, optional
        The path to a whitespace-delimited file that lists full ids for
        kim models.  If not given, will access "kim_models.txt" in the
        settings directory.
    """
    if kim_models_file is None:
        kim_models_file = settings.kim_models_file
    kim_models_file = Path(kim_models_file)

    if kim_models_file.is_file():
        with open(kim_models_file) as f:
            self.__kim_models = f.read().split()
    else:
        raise ValueError('No kim models currently saved')