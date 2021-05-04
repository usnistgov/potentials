from .aslist import aslist

def strquery(qdict, path, val):
    # Add query
    if val is not None:
        qdict[path] = {'$in': aslist(val)}