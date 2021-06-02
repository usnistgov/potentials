from DataModelDict import DataModelDict as DM

from . import PotentialLAMMPSBuilder
from ...tools import aslist

class EamBuilder(PotentialLAMMPSBuilder):
    """ 
    PotentialLAMMPS builder class for the classic eam style only, which uses
    pair_coeff lines of the form:
        
        pair_coeff 1 1 paramfile1
        pair_coeff 2 2 paramfile2

    Note: other EAM styles like eam/alloy, etc. should use ParamFileBuilder!
    """

    def __init__(self, paramfiles=None, **kwargs):
        """
        Class initializer

        Parameters
        ----------
        paramfiles : str or list, optional
            The name(s) of the potential's parameter file(s).  There should be
            one parameter file for each element model.
        **kwargs : any, optional
            Any other keyword parameters accepted by PotentialLAMMPSBuilder.
            Default values used by this class: units='metal' and
            atom_style='atomic'.
        """
        # Set default values for format
        kwargs['units'] = kwargs.get('units', 'metal')
        kwargs['atom_style'] = kwargs.get('atom_style', 'atomic')
        kwargs['pair_style'] = kwargs.get('pair_style', 'eam')

        # Call PotentialLAMMPS's init
        PotentialLAMMPSBuilder.__init__(self, **kwargs)
        
        # Set format-specific parameters
        self.paramfiles = paramfiles
    
    @property
    def paramfiles(self):
        """list : The names of the parameter files to use"""
        return self.__paramfiles

    @paramfiles.setter
    def paramfiles(self, value):
        if value is not None:
            value = aslist(value)
        self.__paramfiles = value

    def buildpaircoeff(self):
        """Builds the pair_coeff command lines"""
        if self.symbols is not None:
            symbols = self.symbols
        else:
            symbols = self.elements

        if len(symbols) != len(self.paramfiles):
            raise ValueError('a paramfile is needed for each symbol/element')

        paircoeffs = []
        for symbol, paramfile in zip(symbols, self.paramfiles):
            paircoeff = DM()
            paircoeff['interaction'] = DM([('symbol', [symbol, symbol])])
            paircoeff['term'] = DM([('file', paramfile)])
            paircoeffs.append(paircoeff)
        
        if len(paircoeffs) == 0:
            paircoeffs = paircoeffs[0]
        
        return paircoeffs

    @property
    def supported_pair_styles(self):
        """tuple : The list of known pair styles that use this format."""
        return ('eam',)