from DataModelDict import DataModelDict as DM

from . import PotentialLAMMPSBuilder

class EimBuilder(PotentialLAMMPSBuilder):
    """
    PotentialLAMMPS builder class for styles similar to eam with pair_coeff lines
    of the form:
        
        pair_coeff * * Sym1 Sym2 paramfile Sym1 Sym2
    """

    def __init__(self, libfile=None, paramfile=None, **kwargs):
        """
        Class initializer

        Parameters
        ----------
        libfile : str, optional
            The name of the potential's library file.
        paramfile : str, optional
            The name of the potential's parameter file.
        **kwargs : any, optional
            Any other keyword parameters accepted by PotentialLAMMPSBuilder.
            Default values used by this class: units='metal' and
            atom_style='atomic'.
        """
        # Set default values for format
        kwargs['units'] = kwargs.get('units', 'metal')
        kwargs['atom_style'] = kwargs.get('atom_style', 'atomic')
        kwargs['allsymbols'] = kwargs.get('allsymbols', True)

        # Call PotentialLAMMPS's init
        PotentialLAMMPSBuilder.__init__(self, **kwargs)
        
        # Set format-specific parameters
        self.paramfile = paramfile
    
    @property
    def paramfile(self):
        """str : The name of the parameter file to use"""
        return self.__paramfile

    @paramfile.setter
    def paramfile(self, value):
        if value is not None:
            value = str(value)
        self.__paramfile = value

    def buildpaircoeff(self):
        """Builds the pair_coeff command lines"""
        if self.paramfile is None:
            raise ValueError('paramfile must be set')

        paircoeff = DM()
        paircoeff.append('term', DM([('option', self.symbollist)]))
        paircoeff.append('term', DM([('file', self.paramfile)]))
        paircoeff.append('term', DM([('symbols', 'True')]))
        
        return paircoeff

    @property
    def supported_pair_styles(self):
        """tuple : The list of known pair styles that use this format."""
        return (
            'eim',
        )