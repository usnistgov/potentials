# coding: utf-8
# Standard libraries
from pathlib import Path

# https://ipython.org/
from IPython.display import display, clear_output, HTML

# https://ipywidgets.readthedocs.io/en/latest/
import ipywidgets as widgets

# https://numpy.org/
import numpy as np

def widget_search_potentials(self):
    """
    Builds ipywidgets for selecting an interatomic potential from the database
    and displaying its full html representation (citation plus implementations)
    """
    if self.potentials_df is None:
        self.load_potentials()
    
    # Build list of all unique elements
    unique_elements = set()
    for elements in self.potentials_df.elements.values:
        unique_elements.update(elements)
    unique_elements = [''] + sorted(list(unique_elements))
    
    # Build list of all unique years
    def getyears(series):
        years = set()
        for citation in series.citations:
            years.add(citation.year)
        return years
    unique_years = self.potentials_df.apply(getyears, axis=1)
    unique_years = [''] + sorted(list(set().union(*unique_years)))

    # Build list of all potential ids
    potential_ids = [pot.id for pot in self.potentials]
    
    # Create selection widgets
    element1_dropdown = widgets.Dropdown(options=unique_elements, description='Element1:')
    element2_dropdown = widgets.Dropdown(options=unique_elements, description='Element2:')
    element3_dropdown = widgets.Dropdown(options=unique_elements, description='Element3:')
    year_dropdown = widgets.Dropdown(options=unique_years, description='Year:')
    author_text = widgets.Text(value='', description='Author:', continuous_update=False)
    potential_dropdown = widgets.Dropdown(options=potential_ids, description='Potential:')
    
    # Initialize output for selected potential
    potential_output = widgets.Output()  
    with potential_output:
        display(HTML(self.potentials[0].html()))
    
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

        # Call search_potentials with author, year, elements
        potentials = self.get_potentials(author=author, year=year, element=elements)
        
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
                display(HTML(potential.html()))

    # Tie potential widget to above function
    potential_dropdown.observe(display_selected_potential, 'value')

    # Display widgets and output
    display(element1_dropdown, element2_dropdown, element3_dropdown,
            year_dropdown, author_text, potential_dropdown, potential_output)

def widget_lammps_potential(self, results=None):
    """
    Builds ipywidgets for selecting a LAMMPS implemented potential from the
    database, downloading the files, and displaying the LAMMPS commands
    associated with using it.

    Parameters
    ----------
    results : dict, optional
        If given a dict, the selected potential can be retrieved under the
        'lammps_potential' key.
    """
    
    if results is None:
        results = {}

    if self.lammps_potentials_df is None:
        self.load_lammps_potentials()
    
    # Build list of all unique pair_styles
    unique_pair_styles = [''] + list(np.unique(self.lammps_potentials_df.pair_style))

    # Build list of all unique elements
    unique_elements = set()
    for elements in self.lammps_potentials_df.elements.values:
        unique_elements.update(elements)
    unique_elements = [''] + sorted(list(unique_elements))
    
    # Build list of all potential ids
    potential_ids = self.lammps_potentials_df.id.tolist()

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

        # Call search_potentials with author, year, elements
        potentials = self.get_lammps_potentials(pair_style=pair_style, element=elements)
        
        # Update potential dropdown accordingly
        potential_dropdown.options = [pot.id for pot in potentials]

    # Tie elements, year and text widgets to above function
    element1_dropdown.observe(update_potential_dropdown_options, 'value')
    element2_dropdown.observe(update_potential_dropdown_options, 'value')
    element3_dropdown.observe(update_potential_dropdown_options, 'value')
    pair_style_dropdown.observe(update_potential_dropdown_options, 'value')
    
    # Define function for updating selected potential
    def update_selected_potential(change=None):
        
        # Select potential based on dropdown value
        try:
            potential = self.get_lammps_potential(id=potential_dropdown.value)
        except:
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
            potential = self.get_lammps_potential(id = potential_dropdown.value, get_files=True)
            results['lammps_potential'] = potential
            print(f'Parameter files copied/downloaded to {Path(potential.id)}')
    download_button.on_click(download_action)

    # Display widgets and output
    display(header1_output, element1_dropdown, element2_dropdown, element3_dropdown,
            pair_style_dropdown, potential_dropdown, download_button, download_output)