
def get_potentials(self, local=None, remote=None, name=None, key=None, id=None,
                     notes=None, fictional=None, element=None,
                     othername=None, modelname=None, year=None, author=None,
                     abstract=None, return_df=False, verbose=False):
    """
    Retrieves all matching potentials from the database.

    Parameters
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    name : str or list
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list
        The unique UUID4 record key(s) to parse by. 
    id : str or list
        The unique record id(s) labeling the records to parse by.
    notes : str or list
        Term(s) to search for in the potential's notes field.
    fictional : bool
        Limits based on if the potential is labeled as fictional or not.
    element : str or list
        Element(s) in the model to parse by.
    othername : str or list
        Alternate system names (often compounds or molecules) to parse by.
    modelname : str or list
        Identifying model names to parse by.  These are used to differentiate
        between potentials that would otherwise have the same id based on year,
        primary author and elements. 
    year : int or list
        Publication year(s) to parse by.
    author : str or list
        Author name(s) to parse by.  This works best for last names only.
    abstract : str or list
        Term(s) to search for in the potential's citation's abstract field.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned.
    """
    return self.get_records('Potential', local=local, remote=remote, name=name, key=key, id=id,
                     notes=notes, fictional=fictional, element=element,
                     othername=othername, modelname=modelname, year=year, author=author,
                     abstract=abstract, return_df=return_df, verbose=verbose)

def get_potential(self, local=None, remote=None, name=None, key=None, id=None,
                     notes=None, fictional=None, element=None,
                     othername=None, modelname=None, year=None, author=None,
                     abstract=None, prompt=True, verbose=False):
    """
    Retrieves exactly one matching potential from the database.

    Parameters
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    name : str or list
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list
        The unique UUID4 record key(s) to parse by. 
    id : str or list
        The unique record id(s) labeling the records to parse by.
    notes : str or list
        Term(s) to search for in the potential's notes field.
    fictional : bool
        Limits based on if the potential is labeled as fictional or not.
    element : str or list
        Element(s) in the model to parse by.
    othername : str or list
        Alternate system names (often compounds or molecules) to parse by.
    modelname : str or list
        Identifying model names to parse by.  These are used to differentiate
        between potentials that would otherwise have the same id based on year,
        primary author and elements. 
    year : int or list
        Publication year(s) to parse by.
    author : str or list
        Author name(s) to parse by.  This works best for last names only.
    abstract : str or list
        Term(s) to search for in the potential's citation's abstract field.
    prompt : bool
        If prompt=True (default) then a screen input will ask for a selection
        if multiple matching potentials are found.  If prompt=False, then an
        error will be thrown if multiple matches are found.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    return self.get_record('Potential', local=local, remote=remote, name=name,
                           key=key, id=id, notes=notes, fictional=fictional,
                           element=element, othername=othername,
                           modelname=modelname, year=year, author=author,
                           abstract=abstract, prompt=prompt, verbose=verbose)

def download_potentials(self, name=None, key=None, id=None,
                        notes=None, fictional=None, element=None,
                        othername=None, modelname=None, year=None, author=None,
                        abstract=None, overwrite=False, verbose=False):
    """
    Downloads potentials from the remote to the local.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.  For potential records, the names
        should correspond to the id with a prefix of "potentials." added to it.
    key : str or list
        The unique UUID4 record key(s) to parse by. 
    id : str or list
        The unique record id(s) labeling the records to parse by.
    notes : str or list
        Term(s) to search for in the potential's notes field.
    fictional : bool
        Limits based on if the potential is labeled as fictional or not.
    element : str or list
        Element(s) in the model to parse by.
    othername : str or list
        Alternate system names (often compounds or molecules) to parse by.
    modelname : str or list
        Identifying model names to parse by.  These are used to differentiate
        between potentials that would otherwise have the same id based on year,
        primary author and elements. 
    year : int or list
        Publication year(s) to parse by.
    author : str or list
        Author name(s) to parse by.  This works best for last names only.
    abstract : str or list
        Term(s) to search for in the potential's citation's abstract field.
    overwrite : bool, optional
        Flag indicating if any existing local records with names matching
        remote records are updated (True) or left unchanged (False).  Default
        value is False.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.

    """
    self.download_records('Potential', name=name, key=key, id=id,
                     notes=notes, fictional=fictional, element=element,
                     othername=othername, modelname=modelname, year=year, author=author,
                     abstract=abstract, overwrite=overwrite, verbose=verbose)

def upload_potential(self, potential=None, workspace=None, overwrite=False,
                    verbose=False):
    """
    Uploads a potential to the remote database.
    
    Parameters
    ----------
    potential : Potential
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
    self.upload_record(record=potential, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def save_potential(self, potential, overwrite=False, verbose=False):
    """
    Saves a potential to the local database.
    
    Parameters
    ----------
    potential : Potential
        The record to save.  
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the local
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.save_record(record=potential, overwrite=overwrite, verbose=verbose)

def delete_potential(self, potential, local=True, remote=False, verbose=False):
    """
    Deletes a potential from the local and/or remote locations.  

    Parameters
    ----------
    potential : Potential
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
    self.delete_record(record=potential, local=local, remote=remote,
                       verbose=verbose)