from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator

class BasePlugin(ABC):
    @abstractmethod
    def fit(*args, **kwargs): ...
    
    @abstractmethod
    def predict(*args, **kwargs): ...

class BaseFilterPlugin(BasePlugin, BaseEstimator):...