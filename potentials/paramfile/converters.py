# coding: utf-8
# Standard libraries
import io
from typing import Optional, Union

# https://numpy.org/
import numpy as np

# Local imports
from ..tools import aslist
from . import EAM, EAMAlloy, EAMFS, ADP

def eam_to_eam_alloy(eam: Union[str, io.IOBase, EAM, list],
                     symbol: Union[str, list],
                     numr: Optional[int] = None,
                     cutoffr: Optional[float] = None,
                     deltar: Optional[float] = None,
                     numrho: Optional[int] = None,
                     cutoffrho: Optional[float] = None,
                     deltarho: Optional[float] = None,
                     header: Optional[str] = None) -> EAMAlloy:
    """
    Converts one or more parameter files in the eam format to the eam/alloy
    format.
    
    Parameters
    ----------
    eam : path, file-like object, potentials.paramfile.EAM, or list
        One or more parameter files in the LAMMPS pair_style eam funcfl format.
    symbol : str or list
        The model symbol(s) to associate with the parameter file(s).
    numr : int, optional
        The number of r tabulation points to use in the alloy file.  If given,
        then cutoffr and/or deltar must be given.  If not given, will use the r
        tabulation points from the eam parameter file with the largest r cutoff.
    cutoffr : float, optional
        The r cutoff value to use in the alloy file.  Will be used in
        tabulating r values if numr is given and deltar is not.
    deltar : float, optional
        The r step size to use for the r tabulation points in the alloy file.
        If given, numr must also be given.
    numrho : int, optional
        The number of rho tabulation points to use in the alloy file. If given,
        then cutoffrho and/or deltarho must be given.  If not given, will use
        the rho tabulation points from the eam parameter file with the largest
        rho cutoff.
    cutoffrho : float, optional
        The rho cutoff value to use in the alloy file.  Will be used in
        tabulating rho values if numrho is given and deltarho is not.
    deltarho : float, optional
        The rho step size to use for the r tabulation points in the alloy file.
        If given, numrho must also be given.
    header : str, optional
        Allows for a new header to be specified as the format is different.  If
        not given, the new header will be composed of the headers from the
        first three original eam files.

    Returns
    -------
    potentials.paramfile.EAMAlloy
        The eam funcfl parameter files converted and combined into an eam/alloy
        setfl file representation. 
    """
    # Convert eam and symbol to lists and check len
    eams = aslist(eam)
    symbols = aslist(symbol)
    if len(eams) != len(symbols):
        raise ValueError('Lengths of eam files and symbols does not match')
    
    # Set conversion constants
    hartree = 27.2
    bohr = 0.529
    
    # Load parameter files
    for i in range(len(eams)):
        if not isinstance(eams[i], EAM):
            eams[i] = EAM(eams[i])
    
    alloy = EAMAlloy()
    
    if header is None:
        header = ''
        for i, eam in enumerate(eams):
            header += eam.header + '\n'
            if i == 2:
                break
    alloy.header = header

    # Set r
    if numr is None:
        numr = 0
        for eam in eams:
            if eam.numr > numr:
                numr = eam.numr
                cutoffr = eam.cutoffr
                deltar = eam.deltar
    alloy.set_r(num=numr, cutoff=cutoffr, delta=deltar)
    
    # Set rho
    if numrho is None:
        numrho = 0
        for eam in eams:
            if eam.numrho > numrho:
                numrho = eam.numrho
                cutoffrho = eam.cutoffrho
                deltarho = eam.deltarho
    alloy.set_rho(num=numrho, cutoff=cutoffrho, delta=deltarho)
    
    # Loop over eam files
    for eam, symbol in zip(eams, symbols):
        
        # Check r values
        if np.allclose(eam.r, alloy.r):
            r = None
        else:
            r = alloy.r
        
        # Check rho values
        if np.allclose(eam.rho, alloy.rho):
            rho = None
        else:
            rho = alloy.rho
        
        # Copy over symbol info
        alloy.set_symbol_info(symbol, **eam.symbol_info())
        
        # Copy over F(rho)
        alloy.set_F_rho(symbol, table=eam.F_rho(rho=rho))
        
        # Copy over rho(r)
        alloy.set_rho_r(symbol, table=eam.rho_r(r=r))
        
        # Copy over elemental r*phi(r)
        alloy.set_rphi_r(symbol, table=eam.rphi_r(r=r))
        
    # Calculate cross r*phi(r) values
    for i in range(len(symbols)):
        for j in range(i):
            zi = eams[i].z_r(r=alloy.r)
            zj = eams[j].z_r(r=alloy.r)
            rphi_r = hartree * bohr * zi * zj
            alloy.set_rphi_r([symbols[i], symbols[j]], table=rphi_r)
            
    return alloy

def eam_alloy_to_eam_fs(alloy: EAMAlloy) -> EAMFS:
    """
    Converts a parameter file in the eam/alloy format to the eam/fs format.
    
    Parameters
    ----------
    alloy : path, file-like object, or potentials.paramfile.EAMAlloy
        A parameter file in the LAMMPS pair_style eam/alloy setfl format.
    
    Returns
    -------
    potentials.paramfile.EAMFS
        The eam/alloy setfl parameter file converted and combined into an
        eam/fs setfl file representation.
    """
    # Load parameter file
    if not isinstance(alloy, EAMAlloy):
        alloy = EAMAlloy(alloy)
    
    # Initialize fs object
    fs = EAMFS()
    
    # Copy over header
    fs.header = alloy.header

    # Copy over r
    fs.set_r(num=alloy.numr, cutoff=alloy.cutoffr, delta=alloy.deltar)

    # Copy over rho
    fs.set_rho(num=alloy.numrho, cutoff=alloy.cutoffrho, delta=alloy.deltarho)
    
    for i, symbol in enumerate(alloy.symbols):
        
        # Copy over symbol info
        fs.set_symbol_info(**alloy.symbol_info(symbol))
    
    for i, symbol in enumerate(alloy.symbols):
        
        # Copy over F(rho)
        fs.set_F_rho(symbol, table=alloy.F_rho(symbol))
        
        # Copy over rho(r)
        for symbol2 in alloy.symbols:
            symbolpair = [symbol, symbol2] # OR REVERSED?
            fs.set_rho_r(symbolpair, table=alloy.rho_r(symbol))
    
        # Copy over r*phi(r)
        for symbol2 in alloy.symbols[:i+1]:
            symbolpair = [symbol, symbol2]
            fs.set_rphi_r(symbolpair, table=alloy.rphi_r(symbolpair))
    
    return fs

def eam_alloy_to_adp(alloy: EAMAlloy) -> ADP:
    """
    Converts a parameter file in the eam/alloy format to the adp format.
    NOTE: the u(r) and w(r) tables are automatically set to all zeros.
    
    Parameters
    ----------
    alloy : path, file-like object, or potentials.paramfile.EAMAlloy
        A parameter file in the LAMMPS pair_style eam/alloy setfl format.
    
    Returns
    -------
    potentials.paramfile.ADP
        The eam/alloy setfl parameter file converted and combined into an
        adp setfl file representation.
    """
    # Load parameter file
    if not isinstance(alloy, EAMAlloy):
        alloy = EAMAlloy(alloy)
    
    # Initialize fs object
    adp = ADP()
    
    # Copy over header
    adp.header = alloy.header

    # Copy over r
    adp.set_r(num=alloy.numr, cutoff=alloy.cutoffr, delta=alloy.deltar)

    # Copy over rho
    adp.set_rho(num=alloy.numrho, cutoff=alloy.cutoffrho, delta=alloy.deltarho)
    
    for i, symbol in enumerate(alloy.symbols):
        
        # Copy over symbol info
        adp.set_symbol_info(**alloy.symbol_info(symbol))
    
    for i, symbol in enumerate(alloy.symbols):
        
        # Copy over F(rho)
        adp.set_F_rho(symbol, table=alloy.F_rho(symbol))
        
        # Copy over rho(r)
        adp.set_rho_r(symbol, table=alloy.rho_r(symbol))
    
        # Copy over r*phi(r)
        for symbol2 in alloy.symbols[:i+1]:
            symbolpair = [symbol, symbol2]
            adp.set_rphi_r(symbolpair, table=alloy.rphi_r(symbolpair))
            
            # Set u(r) and w(r) to all zeros
            adp.set_u_r(symbolpair, table=np.zeros_like(adp.r))
            adp.set_w_r(symbolpair, table=np.zeros_like(adp.r))
    
    return adp
