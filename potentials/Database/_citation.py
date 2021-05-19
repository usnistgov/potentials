# https://github.com/sckott/habanero
from habanero import cn

from .. import load_record

def get_citations(self, local=None, remote=None, name=None, year=None, volume=None,
                  title=None, journal=None, doi=None, author=None,
                  abstract=None, return_df=False, verbose=False):
    """
    Retrieves all matching citations from the database.

    Parameters 
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    name : str or list, optional
        The name(s) of records to limit the search by.
    year : int or list, optional
        Publication year(s) to limit the search by.
    volume : int or list, optional
        Journal volume(s) to limit the search by.
    title : str or list, optional
        Word(s) to search for in the article titles.
    journal : str or list, optional
        Journal name(s) to limit the search by.
    doi : str or list, optional
        Article DOI(s) to limit the search by. 
    author : str or list, optional
        Author name(s) to search for.  Works best for last names only.
    abstract : str or list, optional
        Word(s) to search for in the article abstracts.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    return_df : bool, optional
        If True, then the corresponding pandas.Dataframe of metadata
        will also be returned.
    """
    return self.get_records('Citation', local=local, remote=remote, name=name, year=year, volume=volume,
                            title=title, journal=journal, doi=doi, author=author,
                            abstract=abstract, return_df=return_df, verbose=verbose)

def get_citation(self, local=None, remote=None, name=None, year=None, volume=None,
                 title=None, journal=None, doi=None, author=None,
                 abstract=None, verbose=False):
    """
    Retrieves exactly one matching citation from the database.

    Parameters 
    ----------
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    name : str or list, optional
        The name(s) of records to limit the search by.
    year : int or list, optional
        Publication year(s) to limit the search by.
    volume : int or list, optional
        Journal volume(s) to limit the search by.
    title : str or list, optional
        Word(s) to search for in the article titles.
    journal : str or list, optional
        Journal name(s) to limit the search by.
    doi : str or list, optional
        Article DOI(s) to limit the search by. 
    author : str or list, optional
        Author name(s) to search for.  Works best for last names only.
    abstract : str or list, optional
        Word(s) to search for in the article abstracts.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.

    Raises
    ------
    ValueError
        If no or multiple matching records are found.
    """
    return self.get_record('Citation', local=local, remote=remote, name=name, year=year, volume=volume,
                            title=title, journal=journal, doi=doi, author=author,
                            abstract=abstract, verbose=verbose)

def fetch_citation(self, doi, local=None, remote=None, verbose=False):
    """
    Retrieves a single citation based on its DOI.  First, the database is checked
    for matches with the DOI, then with the record name.  If no matches are found
    in the database, then the corresponding citation is downloaded from CrossRef.

    Parameters
    ----------
    doi : str
        The citation's DOI.  If the citation has no DOI, then the citation's
        record name should be given instead.
    local : bool, optional
        Indicates if the local location is to be searched.  Default value
        matches the value set when the database was initialized.
    remote : bool, optional
        Indicates if the remote location is to be searched.  Default value
        matches the value set when the database was initialized.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    if local is not False or remote is not False:
        # Try fetching based on doi
        try:
            return self.get_citation(doi=doi, local=local, remote=remote, verbose=verbose)
        except:
            pass

        # Try fetching based on name
        try:
            return self.get_citation(name=doi, local=local, remote=remote, verbose=True)
        except:
            pass
    
    # Fetch from CrossRef if database search failed/skipped
    bibtex = cn.content_negotiation(ids=doi, format="bibtex")
    if verbose:
        print(f'Citation retrieved from CrossRef')

    return load_record('Citation', bibtex)

def download_citations(self, name=None, year=None, volume=None,
                  title=None, journal=None, doi=None, author=None,
                  abstract=None, overwrite=False, verbose=False):
    """
    Downloads citations from the remote to the local.

    Parameters 
    ----------
    name : str or list, optional
        The name(s) of records to limit the search by.
    year : int or list, optional
        Publication year(s) to limit the search by.
    volume : int or list, optional
        Journal volume(s) to limit the search by.
    title : str or list, optional
        Word(s) to search for in the article titles.
    journal : str or list, optional
        Journal name(s) to limit the search by.
    doi : str or list, optional
        Article DOI(s) to limit the search by. 
    author : str or list, optional
        Author name(s) to search for.  Works best for last names only.
    abstract : str or list, optional
        Word(s) to search for in the article abstracts.
    overwrite : bool, optional
        Flag indicating if any existing local records with names matching
        remote records are updated (True) or left unchanged (False).  Default
        value is False.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """

    self.download_records('Citation', name=name, year=year, volume=volume,
                          title=title, journal=journal, doi=doi, author=author,
                          abstract=abstract, overwrite=overwrite, verbose=verbose)

def save_citation(self, citation, overwrite=False, verbose=False):
    """
    Saves a citation to the local database.
    
    Parameters
    ----------
    citation : Citation
        The record to save.  
    overwrite : bool, optional
        Indicates what to do when a matching record is found in the local
        location.  If False (default), then the record is not updated.  If
        True, then the record is updated.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    self.save_record(record=citation, overwrite=overwrite, verbose=verbose)

def upload_citation(self, citation, workspace=None, overwrite=False,
                    verbose=False):
    """
    Uploads a citation to the remote database.
    
    Parameters
    ----------
    citation : Citation
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
    self.upload_record(record=citation, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def delete_citation(self, citation, local=True, remote=False, verbose=False):
    """
    Deletes a citation from the local and/or remote locations.  

    Parameters
    ----------
    citation : Citation
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
    self.delete_record(record=citation, local=local, remote=remote,
                       verbose=verbose)