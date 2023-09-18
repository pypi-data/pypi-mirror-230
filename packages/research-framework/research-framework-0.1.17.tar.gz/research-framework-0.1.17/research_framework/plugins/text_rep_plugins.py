from typing import Dict, Any
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from research_framework.base.plugin.base_plugin import BaseFilterPlugin
from research_framework.container.container import Container
from research_framework.dataset.standard_dataset import StandardDataset
from research_framework.lightweight.wrappers import FitPredictFilterWrapper

import pandas as pd
import numpy as np

@Container.bind(FitPredictFilterWrapper)
class Tf(BaseFilterPlugin):
    def __init__(self, lowercase=True):
        self.lowercase = lowercase
        self.model = CountVectorizer(lowercase=self.lowercase)


    def set_params(self, **params):
        aux = super().set_params(**params)
        self.model = CountVectorizer(lowercase=self.lowercase)
        return aux

    def fit(self, x, y=None):
        if type(x) == pd.DataFrame:
            self.model.fit(x.text)
        elif type(x) == list:
            self.model.fit(x)
        return self
        
    def transform(self, x):
        return self.predict(x)

    def predict(self, x ):
        if type(x) == pd.DataFrame:
            return StandardDataset(x, self.model.transform(x.text))
        elif type(x) == list:
            return self.model.transform(x)
    


@Container.bind(FitPredictFilterWrapper)
class TfIdf(BaseFilterPlugin):
    def __init__(self, lowercase=True):
        self.lowercase = lowercase
        self.model = TfidfVectorizer(lowercase=self.lowercase)

    def set_params(self, **params):
        aux = super().set_params(**params)
        self.model = TfidfVectorizer(lowercase=self.lowercase)
        return aux
    
    def fit(self, x, _):
        if type(x) == pd.DataFrame:
            self.model.fit(x.text)
        elif type(x) == list:
            self.model.fit(x)
        return self
        
    def transform(self, x):
        return self.predict(x)

    def predict(self, x):
        if type(x) == pd.DataFrame:
            return StandardDataset(x, self.model.transform(x.text))
        elif type(x) == list:
            return self.model.transform(x)
            
        

