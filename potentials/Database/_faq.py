
def get_faqs(self, local=None, remote=None, name=None, return_df=False,
             question=None, answer=None, verbose=False):
    """
    Retrieves all matching FAQs from the database.

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
    question : str or list
        Term(s) to search for in the question field.
    answer : str or list
        Term(s) to search for in the answer field.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned.
    """
    return self.get_records('FAQ', local=local, remote=remote, name=name, 
                            question=question, answer=answer, return_df=return_df,
                            verbose=verbose)

def get_faq(self, local=None, remote=None, name=None, question=None, answer=None,
            verbose=False):
    """
    Retrieves exactly one matching FAQ from the database.

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
    question : str or list
        Term(s) to search for in the question field.
    answer : str or list
        Term(s) to search for in the answer field.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    return self.get_record('FAQ', local=local, remote=remote, name=name, 
                           question=question, answer=answer, verbose=verbose)

def download_faqs(self, name=None, question=None, answer=None, 
                  overwrite=False, verbose=False):
    """
    Downloads FAQs from the remote to the local.

    Parameters
    ----------
    name : str or list
        The record name(s) to parse by.
    question : str or list
        Term(s) to search for in the question field.
    answer : str or list
        Term(s) to search for in the answer field.
    overwrite : bool, optional
        Flag indicating if any existing local records with names matching
        remote records are updated (True) or left unchanged (False).  Default
        value is False.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.download_records('FAQ', name=name, question=question, answer=answer,
                          overwrite=overwrite, verbose=verbose)

def upload_faq(self, faq=None, workspace=None, overwrite=False,
                    verbose=False):
    """
    Uploads a FAQ to the remote database.
    
    Parameters
    ----------
    faq : FAQ
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
    self.upload_record(record=faq, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def save_faq(self, faq, overwrite=False, verbose=False):
    """
    Saves a FAQ to the local database.
    
    Parameters
    ----------
    faq : FAQ
        The record to save.  
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the local
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.save_record(record=faq, overwrite=overwrite, verbose=verbose)

def delete_faq(self, faq, local=True, remote=False, verbose=False):
    """
    Deletes a FAQ from the local and/or remote locations.  

    Parameters
    ----------
    faq : FAQ
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
    self.delete_record(record=faq, local=local, remote=remote,
                       verbose=verbose)