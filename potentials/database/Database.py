from pathlib import Path
import pandas as pd
import numpy as np

from .. import rootdir
from ..tools import aslist
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
        return np.array(self.__citations)
    
    @property
    def citations_df(self):
        df = []
        for citation in self.citations:
            df.append(citation.content)
        return pd.DataFrame(df)

    @property
    def potentials(self):
        return np.array(self.__potentials)
    
    @property
    def potentials_df(self):
        df = []
        for potential in self.potentials:
            df.append(potential.asdict())
        return pd.DataFrame(df)
    
    @property
    def implementations(self):
        return np.array(self.__implementations)
    
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

    def full_html(self, potential):
        """
        Generates HTML content string for a Potential and listing all associated
        implementations.

        Parameters
        ----------
        potential : Potential
            The Potential to generate the HTML content for.

        Returns
        -------
        str
            The HTML content for the Potential and any associated Implementations
        """


        htmlstr = potential.html() 

        # Display html of all implementations associated with the above potential
        imp_df = self.implementations_df.sort_values(['date', 'id'])
        indices = imp_df.index[imp_df.potential == potential]
        for imp in self.implementations[indices]:
            htmlstr += '<br/>\n' + imp.html(full=False)
        
        return htmlstr

    def search_potentials(self, author=None, year=None, elements=None):
        """
        Search for potentials in the database matching the given fields.

        Parameters
        ----------
        author : str, optional
            Author string to search for.  Note that the citation info must
            exactly contain this field, so multiple authors not supported yet.
        year : str, optional
            Publication year to search for.
        elements : list, optional
            Element models to search for.  If multiple elements are listed, the
            results will be inclusive, i.e. any potentials with at least one of
            the elements will be included.

        Returns
        -------
        list of Potential
            A list of all of the matching Potential objects.
        """


        def str_in_column(series, columnname, string=None):
            """
            Utility function for pandas apply() to find rows where the specified column contains
            a certain string value.
            
            Parameters
            ----------
            series : pandas.Series
                The Series (row) to check
            columnname : str
                The column name to check
            string : str or None, optional
                The string to check if included in the row-column value.  If None (default), then
                the function will always return True.
            
            Returns 
            -------
            bool
                True if string is in the row-column value or string is None, False otherwise.
            """
            if string is None:
                return True
            else:
                if isinstance(series[columnname], str):
                    return str(string) in series[columnname]
                else:
                    return False
        
        def cite_match(series, citations=None):
            """
            Utility function for pandas apply() to match citations to potentials
            
            Parameters
            ----------
            series : pandas.Series
                The Series (row) to check
            listvals : str or None, optional
                The list of terms to compare to the row-column list.
            
            Returns 
            -------
            bool
                True if string is in the row-column value or string is None, False otherwise.
            """
            if citations is None:
                return True
            else:
                if isinstance(series.dois, list):
                    for citation in citations:
                        if citation.doi in series.dois:
                            return True
                    return False
                else:
                    return False
                
        def list_match(series, columnname, listvals=None):
            """
            Utility function for pandas apply() to match rows that are lists to 
            
            Parameters
            ----------
            series : pandas.Series
                The Series (row) to check
            columnname : str
                The column name to check
            listvals : str or None, optional
                The list of terms to compare to the row-column list.
            
            Returns 
            -------
            bool
                True if string is in the row-column value or string is None, False otherwise.
            """
            if listvals is None:
                return True
            else:
                if isinstance(series[columnname], list):
                    for val in aslist(listvals):
                        if val in series[columnname]:
                            return True
                    return False
                else:
                    return False

        # Parse citation info for matching author and year
        cite_df = self.citations_df
        citations = self.citations[
            (cite_df.apply(str_in_column, args=('year', year), axis=1))
            &(cite_df.apply(str_in_column, args=('author', author), axis=1))
        ]
    
        # Parse potential info for matching citation and elements
        pot_df = self.potentials_df
        indices = pot_df[
            (pot_df.apply(cite_match, args=(citations,), axis=1))
            &(pot_df.apply(list_match, args=('elements', elements), axis=1))
            ].sort_values('id').index
        
        return self.potentials[indices]