from ..tools import aslist


def description():
    return "Query records where a string element has a value matching a val string"

def mongo(qdict, path, val):
    if val is not None:
        qdict[path] = {'$in': aslist(val)}

def pandas(df, name, val, parent=None):
    
    def apply_function(series, name, val, parent):
        if val is None:
            return True
        
        if parent is None:
            return series[name] in aslist(val)
        
        else:
            for p in series[parent]:
                if name in p and p[name] in aslist(val):
                    return True
            return False

    return df.apply(apply_function, axis=1, args=(name, val, parent))