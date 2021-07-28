from ..tools import iaslist


def description():
    return "Query records based on a date element"

def mongo(qdict, path, val):
    if val is not None:
        val = [str(v) for v in iaslist(val)]
        qdict[path] = {'$in': val}

def pandas(df, name, val, parent=None):
    
    def apply_function(series, name, val, parent):
        if val is None:
            return True
        val = [str(v) for v in iaslist(val)]

        if parent is None:
            return str(series[name]) in val
        
        else:
            for p in series[parent]:
                if name in p and str(p[name]) in val:
                    return True
            return False

    return df.apply(apply_function, axis=1, args=(name, val, parent))