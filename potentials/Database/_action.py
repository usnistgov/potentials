
def get_actions(self, local=None, remote=None, name=None, date=None, type=None,
                potential_id=None, potential_key=None, element=None,
                comment=None, return_df=False, verbose=False):
    """
    Retrieves all matching actions from the database.

    Parameters
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    name : str or list
        The record name(s) to parse by.
    date : str or list
        The date associated with the record.
    type : str or list
        The type of action: 'new posting', 'updated posting', 'retraction',
        or 'site change'.
    potential_id : str or list
        Limits results to entries related to the given potential id.
    potential_key : str or list
        Limits results to entries related to the given potential key.
    element : str or list
        Limits results to entries related to potentials with the given
        element(s).
    comment : str or list
        Term(s) to search for in the action's comment field.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned.
    """
    return self.get_records('Action', local=local, remote=remote, name=name, 
                            date=date, type=type, potential_id=potential_id,
                            potential_key=potential_key, element=element,
                            comment=comment, return_df=return_df,
                            verbose=verbose)

def get_action(self, local=None, remote=None, name=None, date=None, type=None,
               potential_id=None, potential_key=None, element=None,
               comment=None, verbose=False):
    """
    Retrieves exactly one matching action from the database.

    Parameters
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    name : str or list
        The record name(s) to parse by.
    date : str or list
        The date associated with the record.
    type : str or list
        The type of action: 'new posting', 'updated posting', 'retraction',
        or 'site change'.
    potential_id : str or list
        Limits results to entries related to the given potential id.
    potential_key : str or list
        Limits results to entries related to the given potential key.
    element : str or list
        Limits results to entries related to potentials with the given
        element(s).
    comment : str or list
        Term(s) to search for in the action's comment field.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    return self.get_record('Action', local=local, remote=remote, name=name, 
                           date=date, type=type, potential_id=potential_id,
                           potential_key=potential_key, element=element,
                           comment=comment, verbose=verbose)

def download_actions(self, name=None, date=None, type=None, potential_id=None,
                     potential_key=None, element=None, comment=None,
                     overwrite=False, verbose=False):
    """
    Downloads actions from the remote to the local.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    date : str or list
        The date associated with the record.
    type : str or list
        The type of action: 'new posting', 'updated posting', 'retraction',
        or 'site change'.
    potential_id : str or list
        Limits results to entries related to the given potential id.
    potential_key : str or list
        Limits results to entries related to the given potential key.
    element : str or list
        Limits results to entries related to potentials with the given
        element(s).
    comment : str or list
        Term(s) to search for in the action's comment field.
    overwrite : bool, optional
        Flag indicating if any existing local records with names matching
        remote records are updated (True) or left unchanged (False).  Default
        value is False.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.download_records('Action', name=name, date=date, type=type,
                          potential_id=potential_id, potential_key=potential_key,
                          element=element, comment=comment, overwrite=overwrite,
                          verbose=verbose)

def upload_action(self, action=None, workspace=None, overwrite=False,
                    verbose=False):
    """
    Uploads an action to the remote database.
    
    Parameters
    ----------
    action : Action
        The record to upload.
    workspace : str, optional
        The workspace to assign the record to. If not given, no workspace will
        be assigned (only accessible to user who submitted it).
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the remote
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.upload_record(record=action, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def save_action(self, action, overwrite=False, verbose=False):
    """
    Saves an action to the local database.
    
    Parameters
    ----------
    action : Action
        The record to save.  
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the local
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.save_record(record=action, overwrite=overwrite, verbose=verbose)

def delete_action(self, action, local=True, remote=False, verbose=False):
    """
    Deletes an action from the local and/or remote locations.  

    Parameters
    ----------
    action : Action
        The record to delete.  If not given, then style and name
        are required.
    local : bool, optional
        Indicates if the record will be deleted from the local location.
        Default value is True.
    remote : bool, optional
        Indicates if the record will be deleted from the remote location.
        Default value is False.  If True, requires an account for the remote
        location with write permissions.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.delete_record(record=action, local=local, remote=remote,
                       verbose=verbose)