# coding: utf-8
# Standard libraries
from typing import Tuple, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://scipy.org/
from scipy.special import comb

# Local imports
from . import PotentialLAMMPSBuilder
from ...tools import aslist

class PairBuilder(PotentialLAMMPSBuilder):
    """
    PotentialLAMMPS builder class for true pair styles with coefficients set
    directly by the pair_coeff lines:
        
        pair_coeff 1 1 a11 b11 ...
        pair_coeff 1 2 a12 b12 ...
        ...
    """

    def __init__(self,
                 interactions: Union[dict, list, None] = None,
                 **kwargs):
        """
        Class initializer

        Parameters
        ----------
        interactions : dict or list of dict, optional
            Each unique pair interaction is characterized by a dict containing
            symbols=two element model symbols, and terms=list of pair_coeff terms.
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
    def interactions(self) -> Tuple[dict]:
        """tuple of dict: The pair interaction parameters"""
        return tuple(self.__interactions)

    def set_interaction(self,
                        symbols: Union[str, list, None] = None,
                        terms: Union[str, list, None] = None):
        """
        Function allowing for symbol-symbol interactions to be defined one at
        a time.
        
        Parameters
        ----------
        symbols : list, optional
            The pair of symbols that the interaction is defined for.  Not
            required if the potential only models one interaction.
        terms : list, optional
            The pair_coeff command line terms for the interaction.
        """
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

    def buildpaircoeff(self) -> str:
        """
        Builds the LAMMPS pair_coeff command lines.
        
        Returns
        -------
        str
            The LAMMPS pair_coeff command line.
        """
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
    def supported_pair_styles(self) -> tuple:
        """tuple : The list of known pair styles that use this format."""
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