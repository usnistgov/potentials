
def get_requests(self, local=None, remote=None, name=None, date=None, 
                 comment=None, return_df=False, verbose=False):
    """
    Retrieves all matching requests from the database.

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
    comment : str or list
        Term(s) to search for in the request's comment field.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned.
    """
    return self.get_records('Request', local=local, remote=remote, name=name, 
                            date=date, type=type, comment=comment,
                            return_df=return_df, verbose=verbose)

def get_request(self, local=None, remote=None, name=None, date=None,
                comment=None, verbose=False):
    """
    Retrieves exactly one matching request from the database.

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
    comment : str or list
        Term(s) to search for in the request's comment field.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    return self.get_record('Request', local=local, remote=remote, name=name, 
                           date=date, type=type, comment=comment,
                           verbose=verbose)

def download_requests(self, name=None, date=None,
                     comment=None, overwrite=False, verbose=False):
    """
    Downloads requests from the remote to the local.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    date : str or list
        The date associated with the record.
    comment : str or list
        Term(s) to search for in the request's comment field.
    overwrite : bool, optional
        Flag indicating if any existing local records with names matching
        remote records are updated (True) or left unchanged (False).  Default
        value is False.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.download_records('Request', name=name, date=date, type=type,
                          comment=comment, overwrite=overwrite, verbose=verbose)

def upload_request(self, request=None, workspace=None, overwrite=False,
                    verbose=False):
    """
    Uploads a request to the remote database.
    
    Parameters
    ----------
    request : Request
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
    self.upload_record(record=request, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def save_request(self, request, overwrite=False, verbose=False):
    """
    Saves a request to the local database.
    
    Parameters
    ----------
    request : Request
        The record to save.  
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the local
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.save_record(record=request, overwrite=overwrite, verbose=verbose)

def delete_request(self, request, local=True, remote=False, verbose=False):
    """
    Deletes a request from the local and/or remote locations.  

    Parameters
    ----------
    request : Request
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
    self.delete_record(record=request, local=local, remote=remote,
                       verbose=verbose)