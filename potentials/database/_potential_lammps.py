# coding: utf-8
# Standard Python libraries
from pathlib import Path

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://requests.readthedocs.io/en/master/
import requests

# Local imports
from .. import PotentialLAMMPS
from ..tools import aslist

@property
def potential_LAMMPS(self):
    return self.__potential_LAMMPS

@property
def potential_LAMMPS_df(self):
    return self.__potential_LAMMPS_df

def _no_load_potential_LAMMPS(self):
    self.__potential_LAMMPS = None
    self.__potential_LAMMPS_df = None

def load_potential_LAMMPS(self, localpath=None, verbose=False):
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
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    potentials = {}
    localloaded = 0

    # Set localpath as given here or during init
    if localpath is None:
        localpath = self.localpath
    
    # Check localpath first
    if localpath is not None:
        for potfile in Path(localpath, 'potential_LAMMPS').glob('*'):
            if potfile.suffix in ['.xml', '.json']:
                potentials[potfile.stem] = PotentialLAMMPS(potfile)

        if verbose:
            localloaded = len(potentials)
            print(f'Loaded {localloaded} local LAMMPS potentials')
    
    # Load remote
    try:
        records = self.cdcs.query(template='potential_LAMMPS')
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
    
    # Build potential_LAMMPS and potential_LAMMPS_df
    if len(potentials) > 0:
        pots = np.array(list(potentials.values()))
        potdicts = []
        for pot in pots:
            potdicts.append(pot.asdict())

        self.__potential_LAMMPS_df = pd.DataFrame(potdicts).sort_values('id')
        self.__potential_LAMMPS = pots[self.potential_LAMMPS_df.index]
        self.__potential_LAMMPS_df.reset_index(drop=True)

    else:
        self.__potential_LAMMPS = None
        self.__potential_LAMMPS_df = None

def get_potential_LAMMPS(self, id=None, key=None, potid=None, potkey=None,
                         status='active', pair_style=None, element=None,
                         symbol=None, verbose=False):
    
    # Check loaded values if available
    if self.potential_LAMMPS_df is not None:
        
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
        
        pots = self.potential_LAMMPS
        potsdf = self.potential_LAMMPS_df
        potentials = pots[potsdf.apply(valmatch, args=[id, 'id'], axis=1)
                         &potsdf.apply(valmatch, args=[key, 'key'], axis=1)
                         &potsdf.apply(valmatch, args=[potid, 'potid'], axis=1)
                         &potsdf.apply(valmatch, args=[potkey, 'potkey'], axis=1)
                         &potsdf.apply(valmatch, args=[status, 'status'], axis=1)
                         &potsdf.apply(valmatch, args=[pair_style, 'pair_style'], axis=1)
                         &potsdf.apply(listmatch, args=[element, 'elements'], axis=1)
                         &potsdf.apply(listmatch, args=[symbol, 'symbols'], axis=1)]
        if verbose:
            print(len(potentials), 'matching LAMMPS potentials found from loaded records')
        return potentials

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
            #mquery['potential-LAMMPS.status'] = {'$in': status}

        # Add pair_style query
        if pair_style is not None:
            pair_style = aslist(pair_style)
            mquery['potential-LAMMPS.pair_style'] = {'$in': pair_style}
        
        # Add element query
        if element is not None:
            element = aslist(element)
            mquery['potential-LAMMPS.atom.element'] = {'$all': element}
        
        # Add symbol query
        if symbol is not None:
            symbol = aslist(symbol)
            mquery['potential-LAMMPS.atom.symbol'] = {'$all': symbol}

        matches = self.cdcs.query(template='potential_LAMMPS', mongoquery=mquery)
        if len(matches) > 0:
            matches = matches.sort_values('title').reset_index(drop=True)
        def makepotentials(series):
            return PotentialLAMMPS(model=series.xml_content)

        if verbose:
            print(len(matches), 'matching LAMMPS potentials found from remote database')
        return matches.apply(makepotentials, axis=1)

def download_LAMMPS_files(self, potential_LAMMPS, targetdir='.'):

    for lmppot in aslist(potential_LAMMPS):
        pot = self.get_potential(id=lmppot.potid)
        potdir = Path(targetdir, pot.id)
        if not potdir.is_dir():
            potdir.mkdir()

        match = False
        for imp in pot.implementations:
            if imp.key == lmppot.key:
                match = True
                break
        if not match:
            raise ValueError('No matching potential implementation found {imp.id} ({imp.key})')
        
        for artifact in imp.artifacts:
            r = requests.get(artifact.url)
            r.raise_for_status()

            artifactfile = Path(potdir, artifact.filename)
            with open(artifactfile, 'wb') as f:
                f.write(r.content)