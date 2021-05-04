from .aslist import aslist

def strmatch(series, name, val): # valmatch, idmatch, keymatch
    """
    A function for pandas.DataFrame.apply(fxn, axis=1) for identifying which
    series have elements of str type that match a given value.

    Parameters
    ----------
    series : pandas.Series
        The pandas series.  Automatically managed by apply with axis=1.
    name : str
        The element name of the series to check.
    val : None, str or list
        The value(s) to compare to the element.

    Returns
    -------
    bool
        True if val is None, or if series[name] == val or series[name] in val.
        False otherwise
    """
    
    if val is None:
        return True
    else:
        return series[name] in aslist(val)

def intmatch(series, name, val):
    """
    A function for pandas.DataFrame.apply(fxn, axis=1) for identifying which
    series have elements of int type that match a given value.

    Parameters
    ----------
    series : pandas.Series
        The pandas series.  Automatically managed by apply with axis=1.
    name : str
        The element name of the series to check.
    val : None, str or list
        The value(s) to compare to the element.

    Returns
    -------
    bool
        True if val is None, or if series[name] == val or series[name] in val.
        False otherwise
    """
    if val is None:
        return True
    else:
        val = aslist(val)
        for i in range(len(val)):
            val[i] = int(val[i])
        return series[name] in val

def listmatch(series, name, val): # elememtmatch
    """
    A function for pandas.DataFrame.apply(fxn, axis=1) for identifying which
    series have list elements that match a given value.  The selection is
    exclusive in that every given value must be in the series[name] list.

    Parameters
    ----------
    series : pandas.Series
        The pandas series.  Automatically managed by apply with axis=1.
    name : str
        The element name of the series to check.
    val : None, str or list
        The value(s) to compare to the element.

    Returns
    -------
    bool
        True if val is None, or if each value in val is in series[name].
        False otherwise.
    """
    if val is None:
        return True

    elif isinstance(series[name], (list, tuple)):
        for v in aslist(val):
            if v not in series[name]:
                return False
        return True
    else:
        return False

def authormatch(series, val):
    """
    A function for pandas.DataFrame.apply(fxn, axis=1) for identifying which
    Potential series have citations with all given authors.

    Parameters
    ----------
    series : pandas.Series
        The pandas series.  Automatically managed by apply with axis=1.
    name : str
        The element name of the series to check.
    val : None, str or list
        The value(s) to compare to the element.

    Returns
    -------
    bool
        True if val is None, or if each value in val is contained in the
        citation authors.  False otherwise.
    """
    
    if val is None:
        return True
    else:
        val = aslist(val)
        matches = [False for i in range(len(val))]
        for citation in series.citations:
            for i in range(len(val)):
                if val[i] in citation.author:
                    matches[i] = True
        if sum(matches) == len(val):
            return True
        else:
            return False

def yearmatch(series, val):
    """
    A function for pandas.DataFrame.apply(fxn, axis=1) for identifying which
    Potential series have citation publication years matching with any of the
    given values.  The selection is inclusive in that only one citation year
    has to be the same as one of the given values to be considered a match. 

    Parameters
    ----------
    series : pandas.Series
        The pandas series.  Automatically managed by apply with axis=1.
    name : str
        The element name of the series to check.
    val : None, str or list
        The value(s) to compare to the element.

    Returns
    -------
    bool
        True if val is None, or if any value in val matches one citation's
        year.  False otherwise.
    """
    if val is None:
        return True
    else:
        val = aslist(val)
        for i in range(len(val)):   
            val[i] = str(val[i])
        for citation in series.citations:
            if citation.year in aslist(val):
                return True
        return False
