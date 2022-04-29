# coding: utf-8
# Standard libraries
from pathlib import Path
from typing import Optional, Union

import yabadaba

# Local imports
from .. import settings
from .load_database import load_database

class Database():
    """
    Class for interacting with potential records hosted from potentials.nist.gov
    """
    # Class imports
    from ._record import (get_records, get_record, retrieve_record, download_records,
                          remote_query, upload_record, delete_record, save_record)

    from ._citation import (get_citations, get_citation, retrieve_citation, fetch_citation,
                            download_citations, upload_citation, save_citation, delete_citation)

    from ._potential import (get_potentials, get_potential, retrieve_potential, download_potentials,
                             upload_potential, save_potential, delete_potential)

    from ._action import (get_actions, get_action, retrieve_action, download_actions,
                          upload_action, save_action, delete_action)

    from ._request import (get_requests, get_request, retrieve_request, download_requests,
                          upload_request, save_request, delete_request)

    from ._faq import (get_faqs, get_faq, retrieve_faq, download_faqs,
                       upload_faq, save_faq, delete_faq)

    from ._related_models import (load_related_models, related_models, get_related_models,
                                 save_related_models, add_related_models, sort_related_models)

    from ._kim_potential import (get_kim_lammps_potentials, kim_models, init_kim_models,
                                 find_kim_models, set_kim_models, save_kim_models_file,
                                 delete_kim_models_file, load_kim_models_file)

    from ._lammps_potential import (get_lammps_potentials, get_lammps_potential,
                                    download_lammps_potentials, get_lammps_potential_files,
                                    retrieve_lammps_potential, upload_lammps_potential,
                                    save_lammps_potential, delete_lammps_potential,
                                    bad_lammps_potentials)

    from ._widgets import (widget_search_potentials, widget_lammps_potential)

    def __init__(self,
                 local: Optional[bool] = None,
                 remote: Optional[bool] = None,
                 localpath: Optional[str] = None,
                 local_name: Optional[str] = None,
                 local_database: Optional[yabadaba.database.Database] = None,
                 local_style: Optional[str] = None,
                 local_host: Optional[str] = None,
                 local_terms: Optional[dict] = None,
                 remote_name: Optional[str] = None,
                 remote_database: Optional[yabadaba.database.Database] = None,
                 remote_style: Optional[str] = None,
                 remote_host: Optional[str] = None,
                 remote_terms: Optional[dict] = None, 
                 kim_models: Union[str, list, None] = None,
                 kim_api_directory: Optional[Path] = None,
                 kim_models_file: Optional[Path] = None):
        """
        Class initializer

        Parameters
        ----------
        local : bool, optional
            Indicates if the load operations will check for local records.
            Default value is controlled by settings.  If False, then the local
            interactions will not be set.
        remote : bool, optional
            Indicates if the load operations will check for remote records.
            Default value is controlled by settings.  If False, then the remote
            interactions will not be set.

        localpath : str, optional
            The path to a directory where a local-style directory is to be
            found. This is an alias for local_host, with a local_style of
            "local" and is only retained for backwards compatibility.
        local_database : yabadaba.Database
            A pre-existing Database object to use for the local.
        local_name : str, optional
            The name assigned to a pre-defined database to use for the local
            interactions.  Cannot be given with local_style, local_host or
            local_terms.
        local_style : str, optional
            The database style to use for the local interactions.
        local_host : str, optional
            The URL/file path where the local database is hosted.
        local_terms : dict, optional
            Any other keyword parameters defining necessary access/settings
            information for using the local database.  Allowed keywords are
            database style-specific.
        
        remote_name : str, optional
            The name assigned to a pre-defined database to use for the remote
            interactions.  Cannot be given with remote_style, remote_host or
            remote_terms.
        remote_database : yabadaba.Database
            A pre-existing Database object to use for the remote.
        remote_style : str, optional
            The database style to use for the remote interactions.
        remote_host : str, optional
            The URL/file path where the remote database is hosted.
        remote_terms : dict, optional
            Any other keyword parameters defining necessary access/settings
            information for using the remote database.  Allowed keywords are
            database style-specific.

        kim_models : str or list, optional
            Allows for the list of installed_kim_models to be explicitly given.
            Cannot be given with the other kim parameters.
        kim_api_directory : path-like object, optional
            The directory containing the kim api to use to build the list.
            Cannot be given with the other kim parameters.
        kim_models_file : path-like object, optional
            The path to a whitespace-delimited file listing full kim ids.
            Cannot be given with the other kim parameters.
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
            if remote_terms is None:
                remote_terms = {}
            self.set_remote_database(name=remote_name, database=remote_database,
                                     style=remote_style, host=remote_host,
                                     **remote_terms)
        else:
            self.__remote_database = None
        
        if local:
            if local_terms is None:
                local_terms = {}
            self.set_local_database(name=local_name, database=local_database,
                                    style=local_style, host=local_host,
                                    localpath=localpath, **local_terms)
        else:
            self.__local_database = None
        
        # Initialize list of kim models to use
        self.init_kim_models(kim_models=kim_models, kim_models_file=kim_models_file,
                             kim_api_directory=kim_api_directory)

    @property
    def remote_database(self) -> yabadaba.database.Database:
        """yabadaba.database.Database : Interfaces with the remote database"""
        return self.__remote_database

    @property
    def local_database(self) -> yabadaba.database.Database:
        """yabadaba.database.Database : Interfaces with the local database"""
        return self.__local_database

    @property
    def local(self) -> bool:
        """bool : Indicates if load operations will check localpath"""
        return self.__local

    @property
    def remote(self) -> bool:
        """bool : Indicates if load operations will check remote database"""
        return self.__remote

    def set_remote_database(self,
                            name: Optional[str] = None,
                            database: Optional[yabadaba.database.Database] = None,
                            style: Optional[str] = None,
                            host: Optional[str] = None,
                            **kwargs):
        """
        Sets the remote database to interact with.  If no parameters are given,
        will load settings for "potentials_remote" database if they have been
        saved, or will otherwise access potentials.nist.gov as an anonymous user.

        Parameters
        ----------
        name : str, optional
            The name assigned to a pre-defined database.  If given, can be the only
            parameter.
        database : yabadaba.database.Database, optional
            A pre-existing Database object to use for the remote.
        style : str, optional
            The database style to use.
        host : str, optional
            The URL/file path where the database is hosted.
        kwargs : dict, optional
            Any other keyword parameters defining necessary access information.
            Allowed keywords are database style-specific.
        """
        if database is not None:
            assert name is None and style is None and host is None
            self.__remote_database = database

        elif name is None and style is None and host is None:
            if 'potentials_remote' in settings.list_databases:
                self.__remote_database = load_database(name='potentials_remote')
            else:
                kwargs['username'] = kwargs.get('username', '')
                self.__remote_database = load_database(style='cdcs',
                                                       host='https://potentials.nist.gov/',
                                                       **kwargs)
        else:
            self.__remote_database = load_database(name=name, style=style, host=host, **kwargs)

    def set_local_database(self,
                           localpath: Optional[str] = None,
                           name: Optional[str] = None,
                           database: Optional[yabadaba.database.Database] = None,
                           style: Optional[str] = None,
                           host: Optional[str] = None,
                           **kwargs):
        """
        Sets the local database to interact with.  If no parameters are given,
        will load settings for "potentials_local" database if they have been
        saved, or will otherwise use a local directory inside the default
        settings directory.

        Parameters
        ----------
        name : str, optional
            The name assigned to a pre-defined database.  If given, can be the only
            parameter.
        database : yabadaba.Database, optional
            A pre-existing Database object to use for the local.
        style : str, optional
            The database style to use.
        host : str, optional
            The URL/file path where the database is hosted.
        localpath : str, optional
            The path to a directory where a local-style directory is to be found.
            This is an alias for host, with a style of "local" and is only retained
            for backwards compatibility.
        kwargs : dict, optional
            Any other keyword parameters defining necessary access information.
            Allowed keywords are database style-specific.
        """

        if database is not None:
            assert name is None and style is None and host is None and localpath is None
            self.__local_database = database
            return

        # Handle old localpath
        if localpath is not None:
            assert host is None, 'host and localpath cannot both be given'
            assert style is None or style == 'local', 'localpath is associated with style "local"'
            host = localpath
            style = 'local'

        if name is None and style is None and host is None:
            
            if 'potentials_local' in settings.list_databases:
                self.__local_database = load_database(name='potentials_local')
            else:
                self.__local_database = load_database(style='local',
                                                      host=Path(settings.directory, 'library'), 
                                                      **kwargs)
        else:
            self.__local_database = load_database(name=name, style=style, host=host, **kwargs)

    def download_all(self,
                     status: Union[str, list, None] = None,
                     downloadfiles: bool = True,
                     overwrite: bool = False,
                     verbose: bool = False):
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