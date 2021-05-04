from ..tools import ModuleManager

class RecordManager(ModuleManager):
    """
    Class for managing the imported record subclass styles
    """

    def pandasfilter(self, style, dataframe, **kwargs):
        """
        Filters a pandas.DataFrame based on kwargs values for the record style.
        
        Parameters
        ----------
        style : str
            The record style.
        dataframe : pandas.DataFrame
            A table of metadata for multiple records of the record style.
        **kwargs : any
            Any of the record style-specific search parameters.
        
        Returns
        -------
        pandas.Series, numpy.NDArray?
            Boolean map of matching values
        """
        self.assert_style(style)
        return self.loaded_styles[style].pandasfilter(dataframe, **kwargs)

    def mongoquery(self, style, **kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        style : str
            The record style.
        **kwargs : any
            Any of the record style-specific search parameters.
        
        Returns
        -------
        dict
            The Mongo-style query
        """
        self.assert_style(style)
        return self.loaded_styles[style].mongoquery(**kwargs)

    def cdcsquery(self, style, **kwargs):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        style : str
            The record style.
        **kwargs : any
            Any of the record style-specific search parameters.
        
        Returns
        -------
        dict
            The Mongo-style query
        """
        self.assert_style(style)
        return self.loaded_styles[style].cdcsquery(**kwargs)