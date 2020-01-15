# coding: utf-8

from cdcs import CDCS

class Database():
    """
    Class for interacting with potential records hosted from potentials.nist.gov
    """
    # Class imports
    from ._citation import (citations, citations_df, load_citations,
                            get_citation, _no_load_citations, download_citations,
                            save_citation)
    from ._potential import (potentials, potentials_df, load_potentials,
                             get_potential, get_potentials, _no_load_potentials)
    from ._potential_lammps import (potential_LAMMPS, potential_LAMMPS_df,
                                    load_potential_LAMMPS, _no_load_potential_LAMMPS,
                                    get_potential_LAMMPS, download_LAMMPS_files)
    from ._widgets import (widget_search_potentials, widget_lammps_potential)

    def __init__(self, host=None, username=None, password=None, certification=None,
                 localpath=None, verbose=True, load_citations=False,
                 load_potentials=False, load_potential_LAMMPS=False):
        """
        Class initializer

        Parameters
        ----------
        host : str, optional
            Remote host site to access.  Default value is
            'https://potentials.nist.gov/'
        username : str, optional 
            User name to use to access the host site.  Default value of '' will
            access the site as an anonymous visitor.
        password : str, optional
            Password associated with the given username.  Not needed for
            anonymous access.
        certification : str, optional
            File path to certification file if needed for host.
        localpath : str, optional
            Path to directory where a local copy of the database is to be used.
            Optional.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
        load_citations : bool, optional
            If True, the citations will be loaded during initialization.
            Default value is False.
        load_potentials : bool, optional
            If True, the potentials will be loaded during initialization.
            Default value is False.
        load_potential_LAMMPS : bool, optional
            If True, the LAMMPS potentials will be loaded during initialization.
            Default value is False.
        """
        # Set default database parameters
        if host is None:
            host = 'https://potentials.nist.gov/'
        if username is None:
            username = ''
        
        # Create the underlying CDCS client
        self.__cdcs = CDCS(host=host, username=username, password=password,
                           certification=certification)
        self.__localpath = localpath
        
        # Load records
        if load_citations:
            self.load_citations(verbose=verbose)
        else:
            self._no_load_citations()
        if load_potentials:
            self.load_potentials(verbose=verbose)
        else:
            self._no_load_potentials()
        if load_potential_LAMMPS:
            self.load_potential_LAMMPS(verbose=verbose)
        else:
            self._no_load_potential_LAMMPS()
    
    @property
    def cdcs(self):
        """cdcs.CDCS: REST client for database access"""
        return self.__cdcs
    
    @property
    def localpath(self):
        """str or None: path to the local copy of the database"""
        return self.__localpath