from DataModelDict import DataModelDict as DM

from . import PotentialLAMMPSBuilder

class KimBuilder(PotentialLAMMPSBuilder):
    """
    PotentialLAMMPS builder class for pair_style kim with pair_style and
    pair_coeff lines of the form:
        
        pair_style kim kimid
        pair_coeff * * Sym1
        
    """
    def __init__(self, kimid=None, **kwargs):

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
    def kimid(self):
        "The KIM ID"
        return self.__kimid

    @kimid.setter
    def kimid(self, value):
        if value is not None:
            value = str(value)
        self.__kimid = value
        self.__pair_style_terms = [self.kimid]

    @property
    def pair_style_terms(self):
        return self.__pair_style_terms

    @pair_style_terms.setter
    def pair_style_terms(self, value):
        if value is not None:
            raise AttributeError("can't set attribute: set kimid value instead.")

    def buildpaircoeff(self):
        paircoeff = DM()
        paircoeff.append('term', DM([('symbols', 'True')]))
        
        return paircoeff 
    
    @property
    def supported_pair_styles(self):
        """tuple : The list of known pair styles that use this format."""
        return ('kim')