# coding: utf-8
# Standard Python libraries
from pathlib import Path

# https://numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# Local imports
from .. import Potential
from ..tools import aslist

@property
def potentials(self):
    return self.__potentials

@property
def potentials_df(self):
    return self.__potentials_df

def _no_load_potentials(self):
    self.__potentials = None
    self.__potentials_df = None

def load_potentials(self, localpath=None, verbose=False):
    """
    Loads potentials from the database, first checking localpath, then
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
    potentials = []
    potnames = []

    # Set localpath as given here or during init
    if localpath is None:
        localpath = self.localpath
    
    # Check localpath first
    if localpath is not None:
        for potfile in Path(localpath, 'Potential').glob('*'):
            if potfile.suffix in ['.xml', '.json']:
                potentials.append(Potential(potfile))
                potnames.append(potfile.stem)

        if verbose:
            print(f'Loaded {len(potentials)} local potentials')
    
    # Load remote
    try:
        records = self.cdcs.query(template='Potential')
    except:
        if verbose:
            print('Failed to load potentials from remote')
    else:
        if verbose:
            print(f'Loaded {len(records)} remote potentials')
        for i in range(len(records)):
            record = records.iloc[i]
            if record.title not in potnames:
                potentials.append(Potential(record.xml_content))

        if verbose and len(potnames) > 0:
            print(f' - {len(potentials) - len(potnames)} new')
    
    # Build potentials and potentials_df
    if len(potentials) > 0:
        potdicts = []
        for potential in potentials:
            potdicts.append(potential.asdict())
        self.__potentials_df = pd.DataFrame(potdicts).sort_values('id')
        self.__potentials = np.array(potentials)[self.__potentials_df.index]
        self.__potentials_df.reset_index(drop=True)

    else:
        self.__potentials = None
        self.__potentials_df = None

def get_potentials(self, id=None, key=None, author=None, year=None, element=None,
                  localpath=None, verbose=False):
    
    # Check loaded values if available
    if self.potentials_df is not None:
        
        def idmatch(series, val):
            if val is None:
                return True
            else:
                return series.id in aslist(val)

        def keymatch(series, val):
            if val is None:
                return True
            else:
                return series.key in aslist(val)
        
        def authormatch(series, val):
            if val is None:
                return True
            else:
                val = aslist(val)
                matches = [False for i in range(len(val))]
                for citation in series.citations:
                    for i in range(len(val)):
                        if val[i] in citation.author:
                            matches[i] = True
                if sum(matches) == len(val):
                    return True
                else:
                    return False

        def yearmatch(series, val):
            if val is None:
                return True
            else:
                val = aslist(val)
                for i in range(len(val)):   
                    val[i] = str(val[i])
                for citation in series.citations:
                    if citation.year in aslist(val):
                        return True
                return False
        
        def elementmatch(series, val):
            if val is None:
                return True
            
            elif isinstance(series.elements, list):
                for v in aslist(val):
                    if v not in series.elements:
                        return False
                return True
            else:
                return False
        
        potentials = self.potentials[self.potentials_df.apply(idmatch, args=[id], axis=1)
                              &self.potentials_df.apply(keymatch, args=[key], axis=1)
                              &self.potentials_df.apply(authormatch, args=[author], axis=1)
                              &self.potentials_df.apply(yearmatch, args=[year], axis=1)
                              &self.potentials_df.apply(elementmatch, args=[element], axis=1)]
        if verbose:
            print(len(potentials), 'matching potentials found from loaded records')
        return potentials

    # Check remote values if no loaded values
    else:
        # Build Mongoquery
        mquery = {}

        # Add id query
        if id is not None:
            id = aslist(id)
            mquery['interatomic-potential.id'] = {'$in': id}

        # Add key query
        if key is not None:
            key = aslist(key)
            mquery['interatomic-potential.key'] = {'$in': key}

        # Add author query
        if author is not None:
            author = aslist(author)
            mquery['$and'] = []
            for auth in author:
                mquery['$and'].append({'interatomic-potential.description.citation.author.surname':{'$regex': auth}})
                
        # Add year query
        if year is not None:
            year = aslist(year)
            for i in range(len(year)):
                year[i] = int(year[i])
            mquery['interatomic-potential.description.citation.publication-date.year'] = {'$in': year}
            
        # Add year query
        if element is not None:
            element = aslist(element)
            mquery['interatomic-potential.element'] = {'$all': element}

        matches = self.cdcs.query(template='Potential', mongoquery=mquery)

        if verbose:
            print(len(matches), 'matching potentials found from remote database')

        if len(matches) > 0:
            matches = matches.sort_values('title').reset_index(drop=True)

            def makepotentials(series):
                return Potential(model=series.xml_content)

            return matches.apply(makepotentials, axis=1).values
        else:
            return np.array([])


def get_potential(self, id=None, author=None, year=None, element=None,
                  localpath=None, verbose=False):
    
    potentials = self.get_potentials(id=id, author=author, year=year, element=element,
                                     localpath=localpath, verbose=verbose)
    if len(potentials) == 1:
        return potentials[0]
    elif len(potentials) == 0:
        raise ValueError('No matching potentials found')
    else:
        raise ValueError('Multiple matching potentials found')

def save_potential(self, potential, verbose=False):
    title = 'potential.' + potential.id
    content = potential.asmodel().xml()
    template = 'Potential'
    try:
        self.cdcs.upload_record(content=content, template=template, title=title)
        if verbose:
            print('Potential added to database')
    except:
        self.cdcs.update_record(content=content, template=template, title=title)
        if verbose:
            print('Potential updated in database')