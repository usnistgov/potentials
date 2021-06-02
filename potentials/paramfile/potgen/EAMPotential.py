from __future__ import print_function, division, absolute_import
from .gen_eam_setfl import gen_eam_setfl

class EAMPotential(object):
    """Generic class for representing an EAM-style potential"""
    
    def __init__(self):
        pass
        
    def pair(self, r, symbol=None):
        """The pair interaction function: phi(r)"""
        return 0*r
        
    def rpair(self, r, symbol=None):
        """Pair inreraction multiplied by r: r*phi(r)"""
        return 0*r
        
    def embedding(self, rho, symbol=None):
        """The embedding energy function: F(rhobar)"""
        return 0*rho
        
    def electrondensity(self, r, symbol=None):
        """The electron density function: rho(r)"""
        return 0*r
        
    def setfl(self, numr=1000, cutoffr=6, numrho=1000, cutoffrho=20, 
              a_symbol=None, a_number=None, a_mass=None, a_lat_const=None, a_lat_type=None,
              header=None, xf='%25.16e', ncolumns=5, outfile=None):
        
        gen_eam_setfl(F=self.embedding, rho=self.electrondensity, phi=self.rpair,
            numr=numr, cutoffr=cutoffr, numrho=numrho, cutoffrho=cutoffrho, 
            a_symbol=a_symbol, a_number=a_number, a_mass=a_mass, 
            a_lat_const=a_lat_const, a_lat_type=a_lat_type,
            header=header, xf=xf, ncolumns=ncolumns, outfile=outfile)
        
              
        