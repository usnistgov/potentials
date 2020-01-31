from DataModelDict import DataModelDict as DM

from scipy.special import comb

from . import PotentialLAMMPSBuilder
from ..tools import aslist

class PairBuilder(PotentialLAMMPSBuilder):
    """
    PotentialLAMMPS builder class for true pair styles with coefficients set
    directly by the pair_coeff lines:
        
        pair_coeff 1 1 a11 b11 ...
        pair_coeff 1 2 a12 b12 ...
        ...
    """

    def __init__(self, interactions=None, **kwargs):
        """
        Class initializer

        Parameters
        ----------
        interactions : dict or list of dict, optional
            Each unique pair interaction is characterized by a dict containing
            symbols=two element model symbols, and terms=list of pair_coeff terms.
        **kwargs : any, optional
            Any other keyword parameters accepted by PotentialLAMMPSBuilder.
            Default values used by this class: units='metal' and
            atom_style='atomic'.
        """
        # Set default values for format

        # Call PotentialLAMMPS's init
        PotentialLAMMPSBuilder.__init__(self, **kwargs)
        
        # Set format-specific parameters
        self.__interactions = []
        if interactions is not None:
            interactions = aslist(interactions)
        else:
            interactions = []
        if len(interactions) > 0:
            for interaction in interactions:
                assert interaction.get('symbols', None) is not None, 'symbols must be given with multiple interactions'
        for interaction in interactions:
            self.set_interaction(**interaction)
    
    @property
    def interactions(self):
        """tuple of dict: The pair interaction parameters"""
        return tuple(self.__interactions)

    def set_interaction(self, symbols=None, terms=None):
        
        if terms is not None:
            terms = aslist(terms)
        else:
            raise ValueError('No interaction terms found')
        if len(terms) == 0:
            raise ValueError('No interaction terms found')

        if self.symbols is not None:
            potsymbols = self.symbols
        else:
            potsymbols = self.elements

        # Only one set allowed without symbols
        if symbols is None:
            self.__interactions = [{'terms':terms}]
        
        # Reset if new interaction includes symbols
        elif len(self.interactions) == 1 and 'symbols' not in self.interactions[0]:
            self.__interactions = []
            self.set_interaction(symbols=symbols, terms=terms)
        
        # Append/replace interaction with symbols
        else:
            symbols = sorted(aslist(symbols))
            if len(symbols) != 2:
                raise ValueError('Interaction symbols must be given in pairs')
            for symbol in symbols:
                if potsymbols is None or symbol not in potsymbols:
                    raise ValueError(f'symbol {symbol} not in symbols/elements')
            
            symbolstr = '-'.join(symbols)
            match = False
            for i in range(len(self.interactions)):
                interaction = self.interactions[i]
                setsymbolstr = '-'.join(interaction['symbols'])
                if symbolstr == setsymbolstr:
                    match = True
                    break
            if match:
                self.__interactions.pop(i)
            self.__interactions.append({'symbols':symbols, 'terms':terms})

    def buildpaircoeff(self):
        
        # Universal interactions: ignore symbols
        if len(self.interactions) == 1 and 'symbols' not in self.interactions[0]:
            paircoeff = DM()
            for term in self.interactions[0]['terms']:
                if isinstance(term, (int, float)):
                    paircoeff.append('term', DM([('parameter', term)]))
                else:
                    paircoeff.append('term', DM([('option', str(term))]))
            
            return paircoeff

        # Interactions with symbols
        else:
            paircoeffs = []
            # Verify correct number of interactions
            if self.symbols is not None:
                potsymbols = self.symbols
            else:
                potsymbols = self.elements
            expected = comb(len(potsymbols), 2, exact=True, repetition=True)
            if len(self.interactions) != expected:
                raise ValueError(f'Not all interactions set: expected {expected}, found {len(self.interactions)}')
        
            # Build
            for interaction in self.interactions:
                paircoeff = DM()
                paircoeff['interaction'] = DM([('symbol', interaction['symbols'])])
                for term in interaction['terms']:
                    if isinstance(term, (int, float)):
                        paircoeff.append('term', DM([('parameter', term)]))
                    else:
                        paircoeff.append('term', DM([('option', str(term))]))
                paircoeffs.append(paircoeff)

            if len(paircoeffs) == 1:
                paircoeffs = paircoeffs[0]
        
            return paircoeffs

    @property
    def supported_pair_styles(self):
        return (
            'atm',
            'awpmd/cut',
            'beck',
            'body/nparticle', 'body/rounded/polygon', 'body/rounded/polyhedron',
            'born', 'born/coul/long', 'born/coul/msm', 'born/coul/wolf', 'born/coul/dsf',
            'born/coul/dsf/cs', 'born/coul/long/cs', 'born/coul/wolf/cs', 'buck/coul/long/cs', 'coul/long/cs', 'coul/wolf/cs', 'lj/cut/coul/long/cs',
            'brownian', 'brownian/poly',
            'buck', 'buck/coul/cut', 'buck/coul/long', 'buck/coul/msm', 'buck/long/coul/long',
            'lj/mdf', 'buck/mdf', 'lennard/mdf',
            'buck6d/coul/gauss/dsf', 'buck6d/coul/gauss/long',
            'colloid',
            'cosine/squared',
            'coul/cut', 'coul/debye', 'coul/dsf', 'coul/long', 'coul/msm', 'coul/streitz', 'coul/wolf', 'tip4p/cut', 'tip4p/long',
            'coul/diel', 'coul/shield',
            'lj/cut/soft', 'lj/cut/coul/cut/soft', 'lj/cut/coul/long/soft', 'lj/cut/tip4p/long/soft', 'lj/charmm/coul/long/soft',
            'lj/class2/soft', 'lj/class2/coul/cut/soft', 'lj/class2/coul/long/soft', 'coul/cut/soft', 'coul/long/soft', 'tip4p/long/soft', 'morse/soft',
            'dpd', 'dpd/tstat', 'dpd/fdt', 'dpd/fdt/energy',
            'dsmc',
            'e3b',
            'edpd', 'mdpd', 'mdpd/rhosum', 'tdpd',
            'eff/cut',
            'gauss', 'gauss/cut',
            'gayberne',
            'gran/hooke', 'gran/hooke/history', 'gran/hertz/history',
            'granular',
            'hbond/dreiding/lj', 'hbond/dreiding/morse',
            'line/lj',
            'lj/charmm/coul/charmm', 'lj/charmm/coul/charmm/implicit', 'lj/charmm/coul/long', 'lj/charmm/coul/msm', 'lj/charmmfsw/coul/charmmfsh', 'lj/charmmfsw/coul/long',
            'lj/class2', 'lj/class2/coul/cut', 'lj/class2/coul/long',
            'lj/cubic',
            'lj/cut', 'lj/cut/coul/cut', 'lj/cut/coul/debye', 'lj/cut/coul/dsf', 'lj/cut/coul/long', 'lj/cut/coul/msm', 'lj/cut/coul/wolf', 'lj/cut/tip4p/cut', 'lj/cut/tip4p/long',
            'lj/cut/dipole/cut',  'lj/sf/dipole/sf',  'lj/cut/dipole/long',  'lj/long/dipole/long', 
            'thole', 'lj/cut/thole/long',
            'lj/expand', 'lj/expand/coul/long',
            'lj/gromacs', 'lj/gromacs/coul/gromacs',
            'lj/long/coul/long', 'lj/long/tip4p/long',
            'lj/sdk', 'lj/sdk/coul/long', 'lj/sdk/coul/msm',
            'lj/smooth', 'lj/smooth/linear',
            'lj/switch3/coulgauss/long',
            'lj96/cut',
            'lubricate', 'lubricate/poly', 'lubricateU', 'lubricateU/poly',
            'mie/cut',
            'mm3/switch3/coulgauss/long',
            'momb',
            'morse', 'morse/smooth/linear',
            'nm/cut', 'nm/cut/coul/cut', 'nm/cut/coul/long',
            'oxdna/excv', 'oxdna/stk', 'oxdna/hbond', 'oxdna/xstk', 'oxdna/coaxstk',
            'oxdna2/excv', 'oxdna2/stk', 'oxdna2/hbond', 'oxdna2/xstk', 'oxdna2/coaxstk', 'oxdna2/dh'
            'oxrna2/excv', 'oxrna2/stk', 'oxrna2/hbond', 'oxrna2/xstk', 'oxrna2/coaxstk',  'oxrna2/dh', 
            'peri/pmb', 'peri/lps', 'peri/ves', 'peri/eps',
            'resquared',
            'sdpd/taitwater/isothermal',
            'smd/hertz', 'smd/tlsph', 'smd/tri_surface', 'smd/ulsph',
            'soft',
            'sph/heatconduction', 'sph/idealgas', 'sph/lj', 'sph/rhosum', 'sph/taitwater', 'sph/taitwater/morris',
            'spin/dipole/cut', 'spin/dipole/long', 'spin/dmi', 'spin/exchange', 'spin/magelec', 'spin/neel',
            'srp',
            'tri/lj',
            'ufm',
            'yukawa', 'yukawa/colloid',
            'zbl',
        )