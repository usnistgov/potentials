# coding: utf-8
# Standard libraries
from typing import Optional

# https://ipython.org/
from IPython.display import display, clear_output, HTML

# https://ipywidgets.readthedocs.io/en/latest/
import ipywidgets as widgets

# https://numpy.org/
import numpy as np
import numpy.typing as npt

# https://pandas.pydata.org/
import pandas as pd

# Local imports
from .. import load_record

def widget_search_potentials(self,
                             potentials: Optional[npt.ArrayLike] = None,
                             potentials_df: Optional[pd.DataFrame] = None):
    """
    Builds ipywidgets for selecting an interatomic potential from the database
    and displaying its full html representation (citation plus implementations)

    Parameters
    ----------
    potentials : array-like object, optional
        A list of Potential records to search over.  If not given, will
        call get_potentials.
    potentials_df : pandas.Dataframe, optional
        The metadata Dataframe corresponding to the potentials records.
        If not given, will be generated from potentials if given or by
        calling get_potentials with status='active'.
    """
    # Build potentials and/or potentials_df if needed
    if potentials is None:
        potentials, potentials_df = self.get_potentials(return_df=True)
    elif potentials_df is None:
        potentials_df = []
        for potential in potentials:
            potentials_df.append(potential.metadata())
        potentials_df = pd.DataFrame((potentials_df))

    # Build list of all unique elements
    unique_elements = set()
    for elements in potentials_df.elements.values:
        unique_elements.update(elements)
    unique_elements = [''] + sorted(list(unique_elements))
    
    # Build list of all unique years
    def getyears(series):
        years = set()
        for citation in series.citations:
            years.add(citation['year'])
        return years
    unique_years = potentials_df.apply(getyears, axis=1)
    unique_years = [''] + sorted(list(set().union(*unique_years)))

    # Build list of all potential ids
    potential_ids = potentials_df.id.tolist()
    
    # Create selection widgets
    element1_dropdown = widgets.Dropdown(options=unique_elements, description='Element1:')
    element2_dropdown = widgets.Dropdown(options=unique_elements, description='Element2:')
    element3_dropdown = widgets.Dropdown(options=unique_elements, description='Element3:')
    year_dropdown = widgets.Dropdown(options=unique_years, description='Year:')
    author_text = widgets.Text(value='', description='Author:', continuous_update=False)
    potential_dropdown = widgets.Dropdown(options=potential_ids, description='Potential:')
    
    # Initialize outputs
    header1_output = widgets.Output()
    with header1_output:
        display(HTML('<h1>Search potential listings</h1></br>'))

    # Initialize output for selected potential
    potential_output = widgets.Output()  
    with potential_output:
        potentials[0].html(render=True)
    
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
        if year_dropdown.value != '':
            year = year_dropdown.value
        else:
            year = None

        # Set author value
        if author_text.value != '':
            author = author_text.value
        else:
            author = None

        # Parse potentials using author, year, elements
        matches = potentials_df[load_record('Potential').pandasfilter(potentials_df, author=author, year=year, element=elements)]
        
        # Update potential dropdown accordingly
        potential_dropdown.options = matches.id.tolist()

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
            potential = potentials[potentials_df.id == potential_dropdown.value][0]
        except IndexError:
            with potential_output:
                clear_output()
                display(HTML('<b>No matching potentials found: try different selectors</b>'))
        else:
            # Update potential output
            with potential_output:
                clear_output()
                potential.html(render=True)

    # Tie potential widget to above function
    potential_dropdown.observe(display_selected_potential, 'value')

    # Display widgets and output
    display(header1_output, element1_dropdown, element2_dropdown, element3_dropdown,
            year_dropdown, author_text, potential_dropdown, potential_output)

def widget_lammps_potential(self,
                            lammps_potentials: Optional[npt.ArrayLike] = None,
                            lammps_potentials_df: Optional[pd.DataFrame] = None,
                            results: Optional[dict] = None):
    """
    Builds ipywidgets for selecting a LAMMPS implemented potential from the
    database, downloading the files, and displaying the LAMMPS commands
    associated with using it.

    Parameters
    ----------
    lammps_potentials : array-like object, optional
        A list of PotentialLAMMPS records to search over.  If not given, will
        call get_lammps_potentials with status='active'.
    lammps_potentials_df : pandas.Dataframe, optional
        The metadata Dataframe corresponding to the lammps_potentials records.
        If not given, will be generated from lammps_potentials if given or by
        calling get_lammps_potentials with status='active'.
    results : dict, optional
        If given a dict, the selected potential can be retrieved under the
        'lammps_potential' key.
    """
    
    if results is None:
        results = {}

    # Build lammps_potentials and/or lammps_potentials_df if needed
    if lammps_potentials is None:
        lammps_potentials, lammps_potentials_df = self.get_lammps_potentials(status='active', return_df=True)
    elif lammps_potentials_df is None:
        lammps_potentials_df = []
        for potential in lammps_potentials:
            lammps_potentials_df.append(potential.metadata())
        lammps_potentials_df = pd.DataFrame((lammps_potentials_df))
    
    # Build list of all unique pair_styles
    unique_pair_styles = [''] + list(np.unique(lammps_potentials_df.pair_style))

    # Build list of all unique elements
    unique_elements = set()
    for elements in lammps_potentials_df.elements.values:
        unique_elements.update(elements)
    unique_elements = [''] + sorted(list(unique_elements))
    
    # Build list of all potential ids
    potential_ids = lammps_potentials_df.id.tolist()

    # Create selection widgets
    element1_dropdown = widgets.Dropdown(options=unique_elements, description='Element1:')
    element2_dropdown = widgets.Dropdown(options=unique_elements, description='Element2:')
    element3_dropdown = widgets.Dropdown(options=unique_elements, description='Element3:')
    pair_style_dropdown = widgets.Dropdown(options=unique_pair_styles, description='Pair Style:')
    potential_dropdown = widgets.Dropdown(options=potential_ids, description='Potential:')
    
    # Create interaction widgets
    download_button = widgets.Button(description='Copy Files')

    # Initialize outputs
    header1_output = widgets.Output()
    with header1_output:
        display(HTML('<h1>Select a LAMMPS potential</h1></br>'))
        print('Use the dropdown boxes to parse and select a potential. If you wish')
        print('to copy/download the parameter files to the current working directory')
        print('then click "Copy Files" after selection.')

    download_output = widgets.Output()
    
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

        # Set pair_style value
        pair_style = pair_style_dropdown.value
        if pair_style == '':
            pair_style = None

        # Parse for pair_style and elements
        matches = lammps_potentials_df[load_record('potential_LAMMPS').pandasfilter(lammps_potentials_df, pair_style=pair_style, elements=elements)]
        
        # Update potential dropdown accordingly
        potential_dropdown.options = matches.id.tolist()

    # Tie elements, year and text widgets to above function
    element1_dropdown.observe(update_potential_dropdown_options, 'value')
    element2_dropdown.observe(update_potential_dropdown_options, 'value')
    element3_dropdown.observe(update_potential_dropdown_options, 'value')
    pair_style_dropdown.observe(update_potential_dropdown_options, 'value')
    
    # Define function for updating selected potential
    def update_selected_potential(change=None):
        
        # Select potential based on dropdown value
        try:
            potential = lammps_potentials[lammps_potentials_df.id == potential_dropdown.value][0]
        except IndexError:
            download_button.disabled = True
            with download_output:
                clear_output()
                display(HTML('<b>No matching potentials found: try different selectors</b>'))
            results.pop('lammps_potential', None)
        else:
            results['lammps_potential'] = potential
            download_button.disabled = False

    # Tie potential widget to above function
    potential_dropdown.observe(update_selected_potential, 'value')
    update_selected_potential()

    def download_action(change=None):
        with download_output:
            clear_output()
            results['lammps_potential'].download_files(verbose=True)
    download_button.on_click(download_action)

    # Display widgets and output
    display(header1_output, element1_dropdown, element2_dropdown, element3_dropdown,
            pair_style_dropdown, potential_dropdown, download_button, download_output)