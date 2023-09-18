from abc import ABC, abstractmethod
from typing import Any
from research_framework.lightweight.model.item_model import ItemModel

class BaseFlyweight(ABC):
    
    @staticmethod
    @abstractmethod
    def hashcode_from_name(name): ...
        
    @staticmethod
    @abstractmethod
    def hashcode_from_config(clazz, params):...
        
    @staticmethod
    @abstractmethod
    def append_to_hashcode(hashcode, hashcode2, is_model=False): ...
    
    @abstractmethod
    def get_item(self, hash_code):...
    @abstractmethod
    def get_wrapped_data_from_item(self, item): ...
    @abstractmethod
    def get_data_from_item(self, item): ...
    @abstractmethod
    def set_item(self, name:str, hashcode:str, data:Any):...
    @abstractmethod                
    def unset_item(self, hashcode:str):...