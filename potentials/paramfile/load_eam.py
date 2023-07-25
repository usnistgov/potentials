# coding: utf-8
# Standard libraries
import io
from typing import Optional, Union

# Local imports
from . import EAM, EAMAlloy, EAMFS, ADP

def load_eam(f: Union[str, io.IOBase],
             style: Optional[str] = None) -> Union[EAM, EAMAlloy, EAMFS, ADP]:
    """
    Loads a LAMMPS-compatible EAM parameter file.
    
    Parameters
    ----------
    f : path-like object or file-like object
        The parameter file to read in, either as a file path or as an open
        file-like object.
    style : str, optional
        The parameter file format.  'eam' will load funcfl files for the LAMMPS
        eam pair_style.  'eam/alloy' or 'alloy' will load setfl files for the
        LAMMPS eam/alloy pair_style.  'eam/fs' or 'fs' will load setfl files for
        the eam/fs pair_style.  'ap' will load setfl files for the adp pair_style.
        If not given, will attempt to load the file using the different styles.
        
    Returns
    -------
    EAM, EAMAlloy, EAMFS or ADP
        The loaded parameter file content.
    """
    
    # Shortcut to classes for known styles
    if style == 'eam':
        return EAM(f)
    elif style == 'eam/alloy' or style == 'alloy':
        return EAMAlloy(f)
    elif style == 'eam/fs' or style == 'fs':
        return EAMFS(f)
    elif style == 'adp':
        return ADP(f)
    elif style is not None:
        raise ValueError('Unknown style')
    
    # Check if f is a file
    if hasattr(f, 'readlines'):
        closefile = False
    else:
        f = open(f, encoding='UTF-8')
        closefile = True
    
    def test_style(f, cls):
        """Try loading as cls, reset f position if it fails"""
        try:
            obj = cls(f)
        except:
            f.seek(0)
        else:
            if closefile:
                f.close()
            return obj
    
    # Test if eam
    obj = test_style(f, EAM)
    if obj is not None:
        return obj
    
    # Test if eam/alloy
    obj = test_style(f, EAMAlloy)
    if obj is not None:
        return obj
    
    # Test if eam/fs
    obj = test_style(f, EAMFS)
    if obj is not None:
        return obj
    
    # Test if adp
    obj = test_style(f, ADP)
    if obj is not None:
        return obj

    if closefile:
        f.close()
    raise ValueError('Failed to load as any known style')    