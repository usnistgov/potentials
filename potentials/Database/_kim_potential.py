# coding: utf-8
# Standard Python libraries
from pathlib import Path
import subprocess

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://requests.readthedocs.io/en/master/
import requests

from DataModelDict import DataModelDict as DM

# Local imports
from .. import PotentialLAMMPSKIM
from ..tools import aslist, screen_input
from .. import Settings

def init_installed_kim_models(self, installed_kim_models=None,
                              kim_api_directory=None,
                              kim_settings_file=None):
    """
    Initializes the list of installed kim models.  If any one of the parameters
    are given, then the list will be based on that.  Otherwise, will first
    check the default kim settings file, then the default kim api location.

    Parameters
    ----------
    installed_kim_models : str or list, optional
        Allows for the list of installed_kim_models to be explicitly given.
        Cannot be given with the other parameters.
    kim_api_directory : path-like object, optional
        The directory containing the kim api to use to build the list.
    kim_settings_file : path-like object, optional
        The path to a json file with an 'installed-kim-models' field that lists
        the installed kim models.
    """

    # Directly set list
    if installed_kim_models is not None:
        assert kim_api_directory is None, 'kim_api_directory and installed_kim_models cannot both be given'
        assert kim_settings_file is None, 'installed_kim_models and kim_settings_file cannot both be given'
        self.set_installed_kim_models(installed_kim_models)
    
    # Identify using specified kim api
    elif kim_api_directory is not None:
        assert kim_settings_file is None, 'kim_api_directory and kim_settings_file cannot both be given'
        self.find_installed_kim_models(kim_api_directory)
    
    # Load from specified settings file
    elif kim_settings_file is not None:
        self.load_installed_kim_models(kim_settings_file)
    
    # Load from default settings file
    elif self.default_kim_settings_file.exists():
        self.load_installed_kim_models()

    # Identify using default kim api
    elif Settings().kim_api_directory is not None:
        self.find_installed_kim_models()

    # If all else fails use fire, I mean create empty list
    else:
        self.__installed_kim_models = []

@property
def installed_kim_models(self):
    """list: The full KIM ids of the installed KIM models"""
    return self.__installed_kim_models

@property
def default_kim_settings_file(self):
    """pathlib.Path : The default kim settings file path"""
    return Path(Settings().directory, 'installed_kim_models.json')

def load_kim_lammps_potentials(self, localpath=None, local=None, remote=None,
                               verbose=False):
    """
    Builds PotentialLAMMPSKIM objects based on the installed kim models list
    and the potential_LAMMPS_KIM records in the database.

    Parameters
    ----------
    localpath : str, optional
        Path to a local directory to check for records first.  If not given,
        will check localpath value set during object initialization.  If not
        given or set during initialization, then only the remote database will
        be loaded.
    local : bool, optional
        Indicates if records in localpath are to be loaded.  If not given,
        will use the local value set during initialization.
    remote : bool, optional
        Indicates if the records in the remote database are to be loaded.
        Setting this to be False is useful/faster if a local copy of the
        database exists.  If not given, will use the local value set during
        initialization.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    if verbose:
        print('Building lammps potentials for kim models')

    installed_kim_models = self.installed_kim_models
    
    # Return empty fields if no installed kim models found
    if len(installed_kim_models) == 0:
        if verbose:
            print('No installed kim models identified')
        return []

    # Get potential_LAMMPS_KIM records
    records = self.get_records(template='potential_LAMMPS_KIM', localpath=localpath, local=local, 
                               remote=remote, verbose=verbose)
    
    # Convert to dict
    recorddict = {}
    for record in records:
        recorddict[record['potential-LAMMPS-KIM']['id']] = record
        
    kim_potentials = {}

    for fullid in installed_kim_models:
        if '__MO_' in fullid:
            shortcode = '_'.join(fullid.split('_')[-3:-1])

            if shortcode in recorddict:
                try:
                    kim_potential = PotentialLAMMPSKIM(recorddict[shortcode], fullid)
                    kim_potential.asdict()
                except:
                    if verbose:
                        print(fullid, 'failed to build')
                else:
                    kim_potentials[fullid] = kim_potential
            else:
                if verbose:
                    print(fullid, 'unknown')
    
    if verbose:
        print(f'Loaded {len(kim_potentials)} installed KIM LAMMPS potentials')
        
    return kim_potentials



def find_installed_kim_models(self, kim_api_directory=None):
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
        kim_api_directory = Settings().kim_api_directory
    if kim_api_directory is None:
        raise ValueError('No kim_api_directory given or found in the settings')
    else:
        kim_api_directory = Path(kim_api_directory)
        assert kim_api_directory.is_dir(), 'kim_api_directory does not exist'

    # Build bash commands to list kim api collections
    commands = f'source {kim_api_directory}/bin/kim-api-activate\n'
    commands += 'kim-api-collections-management list'
    
    # Run commands as a subprocess
    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out, err = process.communicate(commands)

    # Parse output to extract installed KIM models
    self.__installed_kim_models = []
    capture = False
    for line in out.split('\n'):
        line = line.strip()
        
        if capture:
            if line == '' or line == '--empty--':
                capture=False
            else:
                self.__installed_kim_models.append(line)
        
        elif 'Portable Models:' in line:
            capture=True

def set_installed_kim_models(self, value):
    """
    Allows for the list of installed KIM models to be directly set.  Useful if
    the kim api is on a different machine or if the list should include models
    associated with different kim api versions.

    Parameters
    ----------
    value : str or list
        The list of installed kim models to use.
    """
    self.__installed_kim_models = aslist(value)

def save_installed_kim_models(self):
    """
    Saves the list of installed kim models so that they can be retrieved later.
    The list of models will be saved in "installed_kim_models.json" in the
    settings directory.
    """
    filename = Path(Settings().directory, 'installed_kim_models.json')
    if filename.is_file():
        print('Installed kim models already saved.')
        option = screen_input('Overwrite? (yes or no):')
        if option.lower() in ['yes', 'y']:
            pass
        elif option.lower() in ['no', 'n']: 
            return None
        else: 
            raise ValueError('Invalid choice')
    
    values = DM()
    values['installed-kim-models'] = self.installed_kim_models
    with open(filename, 'w') as f:
        values.json(fp=f, indent=4)
    

def load_installed_kim_models(self, kim_settings_file=None):
    """
    Loads the list of installed kim models.

    Parameters
    ----------
    kim_settings_file : path-like object, optional
        The path to a json file with an 'installed-kim-models' field that lists
        the installed kim models.  If not given, will access 
        "installed_kim_models.json" in the settings directory.
    """
    if kim_settings_file is None:
        kim_settings_file = self.default_kim_settings_file

    if kim_settings_file.is_file():
        self.set_installed_kim_models(DM(kim_settings_file)['installed-kim-models'])
    else:
        raise ValueError('No installed kim models currently saved')

