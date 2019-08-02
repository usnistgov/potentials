from pathlib import Path
import pandas as pd

from .. import rootdir
from .Citation import Citation

class CitationList():
    def __init__(self, localdir=None):
        if localdir is None:
            localdir = Path(rootdir, '..', 'data', 'bibtex')
        
        self.citationlist = []
        for bibfile in localdir.glob('*.bib'):
            self.citationlist.append(Citation(bibfile))
            
    def df(self):
        citationdf = []
        for citation in self.citationlist:
            citationdf.append(citation.content)
        return pd.DataFrame(citationdf)