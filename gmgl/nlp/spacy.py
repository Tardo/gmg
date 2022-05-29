# GMG Copyright 2022 - Alexandre Díaz
import spacy
from flask import current_app, _app_ctx_stack


class SpacyNLP(object):
    _model_name = 'es_dep_news_trf'

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        with app.app_context():
            try:
                self._pipe = spacy.load(self._model_name)
            except OSError as error:
                spacy.cli.download(self._model_name)
                self._pipe = spacy.load(self._model_name)

    def analyze_text(self, data):
        doc = self.pipe(data)
        for token in doc:
            print(token.text, token.pos_, token.dep_)
        return doc

    @property
    def pipe(self):
        return self._pipe


spacy_nlp = SpacyNLP()
