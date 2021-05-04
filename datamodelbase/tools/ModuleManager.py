# coding: utf-8

class ModuleManager():
    """
    Base class for managing module subclasses
    """
    def __init__(self, parentname):
        """
        Creates a ModuleManager object

        Parameters
        ----------
        parentname : str
            Name of the parent class.  Used solely for messages.
        """
        
        self.__parentname = parentname
        self.__loaded_styles = {}
        self.__failed_styles = {}

    @property
    def parentname(self):
        """str : The name of the parent class (used for messages)"""
        return self.__parentname

    @property
    def loaded_styles(self):
        """dict : The styles that were successfully imported.  Values are the loaded modules"""
        return self.__loaded_styles
    
    @property
    def failed_styles(self):
        """dict : The styles that were unsuccessfully imported.  Values are the error messages"""
        return self.__failed_styles
    
    @property
    def loaded_style_names(self):
        """list : The names of the loaded styles"""
        return list(self.loaded_styles.keys())

    @property
    def failed_style_names(self):
        """list : The names of the loaded styles"""
        return list(self.failed_styles.keys())
    
    def check_styles(self):
        """
        Prints the list of styles that were successfully and
        unsuccessfully loaded.
        """
        print(f'{self.parentname} styles that passed import:')
        for style in self.loaded_style_names:
            print(f'- {style}')

        print(f'{self.parentname} styles that failed import:')
        for style in self.failed_style_names:
            print(f'- {style}: {self.failed_styles[style]}')
        print()

    def assert_style(self, style):
        """Checks if the style successfully loaded, throws an error otherwise."""
        if style in self.failed_style_names:
            raise ImportError(f'{self.parentname} style {style} failed import: {self.failed_styles[style]}')
        elif style not in self.loaded_style_names:
            raise KeyError(f'Unknown {self.parentname} style {style}')

    def init(self, style, *args, **kwargs):
        """
        Initializes an object of the substyle
        """
        self.assert_style(style)
        return self.loaded_styles[style](*args, **kwargs)