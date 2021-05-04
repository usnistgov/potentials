from ..tools import aslist


def description():
    return "Query records where a list element contains one or more matching values"

def mongo(qdict, path, val):
    if val is not None:
        qdict[path] = {'$in': aslist(val)}

def pandas(df, name, val, parent=None):
    
    def apply_function(series, name, val, parent):
        if val is None:
            return True
        
        for v in aslist(val):
            if v not in series[name]:
                return False
        return True

    return df.apply(apply_function, axis=1, args=(name, val, parent))