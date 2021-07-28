from datamodelbase.record import Record
from datamodelbase import query 

from DataModelDict import DataModelDict as DM

modelroot = 'faq'

__all__ = ['FAQ']

class FAQ(Record):

    def __init__(self, model=None, name=None, **kwargs):

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
        return modelroot
    
    @property
    def xsl_filename(self):
        return ('potentials.xsl', 'FAQ.xsl')

    @property
    def xsd_filename(self):
        return ('potentials.xsd', 'FAQ.xsd')

    @property
    def question(self):
        return self.__question

    @question.setter
    def question(self, value):
        if value is None:
            self.__question = None
        else:
            self.__question = str(value)

    @property
    def answer(self):
        return self.__answer

    @answer.setter
    def answer(self, value):
        if value is None:
            self.__answer = None
        else:
            self.__answer = str(value)

    def load_model(self, model, name=None):

        super().load_model(model, name=name)

        faq = self.model[modelroot]
        self.question = faq['question']
        self.answer = faq['answer']

    def set_values(self, name=None, question=None, answer=None):
        if question is not None:
            self.question = question
        if answer is not None:
            self.answer = answer
        if name is not None:
            self.name = name

    def build_model(self):
        model = DM()
        model['faq'] = DM()
        model['faq']['question'] = self.question
        model['faq']['answer'] = self.answer

        self._set_model(model)
        return model

    def metadata(self):
        meta = {}
        meta['name'] = self.name
        meta['question'] = self.question
        meta['answer'] = self.answer
        return meta

    @staticmethod
    def pandasfilter(dataframe, name=None, question=None, answer=None):
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

    @staticmethod
    def mongoquery(name=None, question=None, answer=None):
        mquery = {}
        query.str_match.mongo(mquery, f'name', name)

        root = f'content.{modelroot}'
        query.str_contains.mongo(mquery, f'{root}.question', question)
        query.str_contains.mongo(mquery, f'{root}.answer', answer)
        
        return mquery

    @staticmethod
    def cdcsquery(question=None, answer=None):
        mquery = {}
        root = modelroot
        query.str_contains.mongo(mquery, f'{root}.question', question)
        query.str_contains.mongo(mquery, f'{root}.answer', answer)
        return mquery
