from DataModelDict import DataModelDict as DM

class FAQ():

    def __init__(self, model=None, question=None, answer=None):

        if model is not None:
            try:
                assert question is None
                assert answer is None
            except:
                raise ValueError('model cannot be given with any other arguments')
            self.load(model)
        else:
            self.question = question
            self.answer = answer

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

    def load(self, model):
        model = DM(model).find('faq')
        self.question = model['question']
        self.answer = model['answer']

    def html(self):
        htmlstr = ''
        if self.question is not None:
            htmlstr += f'<b>Question: {self.question}</b><br/>\n'
        if self.answer is not None:
            htmlstr += f'Answer: {self.answer}'
        
        return htmlstr

    def asmodel(self):
        model = DM()
        model['faq'] = DM()
        model['faq']['question'] = self.question
        model['faq']['answer'] = self.answer

        return model

    def asdict(self):
        return {'question': self.question, 'answer': self.answer}