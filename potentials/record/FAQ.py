from datamodelbase.record import Record
from datamodelbase import query 

from DataModelDict import DataModelDict as DM

__all__ = ['FAQ']

class FAQ(Record):
    """
    Class for representing FAQ records that document the FAQs for the NIST
    Interatomic Potentials Repository.
    """
    def __init__(self, model=None, name=None, **kwargs):
        """
        Initializes a Record object for a given style.
        
        Parameters
        ----------
        model : str, file-like object, DataModelDict
            The contents of the record.
        name : str, optional
            The unique name to assign to the record.  If model is a file
            path, then the default record name is the file name without
            extension.
        """
        self.__question = None
        self.__answer = None
        super().__init__(model=model, name=name, **kwargs)

    @property
    def style(self):
        """str: The record style"""
        return 'FAQ'

    @property
    def modelroot(self):
        """str: The root element of the content"""
        return 'faq'
    
    @property
    def xsl_filename(self):
        """tuple: The module path and file name of the record's xsl html transformer"""
        return ('potentials.xsl', 'FAQ.xsl')

    @property
    def xsd_filename(self):
        """tuple: The module path and file name of the record's xsd schema"""
        return ('potentials.xsd', 'FAQ.xsd')

    @property
    def question(self):
        """str: The frequently asked question."""
        return self.__question

    @question.setter
    def question(self, value):
        if value is None:
            self.__question = None
        else:
            self.__question = str(value)

    @property
    def answer(self):
        """str: The answer to the frequently asked question."""
        return self.__answer

    @answer.setter
    def answer(self, value):
        if value is None:
            self.__answer = None
        else:
            self.__answer = str(value)

    def load_model(self, model, name=None):
        """
        Loads record contents from a given model.

        Parameters
        ----------
        model : str or DataModelDict
            The model contents of the record to load.
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        """
        super().load_model(model, name=name)

        faq = self.model[self.modelroot]
        self.question = faq['question']
        self.answer = faq['answer']

    def set_values(self, name=None, question=None, answer=None):
        """
        Set multiple object attributes at the same time.

        Parameters
        ----------
        name : str, optional
            The name to assign to the record.  Often inferred from other
            attributes if not given.
        question : str, optional
            The frequently asked question.
        answer : str, optional
            The answer to the frequently asked question.
        """
        if question is not None:
            self.question = question
        if answer is not None:
            self.answer = answer
        if name is not None:
            self.name = name

    def build_model(self):
        """
        Generates and returns model content based on the values set to object.
        """
        model = DM()
        model['faq'] = DM()
        model['faq']['question'] = self.question
        model['faq']['answer'] = self.answer

        self._set_model(model)
        return model

    def metadata(self):
        """
        Generates a dict of simple metadata values associated with the record.
        Useful for quickly comparing records and for building pandas.DataFrames
        for multiple records of the same style.
        """
        meta = {}
        meta['name'] = self.name
        meta['question'] = self.question
        meta['answer'] = self.answer
        return meta

    def pandasfilter(self, dataframe, name=None, question=None, answer=None):
        """
        Filters a pandas.DataFrame based on kwargs values for the record style.
        
        Parameters
        ----------
        dataframe : pandas.DataFrame
            A table of metadata for multiple records of the record style.
        name : str or list
            The record name(s) to parse by.
        question : str or list
            Term(s) to search for in the question field.
        answer : str or list
            Term(s) to search for in the answer field.
        
        Returns
        -------
        pandas.Series, numpy.NDArray
            Boolean map of matching values
        """
        matches = (
            query.str_match.pandas(dataframe, 'name', name)
            &query.str_contains.pandas(dataframe, 'question', question)
            &query.str_contains.pandas(dataframe, 'answer', answer)
        )
        return matches

    def mongoquery(self, name=None, question=None, answer=None):
        """
        Builds a Mongo-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        name : str or list
            The record name(s) to parse by.
        question : str or list
            Term(s) to search for in the question field.
        answer : str or list
            Term(s) to search for in the answer field.
        
        Returns
        -------
        dict
            The Mongo-style query
        """     
        mquery = {}
        query.str_match.mongo(mquery, f'name', name)

        root = f'content.{self.modelroot}'
        query.str_contains.mongo(mquery, f'{root}.question', question)
        query.str_contains.mongo(mquery, f'{root}.answer', answer)
        
        return mquery

    def cdcsquery(self, question=None, answer=None):
        """
        Builds a CDCS-style query based on kwargs values for the record style.
        
        Parameters
        ----------
        question : str or list
            Term(s) to search for in the question field.
        answer : str or list
            Term(s) to search for in the answer field.
        
        Returns
        -------
        dict
            The CDCS-style query
        """
        
        mquery = {}
        root = self.modelroot
        query.str_contains.mongo(mquery, f'{root}.question', question)
        query.str_contains.mongo(mquery, f'{root}.answer', answer)
        return mquery
