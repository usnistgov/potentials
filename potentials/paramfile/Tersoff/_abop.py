from io import StringIO
from math import sqrt, exp

import numpy as np
import pandas as pd

from potentials.tools import atomic_number

@classmethod
def abop(cls, fname, pair_style=None):
    """
    Reads in parameters from the Albe-Nordlund ABOP format to generate
    the LAMMPS Tersoff parameters.

    Parameters
    ----------
    fname : path-like object
        The name/path of the parameter file to read in.  See the examples
        for file format information.
    pair_style : str, optional
        The specific LAMMPS tersoff pair_style, which can be None,
        'tersoff' or 'tersoff/zbl'.  If None (default) then the pair_style
        will be inferred based on if the extra zbl fields are included in
        the parameter file.
    """
    # Read abop parameters from a file
    abop_params, mod_params = read_abop(fname)

    # Find the list of all element symbol models
    symbols = []
    for el1 in abop_params.el1:
        if el1 not in symbols:
            symbols.append(el1)
    
    # Identify the default pair_style to use
    if pair_style is None:
        if 'bf' in abop_params:
            pair_style = 'tersoff/zbl'
        else:
            pair_style = 'tersoff'
    
    # Initialize the Tersoff object and extract its params
    obj = cls(symbols, pair_style=pair_style)
    tersoff = obj.params

    # Loop over each abop_params row
    for index in abop_params.index:
        abopi = abop_params.loc[index]
        el1 = abopi.el1
        el2 = abopi.el2

        twobody = abop_to_tersoff_2body(abopi, pair_style=pair_style)
        match2body = (tersoff.e2 == tersoff.e3) & ( ( (tersoff.e1 == el1) & (tersoff.e2 == el2) ) | ( (tersoff.e1 == el2) & (tersoff.e2 == el1) ) )
        for key in twobody:
            tersoff.loc[match2body, key] = twobody[key]

        threebody = abop_to_tersoff_3body(abopi, pair_style=pair_style)
        match3body = ( (tersoff.e1 == el1) & (tersoff.e3 == el2) ) | ( (tersoff.e1 == el2) & (tersoff.e3 == el1) )
        for key in threebody:
            tersoff.loc[match3body, key] = threebody[key]

    # Fill in element numbers for ZBL
    if pair_style == 'tersoff/zbl':
        for index in tersoff.index:
            tersoff.loc[index, 'Z_i'] = atomic_number(tersoff.loc[index, 'e1'])
            tersoff.loc[index, 'Z_j'] = atomic_number(tersoff.loc[index, 'e2'])

    # Loop over 3-body modification parameters
    for index in mod_params.index:
        mod = mod_params.loc[index]
        key, e1, e2, e3, val = mod.tolist()
        matchmod = ( (tersoff.e1 == e1) & (tersoff.e2 == e2) & (tersoff.e3 == e3) )
        if key == 'α':
            tersoff.loc[matchmod, 'lambda3'] = val
        elif key == 'ω':
            tersoff.loc[matchmod, 'gamma'] *= val

    return obj

def abop_to_tersoff_2body(abop, pair_style='tersoff'):
    """Transform the 2-body abop params to LAMMPS format"""

    # Extract ABOP parameters
    β = abop.β
    S = abop.S
    D0 = abop.D0
    r0 = abop.r0
    
    # Convert to Tersoff paramters
    tersoff = {}
    tersoff['lambda2'] = λ2 = β * sqrt(2 / S)
    tersoff['B'] = S * D0 / (S - 1) * exp(λ2 * r0)
    tersoff['lambda1'] = λ1 = β * sqrt(2 * S)
    tersoff['A'] = D0 / (S - 1) * exp(λ1 * r0)

    return tersoff

def abop_to_tersoff_3body(abop, pair_style='tersoff'):
    """Transform the 3-body abop params to LAMMPS format"""
    # Map abop to tersoff
    tersoff = {}
    tersoff['gamma'] = abop.γ * abop.ω
    tersoff['lambda3'] = abop.α
    tersoff['costheta0'] = - abop.h
    tersoff['c'] = abop.c
    tersoff['d'] = abop.d
    tersoff['Rcut'] = abop.R
    tersoff['D'] = abop.D

    if pair_style == 'tersoff/zbl' and 'bf' in abop:
        tersoff['ZBLcut'] = abop.rf
        tersoff['ZBLexpscale'] = abop.bf
    
    return tersoff



abop_keys: list = [
    'el1', 'el2', 'D0', 'r0', 'β', 'S', 'γ', 'c', 'd', 'h', 'R', 'D', 'α',
    'ω', 'bf', 'rf']
"""list: All keys recognized as abop parameters"""

def read_abop(fname):
    """
    Read an abop file and extract all parameters within it.
    """
    
    def to_numeric_ignore(series):
        """Wrap pd.to_numeric to avoid errors"""
        try:
            return pd.to_numeric(series)
        except ValueError as e:
            return series

    # Read in file and split contents into 2-body and 3-body tables
    with open(fname) as f:
        contents = f.read()
    if '3 body mods' in contents:
        table1, table2 = contents.split('3 body mods')
    else:
        table1 = contents
        table2 = ''
    
    # Read in 2-body parameter table, transform and convert to numeric values
    read_kwargs = dict(sep='\s+', comment='#', header=None, index_col=0)
    abop = pd.read_csv(StringIO(table1), **read_kwargs).T.reset_index(drop=True)
    abop = abop.apply(to_numeric_ignore, axis=0)

    try:
        mods = pd.read_csv(StringIO(table2), sep='\s+', comment='#', header=None)
    except pd.errors.EmptyDataError:
        mods = pd.DataFrame()
    
    # Check for unknown parameter names
    for key in abop:
        if key not in abop_keys:
            raise ValueError(f'Unknown parameter {key} found in abop file')
    
    # Fill in optional parameter values
    if 'ω' not in abop:
        abop['ω'] = np.ones(len(abop))
    if 'α' not in abop:
        abop['α'] = np.zeros(len(abop))

    # Check for missing parameters
    for key in abop_keys[:-2]:
        if key not in abop:
            raise ValueError(f'Parameter {key} not found in abop file')
    
    # Check for missing ZBL parameters
    if 'bf' in abop and 'rf' not in abop:
        raise ValueError('rf required if bf is given')
    if 'rf' in abop and 'bf' not in abop:
        raise ValueError('bf required if rf is given')

    return abop, mods