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
                if status is not None and lammps_potential.status in status:
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
                         status='active', pair_style=None, element=None,
                         symbol=None, verbose=False, get_files=False):
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
    element : str or list, optional
        The included elemental model(s) to limit the search by.
    symbol : str or list, optional
        The included symbol model(s) to limit the search by.
    verbose: bool, optional
        If True, informative print statements will be used.
    get_files : bool, optional
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
                         &potsdf.apply(listmatch, args=[element, 'elements'], axis=1)
                         &potsdf.apply(listmatch, args=[symbol, 'symbols'], axis=1)]
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
        
        # Add element query
        if element is not None:
            element = aslist(element)
            mquery['potential-LAMMPS.atom.element'] = {'$all': element}

        # Add symbol query
        if symbol is not None:
            symbol = aslist(symbol)
            mquery['$or'] = []
            # Check symbols
            mquery['$or'].append({'potential-LAMMPS.atom.symbol': {'$all': symbol}})
            # if symbols not in model, check elements
            mquery['$or'].append({'potential-LAMMPS.atom.symbol': {'$exists': False},
                                'potential-LAMMPS.atom.element':{'$all': symbol}})

        matches = self.cdcs.query(template='potential_LAMMPS', mongoquery=mquery)
        if len(matches) > 0:
            matches = matches.sort_values('title').reset_index(drop=True)
        def makepotentials(series):
            return PotentialLAMMPS(model=series.xml_content)

        if verbose:
            print(len(matches), 'matching LAMMPS potentials found from remote database')
        lammps_potentials = matches.apply(makepotentials, axis=1)

    # Get files, set pot_dir
    if get_files is True:
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
                         status='active', pair_style=None, element=None,
                         symbol=None, verbose=False, get_files=False):
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
    element : str or list, optional
        The included elemental model(s) to limit the search by.
    symbol : str or list, optional
        The included symbol model(s) to limit the search by.
    verbose: bool, optional
        If True, informative print statements will be used.
    get_files : bool, optional
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
                         status=status, pair_style=pair_style, element=element,
                         symbol=symbol, verbose=verbose, get_files=False)
                         
    if len(lammps_potentials) == 1:
        lammps_potential = lammps_potentials[0]
    elif len(lammps_potentials) == 0:
        raise ValueError('No matching LAMMPS potentials found')
    else:
        raise ValueError('Multiple matching LAMMPS potentials found')

    if get_files is True:
        self.get_lammps_potentials_files(lammps_potential, verbose=verbose)
        lammps_potential.pot_dir = lammps_potential.id
    
    return lammps_potential

def download_lammps_potentials(self, localpath=None, lammps_potentials=None,
                               format='xml', indent=None, verbose=False,
                               status='active', get_files=True):
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
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    status : str, list or None, optional
        Only potential_LAMMPS records with the given status(es) will be
        downloaded.  Allowed values are 'active' (default), 'superseded', and
        'retracted'.  If None is given, then all potentials will be downloaded.
    get_files : bool, optional
        If True, the parameter files associated with the potential_LAMMPS
        record will also be downloaded.
    """
    # Load potentials to speed up file downloads
    if get_files is True and self.potentials is None:
        self.load_potentials()

    template = 'potential_LAMMPS'
    
    # Check localpath values
    if localpath is None:
        localpath = self.localpath
    if localpath is None:
        raise ValueError('localpath must be set to download files')
    
    # Check format value
    format = format.lower()
    allowed_formats = ['xml', 'json']
    if format not in allowed_formats:
        raise ValueError("Format must be 'xml' or 'json'")
    
    

    # Create save directory if needed
    save_directory = Path(localpath, template)
    if not save_directory.is_dir():
        save_directory.mkdir(parents=True)

    for fmt in allowed_formats:
        if fmt != format:
            numexisting = len([fname for fname in save_directory.glob(f'*.{fmt}')])
            if numexisting > 0:
                raise ValueError(f'{numexisting} records of format {fmt} already saved locally')

    # Download and save
    if lammps_potentials is None:

        mquery = {}

        # Add status query
        if status is not None:
            status = aslist(status)
            if 'active' in status:
                status.append(None)
            mquery['potential-LAMMPS.status'] = {'$in':status}

        records = self.cdcs.query(template=template, mongoquery=mquery)
        for i in range(len(records)):
            record = records.iloc[i]
            fname = Path(save_directory, f'{record.title}.{format}')
            content = DM(record.xml_content)
            with open(fname, 'w', encoding='UTF-8') as f:
                if format == 'xml':
                    content.xml(fp=f, indent=indent)
                else:
                    content.json(fp=f, indent=indent)
        if verbose:
            print(f'Downloaded {len(records)} of {template}')
    
    # Save loaded content
    else:
        if status is None:
            status = ['active', 'superseded', 'retracted']
        else:
            status = aslist(status)

        for lammps_potential in aslist(lammps_potentials):
            if lammps_potential.status not in status:
                continue
            
            potname = lammps_potential.id

            fname = Path(save_directory, f'{potname}.{format}')
            if format == 'xml':
                with open(fname, 'w', encoding='UTF-8') as f:
                    lammps_potential.asmodel().xml(fp=f, indent=indent)
            elif format == 'json':
                with open(fname, 'w', encoding='UTF-8') as f:
                    lammps_potential.asmodel().json(fp=f, indent=indent)
        
        if verbose:
            print(f'Downloaded {len(lammps_potentials)} of {template}')

    if get_files is True:
        # Convert downloaded records to lammps_potentials
        def makepotentials(series):
            return PotentialLAMMPS(model=series.xml_content)
        lammps_potentials = records.apply(makepotentials, axis=1)
        
        # Download parameter files
        self.get_lammps_potentials_files(lammps_potentials,
                                         local=False, remote=True,
                                         targetdir=save_directory,
                                         verbose=verbose)

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
            potential = self.get_potential(id=lammps_potential.potid)
            
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

def upload_lammps_potential(self, lammps_potential, verbose=False):
    """
    Saves a new LAMMPS potential to the remote database.  Requires write
    permissions to potentials.nist.gov

    Parameters
    ----------
    lammps_potential : PotentialLAMMPS
        The content to save.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """

    title = lammps_potential.id
    content = lammps_potential.asmodel().xml().replace('True', 'true').replace('False', 'false')
    template = 'potential_LAMMPS'
    try:
        try:
            self.cdcs.upload_record(content=content, template=template, title=title)
            if verbose:
                print('potential_LAMMPS added to database')
        except:
            self.cdcs.update_record(content=content, template=template, title=title)
            if verbose:
                print('potential_LAMMPS updated in database')
    except:
        if verbose:
            print('Failed to upload potential_LAMMPS to database')

def save_lammps_potential(self, lammps_potential, filenames=None,
                          localpath=None, format='xml', indent=None,
                          verbose=False, reload=False):
    """
    Saves a new LAMMPS potential to the local copy of the database

    Parameters
    ----------
    lammps_potential : PotentialLAMMPS or PotentialLAMMPSBuilder
        The content to save.
    filenames : str, path or list, optional
        The path names to any parameter files associated with the potential.
        These will be copied into the local directory as well
    localpath : path-like object, optional
        Path to a local directory where the record and files will be saved to.
        If not given, will use the localpath value set during object
        initialization.
    format : str, optional
        The file format to save the record files as.  Allowed values are 'xml'
        (default) and 'json'.
    indent : int, optional
        The indentation spacing size to use for the locally saved record files.
        If not given, the JSON/XML content will be compact.
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

    # Check potential
    if isinstance(lammps_potential, PotentialLAMMPSBuilder):
        lammps_potential = lammps_potential.potential()
    if lammps_potential.id is None:
        raise ValueError('The id of lammps_potential must be set')
    
    # Save potential
    title = lammps_potential.id
    content = lammps_potential.asmodel()
    if not Path(localpath, template).is_dir():
        Path(localpath, template).mkdir(parents=True)
    fname = Path(localpath, template, f'{title}.{format}')
    with open(fname, 'w') as f:
        if format == 'xml':
            content.xml(fp=f, indent=indent)
        elif format == 'json':
            content.json(fp=f, indent=indent)
    if verbose:
        print(f'LAMMPS potential {title} saved to {localpath}')

    # Copy files
    if filenames is not None:
        potdir = Path(localpath, template, title)
        if not potdir.is_dir():
            potdir.mkdir(parents=True)
        filenames = aslist(filenames)
        for filename in filenames:
            shutil.copy(filename, potdir)
        if verbose:
            print(f'copied {len(filenames)} parameter files')
    
    if reload:
        self.load_lammps_potentials()
