from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from research_framework.base.wrappers.filter_wrapper import BaseFilterWrapper

class BaseContainer(ABC):
    
    @staticmethod
    def register_dao(collection):...
    

    @staticmethod
    def bind(wrapper:Optional[BaseFilterWrapper]=None):...
    
    @staticmethod
    def get_filter(clazz:str, params:Dict[str, Any]) -> BaseFilterWrapper:...
    