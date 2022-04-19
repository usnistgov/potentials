# coding: utf-8
# Standard Python libraries
from pathlib import Path
import json
from typing import Optional, Union

# https://docs.python-requests.org/
import requests

# Local imports
from ..tools import aslist

@property
def related_models(self) -> dict:
    """dict : The list of all related models by interactions"""
    try:
        return self.__related_models
    except:
        self.load_related_models()
        return self.__related_models

def load_related_models(self,
                        local: Optional[bool] = None,
                        remote: Optional[bool] = None,
                        verbose: Optional[bool] = False):
    """
    Loads the related-interactions.json file from either the local location
    or the NIST Interatomic Potentials Repository website.
    
    Parameters
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    verbose : bool, optional
        If True, informative print statements will be generated.
    """
    # Handle local and remote
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote

    if local is True:
        localfile = Path(self.local_database.host, 'related-interactions.json')
        if localfile.is_file():
            with open(localfile) as f:
                self.__related_models = json.load(f)
            if verbose:
                print('related models loaded from the local location')
            return

    if remote is True:
        url = 'https://www.ctcms.nist.gov/potentials/site/related-interactions.json'
        r = requests.get(url)
        r.raise_for_status()
        self.__related_models = json.loads(r.text)
        if verbose:
            print('related models downloaded from the web')
        return
    
    raise ValueError('Failed to find related-interactions.json')

def get_related_models(self, potid: str) -> dict:
    """
    Finds all known related interaction models for a given interatomic potential.

    Parameters
    ----------
    potid : str
        The id of a potential entry to find all related models for.
    
    Returns
    -------
    dict
        The list of all matching related models by interactions
    """
    related_models = self.related_models

    related = {}
    
    # Loop over all interactions
    for interaction in related_models:
        
        # Loop over all sets of related models for the interaction
        for potidset in related_models[interaction]:
            
            # If potid in the set, list all related pot ids for that interaction
            if potid in potidset:
                if interaction not in related:
                    related[interaction] = []
                    for potid2 in potidset:
                        if potid != potid2:
                            related[interaction].append(potid2)
                
                else:
                    raise ValueError(f'{potid} in multiple sets for {interaction}')
    
    if len(related) == 0:
        raise ValueError(f'{potid} not found in related models')

    return related

def save_related_models(self,
                        local: bool = True,
                        altpath: Optional[Path] = None):
    """
    Saves the related-interactions.json file.

    Parameters
    ----------
    local : bool, optional
        Indicates if the file is to be saved to the local location.  Default
        value is True.
    altpath : path-like object, optional
        An alternate directory to save the file to.  If given and local=True,
        then two copies will be saved: one in the local location and one in
        altpath.
    """
    # Save to local location
    if local is True:
        filename = Path(self.local_database.host, 'related-interactions.json')
        with open(filename, 'w') as f:
            json.dump(self.related_models, fp=f)
    
    # Save to altpath
    if altpath is not None:
        
        altpath = Path(altpath)
        if not altpath.is_dir():
            altpath.mkdir(parents=True)

        filename = Path(altpath, 'related-interactions.json')
        with open(filename, 'w') as f:
            json.dump(self.related_models, fp=f)

def add_related_models(self,
                       potid: str,
                       interactions: Union[str, list],
                       related_ids: Union[str, list, None] = None,
                       verbose: bool = False):
    """
    Adds an interatomic potential to the related-interactions.json.  Note
    that this only changes values in the loaded related_models object and any
    changes will still need to be saved using save_related_models().

    Parameters
    ----------
    potid : str
        The id of the potential entry being added to the related models.
    interactions : str or list
        The model interaction(s) defined by the potential.  Each value
        should be a single element symbol for elemental interactions, or a 
        hyphen-separated pair of element symbols for binary interactions.
    related_ids : str, None or list
        This specifies a related potential entry by id for each interaction.
        Giving a value of None for an interaction indicates that the potential
        identified by potid has no known related models for that interaction.
        If not given, then no related models will be set for all
        interactions.
    verbose : bool, optional
        If True, informative print statements will be used.  Default value is
        False.
    """

    # Check values of interactions and related_ids
    interactions = aslist(interactions)
    if related_ids is None:
        related_ids = [None for i in range(len(interactions))]
    else:
        related_ids = aslist(related_ids)
        if len(related_ids) != len(interactions):
            raise ValueError('Different number of related_ids and interactions given')

    # Get/load the related_models dict
    related_models = self.related_models

    # Loop over all interactions
    for interaction, relid in zip(interactions, related_ids):

        # Check and sort binary interactions
        if '-' in interaction:
            terms = interaction.split('-')
            assert len(terms) == 2
            interaction = '-'.join(sorted(terms))

        # Check if interaction exists
        if interaction not in related_models:
            
            # Add set to new interaction
            if relid is None:
                related_models[interaction] = [[potid]]
            else:
                related_models[interaction] = [[potid, relid]]
            if verbose:
                print(f'Set added to new interaction {interaction}')
        
        else:

            # Pull out models for the interaction
            int_models = related_models[interaction]
            
            # Search for ids in the sets
            potsetindex = None
            relsetindex = None
            
            for i, potidset in enumerate(int_models):

                # Search for set containing potid
                if potid in potidset:
                    if potsetindex is None:
                        potsetindex = i
                    else:
                        raise ValueError(f'{potid} found in multiple sets for {interaction}')
                
                # Search for set containing relid
                if relid in potidset:
                    if relsetindex is None:
                        relsetindex = i
                    else:
                        raise ValueError(f'{relid} found in multiple sets for {interaction}')

            # Add new set
            if potsetindex is None and relsetindex is None:
                if relid is None:
                    int_models.append([potid])
                else:
                    int_models.append([potid, relid])
                if verbose:
                    print(f'New set added to {interaction}')
            
            # Add potid to an existing set
            elif potsetindex is None:
                int_models[relsetindex].append(potid)
                if verbose:
                    print(f'potid added to existing set for {interaction}')

            # Add relid to an existing set
            elif relsetindex is None:
                if relid is not None:
                    int_models[potsetindex].append(relid)
                    if verbose:
                        print(f'related id added to existing set containing potid for {interaction}')
                else:
                    if verbose:
                        print(f'potid already in set for {interaction}')
            
            # Join sets if indices are different
            elif potsetindex != relsetindex:
                if potsetindex > relsetindex:
                    potset = int_models.pop(potsetindex)
                    relset = int_models.pop(relsetindex)
                else:
                    relset = int_models.pop(relsetindex)
                    potset = int_models.pop(potsetindex)
                int_models.append(potset + relset)
                if verbose:
                    print(f'existing sets now joined for {interaction}')
            else:

                if verbose:
                    print(f'potid and related id already in the same set for {interaction}')

def sort_related_models(self):
    """
    Sorts the related model dictionary by interactions and the contained sets
    by potential entry ids.
    """
    related_models = self.related_models

    sorted_related_models = {}

    # Iterate over sorted interactions
    for interaction in sorted(related_models.keys()):
        sets = related_models[interaction]

        # Sort each set
        for i in range(len(sets)):
            sets[i] = sorted(sets[i])

        # Sort the sets by the first pot id in each
        def sortkey(l):
            return l[0]
        sets = sorted(sets, key=sortkey)

        sorted_related_models[interaction] = sets

    # Replace related_models with the sorted version
    self.__related_models = sorted_related_models