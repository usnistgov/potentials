# coding: utf-8
# Standard libraries
from typing import Optional, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# Local imports
from . import PotentialLAMMPSBuilder

class KimBuilder(PotentialLAMMPSBuilder):
    """
    PotentialLAMMPS builder class for pair_style kim with pair_style and
    pair_coeff lines of the form:
        
        pair_style kim kimid
        pair_coeff * * Sym1
    
    NOTE: This is for old versions of LAMMPS where kim was treated as a pair
    style.  For newer versions of LAMMPS that use kim commands use the
    PotentialLAMMPSKIM class instead.
    """
    def __init__(self,
                 kimid: Optional[str] = None,
                 **kwargs):
        """
        Class initializer

        Parameters
        ----------
        kimid : str, optional
            The KIM model id.
        id : str, optional
            A human-readable identifier to name the LAMMPS potential
            implementation.  Must be set in order to save to the database as
            the id is used as the potential's file name.
        key : str, optional
            A UUID4 code to uniquely identify the LAMMPS potential
            implementation.  If not specified, a new UUID4 code is
            automatically generated.
        url : str, optional
            A URL where an online copy of the record can be found.
        potid : str, optional
            A human-readable identifier to refer to the conceptual potential
            model that the potential is based on.  This should be shared by
            alternate implementations of the same potential.
        potkey : str, optional
            A UUID4 code to uniquely identify the conceptual potential model.
            This should be shared by alternate implementations of the same
            potential. If not specified, a new UUID4 code is automatically
            generated.
        poturl : str, optional
            A URL where an online copy of the potential model record can be
            found.
        units : str, optional
            The LAMMPS units option to use.  Default value is 'metal'.
        atom_style : str, optional
            The LAMMPS atom_style option to use. Default value is 'atomic'.
        pair_style : str, optional
            The LAMMPS pair_style option to use.
        pair_style_terms :  list, optional
            Any other terms that appear on the pair_style line (like cutoff)
            if needed.
        status : str, optional
            Indicates if the implementation is 'active' (valid and current),
            'superseded' (valid, but better ones exist), or 'retracted'
            (invalid). Default value is 'active'.
        comments : str, optional
            Descriptive information about the potential.
        dois : str or list, optional
            Any DOIs associated with the potential.
        allsymbols : bool, optional
            Flag indicating if the coefficient lines must be defined for every
            particle model in the potential even if those particles are not
            used.  Default value is False as most pair_styles do not require
            this.
        elements : str or list, optional
            The elemental symbols associated with each particle model if the
            particles represent atoms.
        masses : float or list, optional
            The masses of each particle.  Optional if elements is given as
            standard values can be used.
        charges : float or list, optional
            The static charges to assign to each particle, if the model calls
            for it.
        symbols : str or list, optional
            The symbols used to identify each unique particle model. Optional
            if elements is given and the particle symbols are the same as the
            elemental symbols.
        command_terms : list, optional
            Allows any other LAMMPS command lines that must be set for the
            potential to work properly to be set.  Each command line should be
            given as a list of terms, and multiple command lines given as a
            list of lists.
        artifacts : potential.Artifact or list, optional
            Artifact objects detailing any associated parameter or data files
            and the URLs where they can be downloaded from.
        """
        # Set default values for format
        kwargs['pair_style'] = kwargs.get('pair_style', 'kim')
        
        # Remove pair_style_terms
        pair_style_terms = kwargs.pop('pair_style_terms', None)
        assert pair_style_terms is None

        # Call PotentialLAMMPS's init
        PotentialLAMMPSBuilder.__init__(self, **kwargs)

        # Set format-specific parameters
        self.kimid = kimid

    @property
    def kimid(self) -> Optional[str]:
        "str: The KIM model ID"
        return self.__kimid

    @kimid.setter
    def kimid(self, value: Optional[str]):
        if value is not None:
            value = str(value)
        self.__kimid = value
        self.__pair_style_terms = [self.kimid]

    @property
    def pair_style_terms(self) -> list:
        """list : All extra terms to include in the pair_style command line"""
        return self.__pair_style_terms

    @pair_style_terms.setter
    def pair_style_terms(self, value: Union[str, list, None]):
        if value is not None:
            raise AttributeError("can't set attribute: set kimid value instead.")

    def buildpaircoeff(self) -> str:
        """
        Builds the LAMMPS pair_coeff command lines.
        
        Returns
        -------
        str
            The LAMMPS pair_coeff command line.
        """
        paircoeff = DM()
        paircoeff.append('term', DM([('symbols', True)]))
        
        return paircoeff 
    
    @property
    def supported_pair_styles(self) -> tuple:
        """tuple : The list of known pair styles that use this format."""
        return (
            'kim',
        )