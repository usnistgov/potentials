from .Record import Record
from .RecordManager import RecordManager
recordmanager = RecordManager('Record')
__all__ = ['Record', 'recordmanager', 'load_record']

# Define load_record 
def load_record(style, model=None, name=None, **kwargs):
    """
    Loads a Record subclass associated with a given record style.

    Parameters
    ----------
    style : str
        The record style
    name : str
        The name to give to the specific record
    content : 
        The record's data model content
    
    Returns
    -------
    subclass of Record 
        A Record object for the style
    """
    return recordmanager.init(style, model=model, name=name, **kwargs)
