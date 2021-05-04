# coding: utf-8
from pathlib import Path

from .. import settings
from ..tools import aslist

from datamodelbase import load_database

class Database():
    """
    Class for interacting with potential records hosted from potentials.nist.gov
    """
    # Class imports
    from ._record import (get_records, get_record, download_records,
                          remote_query, upload_record, delete_record, save_record)

    from ._citation import (get_citations, get_citation, fetch_citation,
                            download_citations, upload_citation, save_citation, delete_citation)

    from ._potential import (get_potentials, get_potential, download_potentials,
                             upload_potential, save_potential, delete_potential)

    from ._kim_potential import (get_kim_lammps_potentials, kim_models, init_kim_models,
                                 find_kim_models, set_kim_models, save_kim_models_file,
                                 delete_kim_models_file, load_kim_models_file)

    from ._lammps_potential import (get_lammps_potentials, get_lammps_potential,
                                    download_lammps_potentials, get_lammps_potential_files,
                                    upload_lammps_potential, save_lammps_potential,
                                    delete_lammps_potential)

    from ._widgets import (widget_search_potentials, widget_lammps_potential)

    def __init__(self, host=None, username=None, password=None, cert=None, verify=None,
                 localpath=None, format='json', indent=4,
                 verbose=False, local=None, remote=None, 
                 kim_models=None, kim_api_directory=None, kim_models_file=None):
        """
        Class initializer

        Parameters
        ----------
        host : str, optional
            Remote CDCS site to access.  Default value is 'https://potentials.nist.gov/'.
        username : str, optional 
            User name to use to access the remote site.  Default value of '' will
            access the site as an anonymous visitor.
        password : str, optional
            Password associated with the given username.  Not needed for
            anonymous access.
        cert : str or tuple, optional
            File path(s) to certification file(s) if needed for host.
        verify: bool or str, optional
            Verification options.  If not given, will default to True if cert
            is given and False if cert is not given.
        localpath : str, optional
            Path to the local directory to use for the local database location.
            If not given, will use the library_directory setting.
        format : str, optional
            The file format to use for saving records to the local location.
            Allowed values are 'json' or 'xml'.  If not given, will use the
            library_format setting.
        indent : str, optional
            The indentation style to use for saving records to the local
            database location.  If not given, will use the library_indent setting.
        local : bool, optional
            Indicates if the load operations will check localpath for records.
            Default value is controlled by settings.  If False, then localpath,
            format and indent values are ignored.
        remote : bool, optional
            Indicates if the load operations will download records from the
            remote database.  Default value is controlled by settings.  If False,
            then host, username, password, cert and verify values are ignored.
        kim_models : str or list, optional
            Allows for the list of installed_kim_models to be explicitly given.
            Cannot be given with the other parameters.
        kim_api_directory : path-like object, optional
            The directory containing the kim api to use to build the list.
        kim_models_file : path-like object, optional
            The path to a whitespace-delimited file listing full kim ids.
        pot_dir_style : str, optional
            Specifies how the pot_dir values will be set for the loaded lammps
            potentials.  Allowed values are 'working', 'id', and 'local'.
            'working' will set all pot_dir = '', meaning parameter files
            are expected in the working directory when the potential is accessed.
            'id' sets the pot_dir values to match the potential's id.
            'local' sets the pot_dir values to the corresponding local database
            paths where the files are expected to be found.  Default value is
            controlled by settings.
        """


        # Handle local/remote settings
        if local is None:
            local = settings.local
        if remote is None:
            remote = settings.remote
        assert isinstance(local, bool)
        assert isinstance(remote, bool)
        self.__local = local
        self.__remote = remote

        # set database interactions
        if remote:
            self.set_remote_database(host=host,
                                     username=username, password=password,
                                     cert=cert, verify=verify)
        else:
            self.__remote_database = None
        
        if local:
            self.set_local_database(localpath=localpath, format=format, indent=indent)
        else:
            self.__local_database = None
        
        # Initialize list of kim models to use
        self.init_kim_models(kim_models=kim_models, kim_models_file=kim_models_file,
                             kim_api_directory=kim_api_directory)

    @property
    def remote_database(self):
        """datamodelbase.CDCSDatabase : Interfaces with the remote CDCS database"""
        return self.__remote_database

    @property
    def local_database(self):
        """datamodelbase.LocalDatabase : Interfaces with the local database"""
        return self.__local_database

    @property
    def local(self):
        """bool : Indicates if load operations will check localpath"""
        return self.__local

    @property
    def remote(self):
        """bool : Indicates if load operations will check remote database"""
        return self.__remote

    def set_remote_database(self, host=None, username=None, password=None,
                            cert=None, verify=None):
        """
        Sets or changes the remote database settings.

        Parameters
        ----------
        host : str, optional
            Remote CDCS site to access.  Default value is 'https://potentials.nist.gov/'.
        username : str, optional 
            User name to use to access the remote site.  Default value of '' will
            access the site as an anonymous visitor.
        password : str, optional
            Password associated with the given username.  Not needed for
            anonymous access.
        cert : str or tuple, optional
            File path(s) to certification file(s) if needed for host.
        verify: bool or str, optional
            Verification options.  If not given, will default to True if cert
            is given and False if cert is not given.
        """
        # Set default database parameters
        if host is None:
            host = 'https://potentials.nist.gov/'
        if username is None:
            username = ''
        
        if verify is None:
            if cert is None:
                verify = False
            else:
                verify = True

        self.__remote_database = load_database(style='cdcs', host=host,
                                               username=username, password=password,
                                               cert=cert, verify=verify)

    def set_local_database(self, localpath=None, format=None, indent=None):
        """
        Sets or changes the local database settings.

        Parameters
        ----------
        localpath : str, optional
            Path to the local directory to use for the local database location.
            If not given, will use the library_directory setting.
        format : str, optional
            The file format to use for saving records to the local location.
            Allowed values are 'json' or 'xml'.  If not given, will use the
            library_format setting.
        indent : str, optional
            The indentation style to use for saving records to the local
            database location.  If not given, will use the library_indent setting.
        """
        # Define class attributes
        if localpath is None:
            localpath = settings.library_directory
        else:
            localpath = Path(localpath)

        self.__local_database = load_database(style='local', host=localpath,
                                              format=format, indent=indent)

    def download_all(self, status=None, downloadfiles=True, overwrite=False,
                     verbose=False):
        """
        Downloads all potential-related records from the remote location to the
        local location.

        Parameters
        ----------
        status : str, list or None, optional
            Only potential_LAMMPS records with the given status(es) will be
            downloaded.  Allowed values are 'active' , 'superseded', and 'retracted'.
            If None (default) is given, then all potentials will be downloaded.
        downloadfiles : bool, optional
            If True, the parameter files associated with the potential_LAMMPS
            record will also be downloaded.
        overwrite : bool, optional
            Flag indicating if any existing local records with names matching
            remote records are updated (True) or left unchanged (False).  Default
            value is False.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.

        """
        self.download_citations(overwrite=overwrite, verbose=verbose)

        self.download_potentials(overwrite=overwrite, verbose=verbose)

        self.download_lammps_potentials(status=status, downloadfiles=downloadfiles,
                                        overwrite=overwrite, verbose=verbose)