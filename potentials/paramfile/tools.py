# Standard libraries
from typing import Optional, Union

# https://numpy.org/
import numpy as np

# https://scipy.org/
from scipy.optimize import minimize

class IdealFCC():
    """Class representing details for an ideal fcc crystal"""

    @property
    def normalized_dmags(self):
        """numpy.ndarray: The normalized distances to all fcc neighbor shells out to 6*alat"""
        return np.array([
            0.70710678118655,1.00000000000000,1.22474487139158,1.41421356237309,
            1.58113883008418,1.73205080756887,1.87082869338697,2.00000000000000,
            2.12132034355964,2.23606797749979,2.34520787991171,2.44948974278317,
            2.54950975679639,2.73861278752583,2.82842712474619,2.91547594742265,
            3.00000000000000,3.08220700148448,3.16227766016837,3.24037034920393,
            3.31662479035540,3.39116499156263,3.46410161513775,3.53553390593273,
            3.60555127546398,3.67423461417476,3.74165738677394,3.80788655293195,
            3.93700393700590,4.00000000000000,4.06201920231798,4.12310562561766,
            4.18330013267037,4.24264068711928,4.30116263352131,4.35889894354067,
            4.41588043316392,4.47213595499958,4.52769256906870,4.58257569495584,
            4.63680924774785,4.69041575982343,4.74341649025256,4.84767985741632,
            4.89897948556635,4.94974746830583,5.00000000000000,5.04975246918103,
            5.09901951359278,5.14781507049350,5.19615242270663,5.24404424085075,
            5.33853912601565,5.38516480713450,5.43139024560010,5.47722557505166,
            5.52268050859363,5.61248608016091,5.65685424949238,5.70087712549569,
            5.74456264653802,5.78791845139511,5.83095189484530,5.87367006223536,
            5.91607978309961,5.95818764390649,6.00000000000000])

    @property
    def counts(self):
        """numpy.ndarray: The number of atoms in all fcc neighbor shells out to 6*alat"""
        return np.array([
            12,6,24,12,24,8,48,6,36,24,24,24,72,48,12,48,30,72,24,48,24,48,8,84,24,
            96,48,24,96,6,96,48,48,36,120,24,48,24,48,48,120,24,120,96,24,108,30,
            48,72,72,32,144,96,72,72,48,120,144,12,48,48,168,48,96,48,48,30])

    def dmags(self,
              alat: float = 1.0,
              cutoffr: Optional[float] = None,
              eam = None):
        """
        Returns neighbor shell distances and number of atoms in each neighbor shell.

        Parameters
        ----------
        alat : float
            The lattice constant to scale the data by.  Default value is 1.0, i.e.
            no lattice scaling.
        cutoffr : float, optional
            The r cutoff distance beyond which neighbor positions will be excluded.
            If None (default) then the max cutoff of 6*alat is used.  Note that
            larger cutoffs are not allowed as the table only goes to 6*alat.
        eam : EAMAlloy, EAMFS, ADP
            An EAM potential parameter file builder. If given and cutoffr is not
            given, cutoffr will be taken from the set value.

        Returns
        -------
        dmags : numpy.ndarray
            The magnitude distances to each fcc neighbor shell.
        counts : numpy.ndarray
            The number of atoms in each fcc neighbor shell.    
        """
        # Define the fcc dmags and counts tables out to 6 * alat
        dmags = alat * self.normalized_dmags
        counts = self.counts

        # Extract cutoffr from eam if given
        if eam is not None and cutoffr is None:
            cutoffr = eam.cutoffr

        # Trim arrays by the cutoff
        if cutoffr is not None:
            if cutoffr > 6 * alat:
                raise ValueError(f'only cutoffs <= 6 * alat = {6 * alat} are supported')

            incutoff = dmags <= cutoffr
            dmags = dmags[incutoff]
            counts = counts[incutoff]

        return dmags, counts

    def rhobar(self,
               eam,
               alat: float,
               symbol: Union[str, list, None] = None):
        """
        Estimates the total embedding density (rhobar) for an EAM potential and
        an fcc crystal with a given lattice constant.

        Parameters
        ----------
        eam : EAMAlloy, EAMFS, ADP
            A parameter file builder for an EAM style that contains a cutoffr
            attribute and a rho_r() method.
        alat : float
            The fcc lattice constant to use for evaluating the rhobar embedding
            density.
        symbol : str, list or None
            The model symbol(s) associated with the rho(r) function to use. Not
            required if only one symbol has been set for the potential.
        """
        dmags, counts = self.dmags(alat, eam=eam)
        return np.sum(eam.rho_r(symbol=symbol, r=dmags) * counts)

    def min_alat(self,
                 eam,
                 symbol: Union[str, list, None] = None,
                 cutoffrho: Optional[float] = None):
        """
        Finds the minimum lattice parameter for an ideal fcc crystal that is
        compatible with the rho cutoff used.

        NOTE: alat values are also restricted to be >= cutoffr / 6 as the table
        used here only goes to 6*alat.

        Parameters
        ----------
        eam : EAMAlloy, EAMFS, ADP
            A parameter file builder for an EAM style that contains cutoffr and
            cutoffrho attributes and a rho_r() method.
        symbol : str, list or None
            The model symbol(s) associated with the rho(r) function to use. Not
            required if only one symbol has been set for the potential.
        cutoffrho : float or None
            Allows for the specification of a different cutoffrho value to use
            instead of the one currently set to the eam builder object.
        
        Returns
        -------
        alat : float
            The minimum fcc lattice parameter that the cutoffrho value supports.
            Will either be alat for rhobar(alat) = cutoffrho or alat = cutoffr / 6.
        """
        
        if cutoffrho is None:
            cutoffrho = eam.cutoffrho

        def min_fxn(alat):
            """minimization function for finding rhobar(alat) = cutoffrho"""
            return abs(self.rhobar(eam, alat, symbol=symbol) - cutoffrho)
        
        # First check min alat supported
        alat = eam.cutoffr / 6
        rhobar = self.rhobar(eam, alat, symbol=symbol)
        if rhobar < cutoffrho:
            return alat
        
        res = minimize(min_fxn, alat, bounds=((alat, None),))

        return res.x[0]