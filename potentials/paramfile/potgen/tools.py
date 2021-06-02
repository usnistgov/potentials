import numpy as np

atomicsymbols = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg",
                 "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", 
                 "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se",
                 "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh",
                 "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba",
                 "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho",
                 "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt",
                 "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac",
                 "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
                 "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg",
                 "Cn", "Uut", "Fl", "Uup", "Lv", "Uus", "Uuo"]

def get_atomicnumber(symbol):
    return atomicsymbols.index(symbol) + 1
    
def get_atomicsymbol(number):
    return atomicsymbols[number-1]
    
def numderivative(x,y):
    deltax = x[1] - x[0]
    newx = x[:-1] + deltax / 2
    newy = np.diff(y) / deltax
    return newx, newy

def iaslist(term):
    """
    Iterate over items in term as if term was a list. Treats a str, unicode
    term as a single item.
    
    Parameters
    ----------
    term : any
        Term to iterate over.
    
    Yields
    ------
    any
        Items in the list representation of term.
    """
    if isinstance(term, str):
        yield term
    else:
        try:
            for t in term:
                yield t
        except:
            yield term
            
def aslist(term):
    """
    Create list representation of term. Treats a str, unicode term as a single
    item.
    
    Parameters
    ----------
    term : any
        Term to convert into a list, if needed.
        
    Returns
    -------
    list of any
        All items in term as a list
    """
    return [t for t in iaslist(term)]