from research_framework.base.container.base_container import BaseContainer
import os
from pymongo import MongoClient
from typing import Dict, Any, Type
from research_framework.base.container.model.bind_model import BindModel
from research_framework.base.flyweight.base_flyweight import BaseFlyweight
from research_framework.base.plugin.base_plugin import BasePlugin
from research_framework.base.storage.google_storage import BucketStorage
from research_framework.base.wrappers.filter_wrapper import BaseFilterWrapper
from dotenv import load_dotenv
from typing import Optional




load_dotenv()

class Container(BaseContainer):
    fly: BaseFlyweight = None
    client: MongoClient = MongoClient(os.environ["HOST"], tls=False)
    storage: BucketStorage = BucketStorage()
    BINDINGS: Dict[str, BindModel] = dict()
    
    
    @staticmethod
    def register_dao(collection):
        def fun_decorator(fun):
            fun()(Container.client['framework_test'][collection])
            return fun
        return fun_decorator
    

    @staticmethod
    def bind(wrapper:Optional[BaseFilterWrapper]=None):
        def inner(func):
                
            Container.BINDINGS[func.__name__] = BindModel(
                wrapper=wrapper,
                plugin=func)
                
            return func
        return inner
    
    @staticmethod
    def get_filter(clazz:str, params:Dict[str, Any]) -> BaseFilterWrapper:
        bind: BindModel  = Container.BINDINGS[clazz]
        return bind.wrapper(clazz, params, bind.plugin, Container.fly)
    
    @staticmethod
    def get_model(clazz:str, params:Dict[str, Any]) -> BasePlugin:
        bind: BindModel  = Container.BINDINGS[clazz]
        return bind.plugin(**params)
    
    @staticmethod
    def get_clazz(clazz:str) -> Type[BasePlugin]:
        bind: BindModel  = Container.BINDINGS[clazz]
        return bind.plugin
    
        