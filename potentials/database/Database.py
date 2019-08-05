from pathlib import Path
import pandas as pd

from .. import rootdir
from .Citation import Citation
from .Potential import Potential
from .Implementation import Implementation

class Database():
    def __init__(self, localdir=None):
        self.load_local_citations(localdir=localdir)
        self.load_local_potentials(localdir=localdir)
        self.load_local_implementations(localdir=localdir)

    @property
    def citations(self):
        return self.__citations
    
    @property
    def citations_df(self):
        df = []
        for citation in self.citations:
            df.append(citation.content)
        return pd.DataFrame(df)

    @property
    def potentials(self):
        return self.__potentials
    
    @property
    def potentials_df(self):
        df = []
        for potential in self.potentials:
            df.append(potential.asdict())
        return pd.DataFrame(df)
    
    @property
    def implementations(self):
        return self.__implementations
    
    @property
    def implementations_df(self):
        df = []
        for implementation in self.implementations:
            df.append(implementation.asdict())
        return pd.DataFrame(df)

    def load_local_citations(self, localdir=None):
        if localdir is None:
            localdir = Path(rootdir, '..', 'data', 'bibtex')
        
        self.__citations = []
        for bibfile in localdir.glob('*.bib'):
            self.__citations.append(Citation(bibfile))

    def load_local_potentials(self, localdir=None):
        if localdir is None:
            localdir = Path(rootdir, '..', 'data', 'potential')
        
        self.__potentials = []
        for jsonfile in localdir.glob('*.json'):
            self.__potentials.append(Potential(model=jsonfile, citations=self.citations))

    def load_local_implementations(self, localdir=None):
        if localdir is None:
            localdir = Path(rootdir, '..', 'data', 'implementation')
        
        self.__implementations = []
        for jsonfile in localdir.glob('*/meta.json'):
            self.__implementations.append(Implementation(model=jsonfile, potential=self.potentials))