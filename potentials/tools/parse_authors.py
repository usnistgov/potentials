# coding: utf-8
import string

def parse_authors(authors: str,
                  initials: bool = True) -> list:
    """
    Parse a bibtex authors field and return dicts containing separate givenname
    and surname fields.

    Parameters
    ----------
    authors : str
        The bibtex authors field.
    initials : bool, optional
        If True (default), the generated givenname fields will only include
        the givenname initials.  If False, the givenname fields will reflect
        what is in the bibtex authors string which may be full names or
        initials.
    
    Returns 
    -------
    list of dict
        The parsed bibtex authors field divided by author and into separate
        givenname and surname fields.
    """
    author_dicts = []
    
    # Split authors using 'and'
    authorlist = authors.split(' and ') 

    for author in authorlist:
        author_dict = {}
        
        # split given, surname using comma
        if ',' in author:
            index = author.rindex(',')
            author_dict['givenname'] = author[index + 1:].strip()
            author_dict['surname'] = author[:index].strip()

        # split given, surname using rightmost initial
        if '.' in author:  
            index = author.rindex(".")
            author_dict['givenname'] = author[:index + 1].strip()
            author_dict['surname'] = author[index + 1:].strip()
        
        # split given, surname using rightmost space
        else: 
            index = author.rindex(" ")
            author_dict['givenname'] = author[:index + 1].strip()
            author_dict['surname'] = author[index + 1:].strip()
        
        # Change given-name just into initials
        if initials:
            givenname = ''
            for letter in author_dict['givenname'].replace(' ', '').replace('.', ''):
                if letter in string.ascii_uppercase:
                    givenname += letter +'.'
                elif letter in ['-']:
                    givenname += letter
            author_dict['givenname'] = givenname
        
        author_dicts.append(author_dict)

    return author_dicts