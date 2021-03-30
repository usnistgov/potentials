# coding: utf-8
# Standard Python libraries
from pathlib import Path
import shutil

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://requests.readthedocs.io/en/master/
import requests

from DataModelDict import DataModelDict as DM

# Local imports
from .. import PotentialLAMMPS
from ..tools import aslist
from ..build import PotentialLAMMPSBuilder

@property
def lammps_potentials(self):
    return self.__lammps_potentials

@property
def lammps_potentials_df(self):
    return self.__lammps_potentials_df

def _no_load_lammps_potentials(self):
    self.__lammps_potentials = None
    self.__lammps_potentials_df = None

def load_lammps_potentials(self, localpath=None, local=None, remote=None,
                           pot_dir_style='working', status='active', verbose=False):
    """
    Loads LAMMPS potentials from the database, first checking localpath, then
    trying to download from host.
    
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
    pot_dir_style : str, optional
        Specifies how the pot_dir values will be set for the loaded lammps
        potentials.  Allowed values are 'working', 'id', and 'local'.
        'working' (default) will set all pot_dir = '', meaning parameter files
        are expected in the working directory when the potential is accessed.
        'id' sets the pot_dir values to match the potential's id.
        'local' sets the pot_dir values to the corresponding local database
        paths where the files are expected to be found.
    status : str, list or None, optional
        Only potential_LAMMPS records with the given status(es) will be
        loaded.  Allowed values are 'active' (default), 'superseded', and
        'retracted'.  If None is given, then all potentials will be loaded.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    potentials = {}
    localloaded = 0

    # Set localpath, local, and remote as given here or during init
    if localpath is None:
        localpath = self.localpath
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote

    # Check pot_dir_style values
    if pot_dir_style not in ['working', 'id', 'local']:
        raise ValueError('Invalid pot_dir_style value')
    if pot_dir_style == 'local' and localpath is None:
        raise ValueError('local pot_dir_style requires localpath to be set')

    # Check localpath first
    if local is True and localpath is not None:

        if status is not None:
            status = aslist(status)

        for potfile in Path(localpath, 'potential_LAMMPS').glob('*'):
            if potfile.suffix in ['.xml', '.json']:
                lammps_potential = PotentialLAMMPS(potfile)
                if status is None or lammps_potential.status in status:
                    potentials[potfile.stem] = lammps_potential

        if verbose:
            localloaded = len(potentials)
            print(f'Loaded {localloaded} local LAMMPS potentials')
    
    # Load remote
    if remote is True:
        
        # Add status query
        mquery = {}
        if status is not None:
            status = aslist(status)
            if 'active' in status:
                status.append(None)
            mquery['potential-LAMMPS.status'] = {'$in':status}

        try:
            records = self.cdcs.query(template='potential_LAMMPS',
                                      mongoquery=mquery)
        except:
            if verbose:
                print('Failed to load LAMMPS potentials from remote')
        else:
            if verbose:
                print(f'Loaded {len(records)} remote LAMMPS potentials')
            for i in range(len(records)):
                record = records.iloc[i]
                if record.title not in potentials:
                    potentials[record.title] = PotentialLAMMPS(record.xml_content)

            if verbose and localloaded > 0:
                print(f' - {len(potentials) - localloaded} new')
    
    # Build and append kim models
    kim_potentials = self.load_kim_lammps_potentials(localpath=localpath, local=local,
                                                remote=remote, verbose=verbose)
    potentials.update(kim_potentials)

    # Build lammps_potentials and lammps_potentials_df
    if len(potentials) > 0:
        pots = np.array(list(potentials.values()))
        potdicts = []
        for pot in pots:
            potdicts.append(pot.asdict())
            
            # Set pot_dir values based on pot_dir_style
            if pot.pair_style != 'kim':
                if pot_dir_style == 'id':
                    pot.pot_dir = pot.id
                elif pot_dir_style == 'local':
                    pot.pot_dir = Path(localpath, 'potential_LAMMPS', pot.id)

        self.__lammps_potentials_df = pd.DataFrame(potdicts).sort_values('id')
        self.__lammps_potentials = pots[self.lammps_potentials_df.index]
        self.__lammps_potentials_df.reset_index(drop=True)

    else:
        if verbose:
            print('No LAMMPS potentials loaded')
        self.__lammps_potentials = None
        self.__lammps_potentials_df = None

def get_lammps_potentials(self, id=None, key=None, potid=None, potkey=None,
                          status='active', pair_style=None, elements=None,
                          symbols=None, verbose=False, pot_dir_style=None,
                          forceremote=False):
    """
    Gets LAMMPS potentials from the loaded values or by downloading from
    potentials.nist.gov if local copies are not found.
    
    Parameters
    ----------
    id : str or list, optional
        The id value(s) to limit the search by.
    key : str or list, optional
        The key value(s) to limit the search by.
    potid : str or list, optional
        The potid value(s) to limit the search by.
    potkey : str or list, optional
        The potkey value(s) to limit the search by.
    status : str or list, optional
        The status value(s) to limit the search by.
    pair_style : str or list, optional
        The pair_style value(s) to limit the search by.
    elements : str or list, optional
        The included element(s) to limit the search by.
    symbols : str or list, optional
        The included symbol model(s) to limit the search by.
    verbose: bool, optional
        If True, informative print statements will be used.
    pot_dir_style : str or None, optional
        If given, will modify the pot_dir values of all returned potentials
        to correspond with one of the following styles.
        'working' (default) will set all pot_dir = '', meaning parameter files
        are expected in the working directory when the potential is accessed.
        'id' sets the pot_dir values to match the potential's id.
        'local' sets the pot_dir values to the corresponding local database
        paths where the files are expected to be found.
    forceremote : bool, optional
        If True, then files will be searched from the remote database
        regardless of if lammps_potentials have been loaded.

    Returns
    -------
    list
        The matching PotentialLAMMPS objects.
    """
    # Check pot_dir_style values
    if pot_dir_style is not None and pot_dir_style not in ['working', 'id', 'local']:
        raise ValueError('Invalid pot_dir_style value')
    if pot_dir_style == 'local' and self.localpath is None:
        raise ValueError('local pot_dir_style requires localpath to be set')

    # Check loaded values if available
    if self.lammps_potentials_df is not None and forceremote is False:
        
        def valmatch(series, val, key):
            if val is None:
                return True
            else:
                return series[key] in aslist(val)
        
        def listmatch(series, val, key):
            if val is None:
                return True
            
            elif isinstance(series[key], list):
                for v in aslist(val):
                    if v not in series[key]:
                        return False
                return True
            else:
                return False
        
        pots = self.lammps_potentials
        potsdf = self.lammps_potentials_df
        lammps_potentials = pots[potsdf.apply(valmatch, args=[id, 'id'], axis=1)
                         &potsdf.apply(valmatch, args=[key, 'key'], axis=1)
                         &potsdf.apply(valmatch, args=[potid, 'potid'], axis=1)
                         &potsdf.apply(valmatch, args=[potkey, 'potkey'], axis=1)
                         &potsdf.apply(valmatch, args=[status, 'status'], axis=1)
                         &potsdf.apply(valmatch, args=[pair_style, 'pair_style'], axis=1)
                         &potsdf.apply(listmatch, args=[elements, 'elements'], axis=1)
                         &potsdf.apply(listmatch, args=[symbols, 'symbols'], axis=1)]
        if verbose:
            print(len(lammps_potentials), 'matching LAMMPS potentials found from loaded records')

    # Check remote values if no loaded values
    else:
        # Build Mongoquery
        mquery = {}

        # Add id query
        if id is not None:
            id = aslist(id)
            mquery['potential-LAMMPS.id'] = {'$in': id}

        # Add key query
        if key is not None:
            key = aslist(key)
            mquery['potential-LAMMPS.key'] = {'$in': key}

        # Add potid query
        if potid is not None:
            potid = aslist(potid)
            mquery['potential-LAMMPS.potential.id'] = {'$in': potid}
        
        # Add potkey query
        if potkey is not None:
            potkey = aslist(potkey)
            mquery['potential-LAMMPS.potential.key'] = {'$in': potkey}

        # Add status query
        if status is not None:
            status = aslist(status)
            if 'active' in status:
                status.append(None)
            mquery['potential-LAMMPS.status'] = {'$in':status}

        # Add pair_style query
        if pair_style is not None:
            pair_style = aslist(pair_style)
            mquery['potential-LAMMPS.pair_style.type'] = {'$in': pair_style}
        
        # Add elements query
        if elements is not None:
            elements = aslist(elements)
            mquery['potential-LAMMPS.atom.element'] = {'$all': elements}

        # Add symbols query
        if symbols is not None:
            symbols = aslist(symbols)
            mquery['$or'] = []
            # Check symbols
            mquery['$or'].append({'potential-LAMMPS.atom.symbol': {'$all': symbols}})
            # if symbols not in model, check elements
            mquery['$or'].append({'potential-LAMMPS.atom.symbol': {'$exists': False},
                                'potential-LAMMPS.atom.element':{'$all': symbols}})

        matches = self.cdcs.query(template='potential_LAMMPS', mongoquery=mquery)
        if len(matches) > 0:
            matches = matches.sort_values('title').reset_index(drop=True)
        def makepotentials(series):
            return PotentialLAMMPS(model=series.xml_content)

        if verbose:
            print(len(matches), 'matching LAMMPS potentials found from remote database')
        lammps_potentials = matches.apply(makepotentials, axis=1)

    if pot_dir_style is not None:
        if pot_dir_style == 'working':
            for lammps_potential in lammps_potentials:
                lammps_potential.pot_dir = ''
        elif pot_dir_style == 'id':
            for lammps_potential in lammps_potentials:
                lammps_potential.pot_dir = lammps_potential.id
        elif pot_dir_style == 'local':
            for lammps_potential in lammps_potentials:
                lammps_potential.pot_dir = Path(self.localpath, 'potential_LAMMPS', lammps_potential.id)

    return lammps_potentials

def get_lammps_potential(self, id=None, key=None, potid=None, potkey=None,
                         status='active', pair_style=None, elements=None,
                         symbols=None, pot_dir_style=None, verbose=False,
                         forceremote=False):
    """
    Gets a LAMMPS potential from the localpath or by downloading from
    potentials.nist.gov if a local copy is not found.  Will raise an error
    if none or multiple matching potentials are found.
    
    Parameters
    ----------
    id : str or list, optional
        The id value(s) to limit the search by.
    key : str or list, optional
        The key value(s) to limit the search by.
    potid : str or list, optional
        The potid value(s) to limit the search by.
    potkey : str or list, optional
        The potkey value(s) to limit the search by.
    status : str or list, optional
        The status value(s) to limit the search by.
    pair_style : str or list, optional
        The pair_style value(s) to limit the search by.
    elements : str or list, optional
        The included elemental model(s) to limit the search by.
    symbols : str or list, optional
        The included symbol model(s) to limit the search by.
    pot_dir_style : str or None, optional
        If given, will modify the pot_dir values of the returned potentials
        to correspond with one of the following styles.
        'working' (default) will set all pot_dir = '', meaning parameter files
        are expected in the working directory when the potential is accessed.
        'id' sets the pot_dir values to match the potential's id.
        'local' sets the pot_dir values to the corresponding local database
        paths where the files are expected to be found.
    verbose: bool, optional
        If True, informative print statements will be used.
    forceremote : bool, optional
        If True, then files will be searched from the remote database
        regardless of if lammps_potentials have been loaded.

    Returns
    -------
    Potential.LAMMPSPotential
        The potential object to use.
    """
    # Check pot_dir_style values
    if pot_dir_style is not None and pot_dir_style not in ['working', 'id', 'local']:
        raise ValueError('Invalid pot_dir_style value')
    if pot_dir_style == 'local' and self.localpath is None:
        raise ValueError('local pot_dir_style requires localpath to be set')

    lammps_potentials = self.get_lammps_potentials(id=id, key=key, potid=potid,
                                                   potkey=potkey, status=status,
                                                   pair_style=pair_style, elements=elements,
                                                   symbols=symbols, verbose=verbose,
                                                   pot_dir_style=None,
                                                   forceremote=forceremote)
                         
    if len(lammps_potentials) == 1:
        lammps_potential = lammps_potentials[0]
    elif len(lammps_potentials) == 0:
        raise ValueError('No matching LAMMPS potentials found')
    else:
        raise ValueError('Multiple matching LAMMPS potentials found')
    
    if pot_dir_style is not None:
        if pot_dir_style == 'working':
            lammps_potential.pot_dir = ''
        elif pot_dir_style == 'id':
            lammps_potential.pot_dir = lammps_potential.id
        elif pot_dir_style == 'local':
            lammps_potential.pot_dir = Path(self.localpath, 'potential_LAMMPS', lammps_potential.id)

    return lammps_potential

def download_lammps_potentials(self, id=None, key=None, potid=None, potkey=None,
                               status='active', pair_style=None, elements=None,
                               symbols=None, verbose=False, localpath=None,
                               format='xml', indent=None,
                               downloadfiles=False, overwrite=True, reload=False):
    """
    Download potential_LAMMPS records from the remote and save to localpath.
    
    Parameters
    ----------
    id : str or list, optional
        The id value(s) to limit the search by.
    key : str or list, optional
        The key value(s) to limit the search by.
    potid : str or list, optional
        The potid value(s) to limit the search by.
    potkey : str or list, optional
        The potkey value(s) to limit the search by.
    status : str or list, optional
        The status value(s) to limit the search by.
    pair_style : str or list, optional
        The pair_style value(s) to limit the search by.
    elements : str or list, optional
        The included element(s) to limit the search by.
    symbols : str or list, optional
        The included symbol model(s) to limit the search by.
    verbose: bool, optional
        If True, informative print statements will be used.
    localpath : path-like object, optional
        Path to a local directory where the files will be saved to.  If not
        given, will use the localpath value set during object initialization.
    format : str, optional
        The file format to save the record files as.  Allowed values are 'xml'
        (default) and 'json'.
    indent : int, optional
        The indentation spacing size to use for the locally saved record files.
        If not given, the JSON/XML content will be compact.
    downloadfiles : bool, optional
        If True, the parameter files associated with the potential_LAMMPS
        record will also be downloaded.
    overwrite : bool, optional
        If True (default) then any matching LAMMPS potentials already in the
        localpath will be updated if the content has changed.  If False, all
        existing LAMMPS potentials in the localpath will be unchanged.
    reload : bool, optional
        If True, will call load_lammps_potentials() after adding the new
        potential.  Default value is False: loading is slow and should only be
        done when you wish to retrieve the saved potentials.
    """
    
    # Fetch matching lammps potentials from the remote
    lammps_potentials = self.get_lammps_potentials(id=id, key=key, potid=potid,
                                                   potkey=potkey, status=status,
                                                   pair_style=pair_style, elements=elements,
                                                   symbols=symbols, verbose=verbose,
                                                   forceremote=True)

    # Save the potentials to the localpath
    self.save_lammps_potentials(lammps_potentials, downloadfiles=downloadfiles,
                                format=format, localpath=localpath,
                                indent=indent, overwrite=overwrite,
                                verbose=verbose, reload=reload)

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
    localpath : path-like object, optional
        Path to a local directory where the files will be searched for.  If not
        given, will use the localpath value set during object initialization.
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

    # Set localpath, local, and remote as given here or during init
    if localpath is None:
        localpath = self.localpath
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

    # Check localpath first
    copied = False
    num_copied = 0
    if local is True and localpath is not None:
        local_dir = Path(localpath, 'potential_LAMMPS', lammps_potential.id)
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
    

def upload_lammps_potential(self, lammps_potential, workspace=None, verbose=False):
    """
    Saves a new LAMMPS potential to the remote database.  Requires write
    permissions to potentials.nist.gov

    Parameters
    ----------
    lammps_potential : PotentialLAMMPS
        The content to save.
    workspace, str, optional
        The workspace to assign the record to. If not given, no workspace will
        be assigned (only accessible to user who submitted it).
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """

    title = lammps_potential.id
    content = lammps_potential.asmodel().xml().replace('True', 'true').replace('False', 'false')
    template = 'potential_LAMMPS'
    
    self.upload_record(template, content, title, workspace=workspace, 
                        verbose=verbose)

def save_lammps_potentials(self, lammps_potentials, filenames=None,
                           downloadfiles=False, format='xml', localpath=None,
                           indent=None, overwrite=True, verbose=False, reload=False):
    """
    Saves a new LAMMPS potential to the local copy of the database

    Parameters
    ----------
    lammps_potentials : PotentialLAMMPS or list of PotentialLAMMPS
        The lammps_potential(s) to save.
    filenames : list, optional
        The paths to any local parameter files associated with the
        lammps_potentials to copy to the localpath database.  If filenames
        is given and multiple lammps_potentials are given, then
        the length of the filenames list should be the same as the length of
        lammps_potentials.  Each entry can be None, a path, or a list
        of paths.  If not given, each entry will be set to None.
    downloadfiles : bool, optional
        If True, then the parameter files for the lammps_potentials will
        attempt to be downloaded.  If filenames are given for a particular
        lammps potential, then no files will be downloaded.
    format : str, optional
        The file format to save the record files as.  Allowed values are 'xml'
        (default) and 'json'.
    localpath : path-like object, optional
        Path to a local directory where the record and files will be saved to.
        If not given, will use the localpath value set during object
        initialization.
    indent : int, optional
        The indentation spacing size to use for the locally saved record files.
        If not given, the JSON/XML content will be compact.
    overwrite : bool, optional
        If True (default) then any matching LAMMPS potentials already in the
        localpath will be updated if the content has changed.  If False, all
        existing LAMMPS potentials in the localpath will be unchanged.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    reload : bool, optional
        If True, will call load_lammps_potentials() after adding the new
        potential.  Default value is False: loading is slow and should only be
        done when you wish to retrieve the saved potentials.
    """
    template = 'potential_LAMMPS'
    
    # Check localpath values
    if localpath is None:
        localpath = self.localpath
    if localpath is None:
        raise ValueError('localpath must be set to save files')

    # Check format value
    format = format.lower()
    allowed_formats = ['xml', 'json']
    if format not in allowed_formats:
        raise ValueError("Format must be 'xml' or 'json'")

    # Check lammps_potentials and filenames
    lammps_potentials = aslist(lammps_potentials)
    if filenames is None:
        filenames = [None for i in range(len(lammps_potentials))]
    filenames = aslist(filenames)
    if len(lammps_potentials) == 1 and len(filenames) > 1:
        filenames = [filenames]
    if len(lammps_potentials) != len(filenames):
         raise ValueError('Incompatible number of lammps_potentials and filenames')

    # Convert builders to PotentialLAMMPS objects and check for ids
    for i in range(len(lammps_potentials)):
        if isinstance(lammps_potentials[i], PotentialLAMMPSBuilder):
            lammps_potentials[i] = lammps_potentials[i].potential()
        if lammps_potentials[i].id is None:
            raise ValueError(f'The id of lammps_potentials[{i}] not set')

    # Create save directory if needed
    save_directory = Path(localpath, template)
    if not save_directory.is_dir():
        save_directory.mkdir(parents=True)

    # Check for existing records of a different format
    for fmt in allowed_formats:
        if fmt != format:
            numexisting = len([fname for fname in save_directory.glob(f'*.{fmt}')])
            if numexisting > 0:
                raise ValueError(f'{numexisting} records of format {fmt} already saved locally')

    count_duplicate = 0
    count_updated = 0
    count_new = 0    
    count_files_copied = 0
    count_files_not_found = 0
    count_files_downloaded = 0
    count_files_not_downloaded = 0

    for lammps_potential, fnames in zip(lammps_potentials, filenames):
    
        # Build record name
        potname = lammps_potential.id
        recordname = Path(save_directory, f'{potname}.{format}')

        # Skip existing records if overwrite is False
        if overwrite is False and recordname.is_file():
            count_duplicate += 1
            continue

        # Build content
        if format == 'xml':
            content = lammps_potential.asmodel().xml(indent=indent)
        elif format == 'json':
            content = lammps_potential.asmodel().json(indent=indent)

        # Check if existing content has changed
        if recordname.is_file():
            with open(recordname, encoding='UTF-8') as f:
                oldcontent = f.read()
            if content == oldcontent:
                count_duplicate += 1
                continue
            else:
                count_updated += 1
        else:
            count_new += 1

        with open(recordname, 'w', encoding='UTF-8') as f:
            f.write(content)

        # Copy files
        if fnames is not None:
            fnames = aslist(fnames)
            
            potdir = Path(save_directory, potname)
            if len(fnames) > 0:
                if not potdir.is_dir():
                    potdir.mkdir(parents=True)
                
                for filename in fnames:
                    shutil.copy(filename, potdir)
                count_files_copied += 1
            else:
                count_files_not_found += 1
        
        # Build list of potentials to download records for
        elif downloadfiles:
            if len(lammps_potential.artifacts) > 0:
                pot_dir = Path(save_directory, potname)
                lammps_potential.download_files(pot_dir=potdir)
                count_files_downloaded += 1
            else:
                count_files_not_downloaded += 1
        
    if verbose:
        print(f'{len(lammps_potentials)} LAMMPS potentials saved to localpath')
        if count_new > 0:
            print(f' - {count_new} new potentials added')
        if count_updated > 0:
            print(f' - {count_updated} existing potentials updated')
        if count_duplicate > 0:
            print(f' - {count_duplicate} duplicate potentials skipped')
        if count_files_copied > 0:
            print(f' - {count_files_copied} potentials had files copied')
        if count_files_not_found > 0:
            print(f' - {count_files_not_found} potentials had no files to copy')
        if count_files_downloaded > 0:
            print(f' - {count_files_downloaded} potentials had files downloaded')
        if count_files_not_downloaded > 0:
            print(f' - {count_files_not_downloaded} potentials had no files to download')

    if reload:
        self.load_lammps_potentials(verbose=verbose)

def delete_lammps_potential(self, lammps_potential, local=True, remote=False,
                            localpath=None, paramfiles=True, verbose=False):
    """
    Deletes a lammps_potential from the remote database.  Requires write
    permissions to potentials.nist.gov

    Parameters
    ----------
    lammps_potential : PotentialLAMMPS or str
        The LAMMPS potential to delete from the remote database.  Can either
        give the corresponding PotentialLAMMPS object or just the potential's
        id/title.
    local : bool, optional
        If True (default) then the record will be deleted from the localpath.
    remote : bool, optional
        If True then the record will be deleted from the remote database.  
        Requires write permissions to potentials.nist.gov.  Default value is
        False.
    localpath : path-like object, optional
        Path to a local directory where the file to delete is located.  If not
        given, will use the localpath value set during object initialization.
    paramfiles : bool, optional
        If True (default) and local is True, then any parameter files
        associated with the record will also be deleted from localpath.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    template = 'potential_LAMMPS'
    if isinstance(lammps_potential, PotentialLAMMPS):
        title = lammps_potential.id
    elif isinstance(lammps_potential, str):
        title = lammps_potential
    else:
        raise TypeError('Invalid lammps_potential value: must be PotentialLAMMPS or str')
    
    self.delete_record(template, title, local=local, remote=remote,
                       localpath=localpath, verbose=verbose)

    # Delete local parameter files
    if local is True and paramfiles is True:
        # Check localpath values
        if localpath is None:
            localpath = self.localpath
        if localpath is None:
            raise ValueError('localpath must be set to delete local files')
        
        paramdir = Path(localpath, template, title)
        if paramdir.is_dir():
            shutil.rmtree(paramdir)
    