from ..tools import iaslist


def description():
    return "Query records where a integer element has a value matching a val string"

def mongo(qdict, path, val):
    if val is not None:
        val = [int(v) for v in iaslist(val)]
        qdict[path] = {'$in': val}

def pandas(df, name, val, parent=None):
    
    def apply_function(series, name, val, parent):
        if val is None:
            return True
        val = [int(v) for v in iaslist(val)]

        if parent is None:
            return int(series[name]) in val
        
        else:
            for p in series[parent]:
                if name in p and int(p[name]) in val:
                    return True
            return False

    return df.apply(apply_function, axis=1, args=(name, val, parent))