import numpy as np
import pandas as pd



class Tersoff():
    """Class for building and manipulating LAMMPS tersoff parameter files"""

    # Class imports
    from ._abop import abop

    def __init__(self, symbols, pair_style='tersoff'):
        """
        Initializes the class and builds a parameter table.

        Parameters
        ----------
        symbols : list
            The list of element model symbols the potential represents.
        pair_style : str, optional
            The specific LAMMPS tersoff pair_style.  Accepted values are
            'tersoff', 'tersoff/mod', 'tersoff/mod/c' and 'tersoff/zbl'.
        """
        self.init_params(symbols, pair_style=pair_style)

    def __str__(self):
        return self.text()
    
    @property
    def symbols(self) -> list:
        """list: The element model symbols represented by this potential"""
        return self.__symbols
    
    @property
    def pair_style(self) -> str:
        """str: The LAMMPS pair_style for the tersoff potential"""
        return self.__pair_style

    def init_params(self, symbols, pair_style='tersoff'):
        """
        (Re)Initializes the parameter table.

        Parameters
        ----------
        symbols : list
            The list of element model symbols the potential represents.
        pair_style : str, optional
            The specific LAMMPS tersoff pair_style.  Accepted values are
            'tersoff', 'tersoff/mod', 'tersoff/mod/c' and 'tersoff/zbl'.
        """
        self.__symbols = symbols

        if pair_style == 'tersoff':
            self.__init_tersoff_params()
        elif pair_style == 'tersoff/mod':
            self.__init_tersoff_mod_params()
        elif pair_style == 'tersoff/mod/c':
            self.__init_tersoff_mod_c_params()
        elif pair_style == 'tersoff/zbl':
            self.__init_tersoff_zbl_params()
        else:
            raise ValueError(f'invalid/unsupported pair_style {pair_style}')
        
        self.__pair_style = pair_style

    def __iter_symbols_list(self):
        """
        Generates all the ternary combinations for the element model symbols.
        """
        symbols = self.symbols
        e1 = []
        e2 = []
        e3 = []
        for i in range(len(symbols)):
            for j in range(len(symbols)):
                for k in range(len(symbols)):
                    e1.append(symbols[i])
                    e2.append(symbols[j])
                    e3.append(symbols[k])

        return e1, e2, e3

    def __init_tersoff_params(self):
        """Initializes the parameters for the tersoff pair_style format"""
        e1, e2, e3 = self.__iter_symbols_list()
        nrows = len(e1)
        self.params = pd.DataFrame(dict(
            e1 = e1,
            e2 = e2,
            e3 = e3,
            m = np.ones(nrows, dtype=int),
            gamma = np.zeros(nrows),
            lambda3 = np.zeros(nrows),
            c = np.zeros(nrows),
            d = np.zeros(nrows),
            costheta0 = np.zeros(nrows),
            n = np.ones(nrows),
            beta = np.ones(nrows),
            lambda2 = np.zeros(nrows),
            B = np.zeros(nrows),
            Rcut = np.zeros(nrows),
            D = np.zeros(nrows),
            lambda1 = np.zeros(nrows),
            A = np.zeros(nrows)))

    def __init_tersoff_mod_params(self):
        """Initializes the parameters for the tersoff/mod pair_style format"""
        e1, e2, e3 = self.__iter_symbols_list()
        nrows = len(e1)
        self.params = pd.DataFrame(dict(
            e1 = e1,
            e2 = e2,
            e3 = e3,
            beta = np.ones(nrows),
            alpha = np.ones(nrows),
            h = np.zeros(nrows),
            eta = np.zeros(nrows),
            beta_ters = np.ones(nrows, dtype=int),
            lambda2 = np.zeros(nrows),
            B = np.zeros(nrows),
            R = np.zeros(nrows),
            D = np.zeros(nrows),
            lambda1 = np.zeros(nrows),
            A = np.zeros(nrows),
            n = np.zeros(nrows),
            c1 = np.zeros(nrows),
            c2 = np.zeros(nrows),
            c3 = np.zeros(nrows),
            c4 = np.zeros(nrows),
            c5 = np.zeros(nrows)))

    def __init_tersoff_mod_c_params(self):
        """Initializes the parameters for the tersoff/mod/c pair_style format"""
        e1, e2, e3 = self.__iter_symbols_list()
        nrows = len(e1)
        self.params = pd.DataFrame(dict(
            e1 = e1,
            e2 = e2,
            e3 = e3,
            beta = np.ones(nrows),
            alpha = np.ones(nrows),
            h = np.zeros(nrows),
            eta = np.zeros(nrows),
            beta_ters = np.ones(nrows, dtype=int),
            lambda2 = np.zeros(nrows),
            B = np.zeros(nrows),
            R = np.zeros(nrows),
            D = np.zeros(nrows),
            lambda1 = np.zeros(nrows),
            A = np.zeros(nrows),
            n = np.zeros(nrows),
            c1 = np.zeros(nrows),
            c2 = np.zeros(nrows),
            c3 = np.zeros(nrows),
            c4 = np.zeros(nrows),
            c5 = np.zeros(nrows),
            c0 = np.zeros(nrows)))
        
    def __init_tersoff_zbl_params(self):
        """Initializes the parameters for the tersoff/zbl pair_style format"""
        e1, e2, e3 = self.__iter_symbols_list()
        nrows = len(e1)
        self.params = pd.DataFrame(dict(
            e1 = e1,
            e2 = e2,
            e3 = e3,
            m = np.ones(nrows, dtype=int),
            gamma = np.zeros(nrows),
            lambda3 = np.zeros(nrows),
            c = np.zeros(nrows),
            d = np.zeros(nrows),
            costheta0 = np.zeros(nrows),
            n = np.ones(nrows),
            beta = np.ones(nrows),
            lambda2 = np.zeros(nrows),
            B = np.zeros(nrows),
            Rcut = np.zeros(nrows),
            D = np.zeros(nrows),
            lambda1 = np.zeros(nrows),
            A = np.zeros(nrows),
            Z_i = np.zeros(nrows, dtype=int),
            Z_j = np.zeros(nrows, dtype=int),
            ZBLcut = np.zeros(nrows),
            ZBLexpscale = np.zeros(nrows)))

    def text(self, headers: str = '') -> str:
        """
        Builds the parameter file contents as a str.

        Parameters
        ----------
        headers : str
            Any custom header content that you wish to add.  Can be as many
            lines as you like by including newline characters.  Will
            automatically add comment hashtag symbols at the beginning of any
            line if they are needed.  NOTE that the parameter table header
            (i.e. parameter labels) will be auto-generated and thus does not
            needed to be included in this.

        Returns
        -------
        paramstr : str
            The fully compiled comments and potential parameters.
        """
        # Split headers into separate lines
        if headers == '':
            hlines = []
        else:
            hlines = headers.splitlines()
        
        # Add comment hashtag to non-blank lines that don't already start with it
        for i in range(len(hlines)):
            if len(hlines[i].strip()) > 0 and hlines[i].strip()[0] != '#':
                hlines[i] = '#' + hlines[i]
        
        lines = ['' for i in range(len(self.params)+1)]

        # Loop over all keys
        first = True
        for key in self.params.keys():
            l = 3
            
            # Add comment hashtag to first header key
            if first:
                v = '#' + key
                first = False
            else:
                v = key
            
            vals = [v]
            if len(v) > l:
                l = len(v)
            
            for i in self.params.index:
                v = str(self.params.loc[i, key])
                vals.append(v)
                if len(v) > l:
                    l = len(v)

            for i in range(len(lines)):
                lines[i] += f'{vals[i]:{l}} '

        # Compile all parameter lines together
        paramstr = '\n'.join(hlines + lines)
        
        return paramstr

    def save(self, fname, headers:str = ''):
        """
        Generates the parameters in the LAMMPS format and saves them to a file.

        Parameters
        ----------
        fname : path-like object
            The name/path of the file to save the parameters to.
        headers : str
            Any custom header content that you wish to add.  Can be as many
            lines as you like by including newline characters.  Will
            automatically add comment hashtag symbols at the beginning of any
            line if they are needed.  NOTE that the parameter table header
            (i.e. parameter labels) will be auto-generated and thus does not
            needed to be included in this.
        """
        paramstr = self.text(headers=headers)

        with open(fname, 'w') as f:
            f.write(paramstr)