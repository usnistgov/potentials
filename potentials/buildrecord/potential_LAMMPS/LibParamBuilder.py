from DataModelDict import DataModelDict as DM

from . import PotentialLAMMPSBuilder

class LibParamBuilder(PotentialLAMMPSBuilder):
    """
    PotentialLAMMPS builder class for styles based on potential library and
    parameter files with pair_coeff lines of the form:
        
        pair_coeff * * libfile Sym1 Sym2 paramfile Sym1 Sym2
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

        # Call PotentialLAMMPS's init
        PotentialLAMMPSBuilder.__init__(self, **kwargs)
        
        # Set format-specific parameters
        self.libfile = libfile
        self.paramfile = paramfile
    
    @property
    def libfile(self):
        """str : The name of the library file to use"""
        return self.__libfile

    @libfile.setter
    def libfile(self, value):
        if value is not None:
            value = str(value)
        self.__libfile = value

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
        if self.libfile is None:
            raise ValueError('libfile must be set')
        if self.paramfile is None:
            paramfile = 'NULL'
        else:
            paramfile = self.paramfile

        paircoeff = DM()
        paircoeff.append('term', DM([('file', self.libfile)]))
        paircoeff.append('term', DM([('option', self.symbollist)]))
        paircoeff.append('term', DM([('file', paramfile)]))
        paircoeff.append('term', DM([('symbols', 'True')]))
        
        return paircoeff

    @property
    def supported_pair_styles(self):
        """tuple : The list of known pair styles that use this format."""
        return (
            'meam', 'meam/c',
        )