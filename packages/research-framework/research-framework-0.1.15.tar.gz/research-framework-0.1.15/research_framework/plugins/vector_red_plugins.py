from research_framework.container.container import Container
from research_framework.base.plugin.base_plugin import BaseFilterPlugin
from research_framework.lightweight.wrappers import FitPredictFilterWrapper

from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import MaxAbsScaler

import scipy

@Container.bind(FitPredictFilterWrapper)
class MaTruncatedSVD(BaseFilterPlugin):
    def __init__(self, n_components=3, n_iter=7, random_state=42):
        self.n_components=n_components
        self.n_iter=n_iter
        self.random_state=random_state
        
    def fit(self, x, *args, **kwargs):
        if type(x) == list or scipy.sparse.issparse(x):
            self.scaler = MaxAbsScaler().fit(x)
            self.pca = TruncatedSVD(self.n_components, n_iter=self.n_iter, random_state=self.random_state).fit(self.scaler.transform(x))
        else:
            self.scaler = MaxAbsScaler().fit(x.vectors)
            self.pca = TruncatedSVD(self.n_components, n_iter=self.n_iter, random_state=self.random_state).fit(self.scaler.transform(x.vectors))
        return self
        
    def predict(self, x):
        if type(x) == list or scipy.sparse.issparse(x):
            x = self.pca.transform(self.scaler.transform(x))
        else:
            x.vectors = self.pca.transform(self.scaler.transform(x.vectors))
        return x
    
    def transform(self, x):
        return self.predict(x)
    