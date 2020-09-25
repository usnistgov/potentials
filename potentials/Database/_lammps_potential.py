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
                           status='active', verbose=False):
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

    # Check localpath first
    if local is True and localpath is not None:

        if status is not None:
            status = aslist(status)

        for potfile in Path(localpath, 'potential_LAMMPS').glob('*'):
            if potfile.suffix in ['.xml', '.json']:
                lammps_potential = PotentialLAMMPS(potfile)
                if status is None or lammps_potential.status in status:
                    potentials[potfile.stem] = PotentialLAMMPS(potfile)

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
    
    # Build lammps_potentials and lammps_potentials_df
    if len(potentials) > 0:
        pots = np.array(list(potentials.values()))
        potdicts = []
        for pot in pots:
            potdicts.append(pot.asdict())

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
                         symbols=None, verbose=False, getfiles=False):
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
    getfiles : bool, optional
        If True, then the parameter files for the matching potentials
        will also be retrieved and copied to the working directory.
        If False (default) and the parameter files are in the library,
        then the returned objects' pot_dir path will be set appropriately.
        
    Returns
    -------
    Potential.LAMMPSPotential
        The potential object to use.
    """
    # Check loaded values if available
    if self.lammps_potentials_df is not None:
        
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

    # Get files, set pot_dir
    if getfiles is True:
        self.get_lammps_potentials_files(lammps_potentials, verbose)
        for lammps_potential in lammps_potentials:
            lammps_potential.pot_dir = lammps_potential.id
    
    # Try to find pot_dir path in local files
    elif self.localpath is not None:
        for lammps_potential in lammps_potentials:
            pot_path = Path(self.localpath, 'potential_LAMMPS', lammps_potential.id)
            if pot_path.is_dir():
                lammps_potential.pot_dir = pot_path

    return lammps_potentials

def get_lammps_potential(self, id=None, key=None, potid=None, potkey=None,
                         status='active', pair_style=None, elements=None,
                         symbols=None, verbose=False, getfiles=False):
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
    verbose: bool, optional
        If True, informative print statements will be used.
    getfiles : bool, optional
        If True, then the parameter files for the matching potentials
        will also be retrieved and copied to the working directory.
        If False (default) and the parameter files are in the library,
        then the returned objects' pot_dir path will be set appropriately.
        
    Returns
    -------
    Potential.LAMMPSPotential
        The potential object to use.
    """
    lammps_potentials = self.get_lammps_potentials(id=id, key=key, potid=potid, potkey=potkey,
                         status=status, pair_style=pair_style, elements=elements,
                         symbols=symbols, verbose=verbose, getfiles=False)
                         
    if len(lammps_potentials) == 1:
        lammps_potential = lammps_potentials[0]
    elif len(lammps_potentials) == 0:
        raise ValueError('No matching LAMMPS potentials found')
    else:
        raise ValueError('Multiple matching LAMMPS potentials found')

    if getfiles is True:
        self.get_lammps_potentials_files(lammps_potential, verbose=verbose)
        lammps_potential.pot_dir = lammps_potential.id
    
    return lammps_potential

def download_lammps_potentials(self, format='xml', localpath=None, indent=None,
                               status='active', getfiles=True,
                               overwrite=True, verbose=False, reload=False):
    """
    Download potential_LAMMPS records from the remote and save to localpath.
    
    Parameters
    ----------
    localpath : path-like object, optional
        Path to a local directory where the files will be saved to.  If not
        given, will use the localpath value set during object initialization.
    lammps_potentials : list, optional
        A list of LAMMPS potentials to download. If not given, all LAMMPS
        potentials will be downloaded.
    format : str, optional
        The file format to save the record files as.  Allowed values are 'xml'
        (default) and 'json'.
    indent : int, optional
        The indentation spacing size to use for the locally saved record files.
        If not given, the JSON/XML content will be compact.
    status : str, list or None, optional
        Only potential_LAMMPS records with the given status(es) will be
        downloaded.  Allowed values are 'active' (default), 'superseded', and
        'retracted'.  If None is given, then all potentials will be downloaded.
    getfiles : bool, optional
        If True, the parameter files associated with the potential_LAMMPS
        record will also be downloaded.
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
    
    # Load potentials to speed up file downloads
    if getfiles is True and self.potentials is None:
        self.load_potentials()

    mquery = {}

    # Add status query
    if status is not None:
        status = aslist(status)
        if 'active' in status:
            status.append(None)
        mquery['potential-LAMMPS.status'] = {'$in':status}

    records = self.cdcs.query(template=template, mongoquery=mquery)
    def makelammpspotentials(series):
        return PotentialLAMMPS(model=series.xml_content)
    lammps_potentials = records.apply(makelammpspotentials, axis=1)

    if getfiles is True:
        filenames = None
    else:
        filenames = [[] for i in range(len(lammps_potentials))]

    self.save_lammps_potentials(lammps_potentials, filenames=filenames,
                                format=format, localpath=localpath,
                                indent=indent, overwrite=overwrite,
                                verbose=verbose, reload=reload)

def get_lammps_potentials_files(self, lammps_potentials, localpath=None,
                                local=None, remote=None, targetdir='.',
                                verbose=False):
    
    # Set localpath, local, and remote as given here or during init
    if localpath is None:
        localpath = self.localpath
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    # Initialize counters
    num_copied = 0
    num_downloaded = 0

    # Loop over all given potentials
    for lammps_potential in aslist(lammps_potentials):
        
        copied = False
        # Check localpath first
        if local is True and localpath is not None:
            pot_dir = Path(localpath, 'potential_LAMMPS', lammps_potential.id)
            out_dir = Path(targetdir, lammps_potential.id)
            if pot_dir.is_dir():
                if not out_dir.is_dir():
                    shutil.copytree(pot_dir, out_dir)
                    num_copied += 1
                    copied = True
        
        # Check remote
        if remote is True and copied is False:
            try:
                potential = self.get_potential(id=lammps_potential.potid)
            except:
                pass
            else:
                # Find matching implementation
                impmatch = False
                for imp in potential.implementations:
                    if imp.key == lammps_potential.key:
                        impmatch = True
                        break
                
                # Download artifacts
                if impmatch:
                    pot_dir = Path(targetdir, lammps_potential.id)
                    if not pot_dir.is_dir():
                        pot_dir.mkdir(parents=True)

                    for artifact in imp.artifacts:
                        r = requests.get(artifact.url)
                        r.raise_for_status()
                        artifactfile = Path(pot_dir, artifact.filename)
                        with open(artifactfile, 'wb') as f:
                            f.write(r.content)
                    num_downloaded += 1
    
    if verbose:
        if local:
            print(f'Files for {num_copied} LAMMPS potentials copied')
        if remote:
            print(f'Files for {num_downloaded} LAMMPS potentials downloaded')

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
                           format='xml', localpath=None,  indent=None,
                           overwrite=True, verbose=False, reload=False):
    """
    Saves a new LAMMPS potential to the local copy of the database

    Parameters
    ----------
    lammps_potentials : PotentialLAMMPS or list of PotentialLAMMPS
        The lammps_potential(s) to save.
    filenames : list, optional
        The path names to any parameter files associated with each
        lammps_potentials.  Length of the list should be the same as the
        length of lammps_potentials.  Each entry can be None, a path, or a list
        of paths.  If the value is None for an entry then the corresponding
        Potential record will be searched for parameter files to download.  
        Note that files will only be copied/downloaded if the associated record
        is new/different.
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
    downloaders = []

    for lammps_potential, fnames in zip(lammps_potentials, filenames):
    
        # Build filename
        potname = lammps_potential.id
        fname = Path(save_directory, f'{potname}.{format}')

        # Skip existing files if overwrite is False
        if overwrite is False and fname.is_file():
            count_duplicate += 1
            continue

        # Build content
        if format == 'xml':
            content = lammps_potential.asmodel().xml(indent=indent)
        elif format == 'json':
            content = lammps_potential.asmodel().json(indent=indent)

        # Check if existing content has changed
        if fname.is_file():
            with open(fname, encoding='UTF-8') as f:
                oldcontent = f.read()
            if content == oldcontent:
                count_duplicate += 1
                continue
            else:
                count_updated += 1
        else:
            count_new += 1

        with open(fname, 'w', encoding='UTF-8') as f:
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
        else:
            downloaders.append(lammps_potential)
        
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
    
    # Download files for the lammps potentials without lists of files
    if len(downloaders) > 0:
        self.get_lammps_potentials_files(downloaders,
                                         local=False, remote=True,
                                         targetdir=save_directory,
                                         verbose=verbose)

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
    