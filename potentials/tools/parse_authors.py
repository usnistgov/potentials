import string

def parse_authors(authors, initials=True):
    """
    Parse bibtex authors field.
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