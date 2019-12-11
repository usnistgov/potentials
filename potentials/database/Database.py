from pathlib import Path
import pandas as pd
import numpy as np

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML

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
                        if val not in series[columnname]:
                            return False
                    return True
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

    def widget_select_potential_metadata(self):
        """
        Builds ipywidgets for selecting an interatomic potential from the database
        and displaying its full html representation (citation plus implementations)
        """
        # Build list of all unique elements
        unique_elements = set()
        for elements in self.potentials_df.elements.values:
            unique_elements.update(elements)
        unique_elements = [''] + list(sorted(unique_elements))
        
        # Build list of all potentials
        all_potentials = self.search_potentials()
        
        # Create selection widgets
        element1_dropdown = widgets.Dropdown(options=unique_elements, description='Element1:')
        element2_dropdown = widgets.Dropdown(options=unique_elements, description='Element2:')
        element3_dropdown = widgets.Dropdown(options=unique_elements, description='Element3:')
        year_dropdown = widgets.Dropdown(options=[''] + [str(i) for i in range(1985,2020)], description='Year:')
        author_text = widgets.Text(value='', description='Author:')
        potential_dropdown = widgets.Dropdown(options=[pot.id for pot in all_potentials],
                                            description='Potential:')
        
        # Initialize output for selected potential
        potential_output = widgets.Output()  
        with potential_output:
            display(HTML(self.full_html(all_potentials[0])))
        
        # Define function for updating list of potentials
        def update_potential_dropdown_options(change):
            """
            Updates the list of potentials in potential_dropdown based on values in
            the other widgets.
            """
            # Set elements value
            elements = []
            if element1_dropdown.value != '':
                elements.append(element1_dropdown.value)
            if element2_dropdown.value != '':
                elements.append(element2_dropdown.value)
            if element3_dropdown.value != '':
                elements.append(element3_dropdown.value)
            if len(elements) == 0:
                elements = None

            # Set year value
            if year_dropdown != '':
                year = year_dropdown.value
            else:
                year = None

            # Set author value
            if author_text != '':
                author = author_text.value
            else:
                author = None

            # Call search_potentials with author, year, elements
            potentials = self.search_potentials(author, year, elements)
            
            # Update potential dropdown accordingly
            potential_dropdown.options = [pot.id for pot in potentials]

        # Tie elements, year and text widgets to above function
        element1_dropdown.observe(update_potential_dropdown_options, 'value')
        element2_dropdown.observe(update_potential_dropdown_options, 'value')
        element3_dropdown.observe(update_potential_dropdown_options, 'value')
        year_dropdown.observe(update_potential_dropdown_options, 'value')
        author_text.observe(update_potential_dropdown_options, 'value')
        
        # Define function for updating selected potential
        def display_selected_potential(change):
            
            # Select potential based on dropdown value
            try:
                potential = self.potentials[self.potentials_df.id == potential_dropdown.value][0]
            except:
                with potential_output:
                    clear_output()
                    display(HTML('<b>No matching potentials found: try different selectors</b>'))
            else:
                # Update potential output
                with potential_output:
                    clear_output()
                    display(HTML(self.full_html(potential)))

        # Tie potential widget to above function
        potential_dropdown.observe(display_selected_potential, 'value')

        # Display widgets and output
        display(element1_dropdown, element2_dropdown, element3_dropdown,
                year_dropdown, author_text, potential_dropdown, potential_output)