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

def widget_lammps_potential(self):
    """
    Builds ipywidgets for selecting a LAMMPS implemented potential from the
    database, downloading the files, and displaying the LAMMPS commands
    associated with using it.
    """
    
    if self.potential_LAMMPS_df is None:
        self.load_potential_LAMMPS()
    
    # Build list of all status values
    statuses = ['all', 'active', 'superseded', 'retracted']
    
    # Build list of all unique pair_styles
    unique_pair_styles = [''] + list(np.unique(self.potential_LAMMPS_df.pair_style))

    # Build list of all unique elements
    unique_elements = set()
    for elements in self.potential_LAMMPS_df.elements.values:
        unique_elements.update(elements)
    unique_elements = [''] + sorted(list(unique_elements))
    
    # Build list of all potential ids
    potential_ids = self.potential_LAMMPS_df.id.tolist()

    # Create selection widgets
    status_dropdown = widgets.Dropdown(options=statuses, value='active', description='Status:')
    element1_dropdown = widgets.Dropdown(options=unique_elements, description='Element1:')
    element2_dropdown = widgets.Dropdown(options=unique_elements, description='Element2:')
    element3_dropdown = widgets.Dropdown(options=unique_elements, description='Element3:')
    pair_style_dropdown = widgets.Dropdown(options=unique_pair_styles, description='Pair Style:')
    potential_dropdown = widgets.Dropdown(options=potential_ids, description='Potential:')
    
    # Create interaction widgets
    potdir_text = widgets.Text(value='', description='Directory:', continuous_update=False)
    download_button = widgets.Button(description='Download Files')
    symbols_text = widgets.Text(value='', description='Symbols:', continuous_update=False)

    # Initialize outputs
    header1_output = widgets.Output()
    with header1_output:
        display(HTML('<h1>Select a LAMMPS potential</h1></br>'))
        print('Use the dropdown boxes to parse by element(s) and pair_style to select a potential.')
    
    header2_output = widgets.Output()
    def base_header2(potential):
        with header2_output:
            clear_output()
            display(HTML('<h1>Download, display commands</h1>'))
            print('To download LAMMPS files, enter a local directory and click the button.')
            print('To customize LAMMPS commands for specific element model symbols, enter a space-delimited list into the Symbols box.')
            print(f'Allowed symbols = {" ".join(potential.symbols)}')
    base_header2(self.potential_LAMMPS[0])

    download_output = widgets.Output()

    potential_output = widgets.Output()
    def show_pair_info(potential, symbols=None):
        with potential_output:
            clear_output()
            try:
                print(potential.pair_info(symbols))
            except:
                display(HTML('<b>Invalid symbols list</b>'))
    show_pair_info(self.potential_LAMMPS[0])
    
    # Define function for updating list of potentials
    def update_potential_dropdown_options(change):
        """
        Updates the list of potentials in potential_dropdown based on values in
        the other widgets.
        """
        # Set status value
        status = status_dropdown.value
        if status == 'all':
            status = None

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
        potentials = self.get_potential_LAMMPS(status=status, pair_style=pair_style, element=elements)
        
        # Update potential dropdown accordingly
        potential_dropdown.options = [pot.id for pot in potentials]

    # Tie elements, year and text widgets to above function
    element1_dropdown.observe(update_potential_dropdown_options, 'value')
    element2_dropdown.observe(update_potential_dropdown_options, 'value')
    element3_dropdown.observe(update_potential_dropdown_options, 'value')
    status_dropdown.observe(update_potential_dropdown_options, 'value')
    pair_style_dropdown.observe(update_potential_dropdown_options, 'value')
    
    # Define function for updating selected potential
    def update_selected_potential(change):
        
        symbols_text.value = ''
        # Select potential based on dropdown value
        try:
            potential = self.potential_LAMMPS[self.potential_LAMMPS_df.id == potential_dropdown.value][0]
        except:
            symbols_text.disabled = True
            download_button.disabled = True
            with potential_output:
                clear_output()
                display(HTML('<b>No matching potentials found: try different selectors</b>'))
        else:
            symbols_text.disabled = False
            download_button.disabled = False
            base_header2(potential)
            show_pair_info(potential)

    # Tie potential widget to above function
    potential_dropdown.observe(update_selected_potential, 'value')

    def update_symbols(change):
        if symbols_text.value.strip() == '':
            symbols = None
        else:
            symbols = symbols_text.value.split()

        try:
            potential = self.potential_LAMMPS[self.potential_LAMMPS_df.id == potential_dropdown.value][0]
        except:
            symbols_text.disabled = True
            download_button.disabled = True
            with potential_output:
                clear_output()
                display(HTML('<b>No matching potentials found: try different selectors</b>'))
        else:
            symbols_text.disabled = False
            download_button.disabled = False
            show_pair_info(potential, symbols)
        
    symbols_text.observe(update_symbols, 'value')

    def download_action(change):
        with download_output:
            clear_output()
            potdir = potdir_text.value
            if potdir == '':
                potdir = '.'
            try:
                potdir = Path(potdir)
                assert potdir.is_dir()
            except:
                print(f'Download directory "{potdir}"" not found/valid')
            else:
                potential = self.potential_LAMMPS[self.potential_LAMMPS_df.id == potential_dropdown.value][0]
                
                self.download_LAMMPS_files(potential, targetdir=potdir)
                print(f'Files downloaded to {Path(potdir, potential.id)}')
    download_button.on_click(download_action)

    # Display widgets and output
    display(header1_output, status_dropdown, element1_dropdown, element2_dropdown, element3_dropdown,
            pair_style_dropdown, potential_dropdown, header2_output, potdir_text, symbols_text,
             download_button, download_output, potential_output)