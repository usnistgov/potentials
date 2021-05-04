from ..tools import aslist

def description():
    return "Query records where val string(s) are in a string element"

def mongo(qdict, path, val):
    if val is not None:
        val = aslist(val)
        qdict['$and'] = []
        for v in val:
            qdict['$and'].append({path:{'$regex': v}})

def pandas(df, name, val, parent=None):

    def apply_function(series, name, val, parent):
        if val is None:
            return True
        
        if parent is None:
            for v in aslist(val):
                if v not in series[name]:
                    return False
            return True
        
        else:
            for v in aslist(val):
                match = False
                for p in series[parent]:
                    if name in p and v in p[name]:
                        match = True
                        break
                if match is False:
                    return False
            return True

    
    return df.apply(apply_function, axis=1, args=(name, val, parent))
