
from research_framework.base.plugin.base_plugin import BasePlugin
from research_framework.base.wrappers.filter_wrapper import BaseFilterWrapper
from research_framework.lightweight.lightweight import FlyWeight
from research_framework.container.container import Container

from typing import Dict, Any, Optional
import json

class FitPredictFilterWrapper(BaseFilterWrapper):
    def __init__(self, clazz:str, params:Dict[str, Any], filter_clazz: BasePlugin, fly: FlyWeight):
        self.clazz:str = clazz
        self.params:Dict[str, Any] = params
        self.filter: BasePlugin = filter_clazz(**params)
        self.fly: FlyWeight = fly
        self.hashcode:Optional[str] = None
        self.filter_name:Optional[str] = None
        self.store:bool = Container.global_config.store
        self.overwrite:bool = Container.global_config.overwrite
        
    def fit(self, data_hashcode:str, data:Any):
        
        filter_hashcode = self.fly.hashcode_from_config(self.clazz, self.params)
        trained_filter_name = f'{self.clazz}{json.dumps(self.params)}[Trained]({data_hashcode})'
        trained_filter_hashcode = self.fly.append_to_hashcode(data_hashcode, filter_hashcode, is_model=True)
        filter_trained_item = self.fly.get_item(trained_filter_hashcode)
        
        if filter_trained_item is None or self.overwrite:
            #Esto significa que no tenemos el modelo entrenado guardado.
            if callable(data):
                data = data()

            self.filter.fit(data)
            
            if self.store:
                if filter_trained_item is None:
                    if not self.fly.set_item(
                        trained_filter_name,
                        trained_filter_hashcode,
                        self.filter
                    ):
                        raise Exception("Couldn't save item")
                else:
                    if not self.fly.set_item(
                        trained_filter_name,
                        trained_filter_hashcode,
                        self.filter,
                        self.overwrite
                    ):
                        raise Exception("Couldn't save item")
            
            self.hashcode = trained_filter_hashcode
            self.filter_name = trained_filter_name
            
        else:
            self.filter = lambda : self.fly.get_data_from_item(filter_trained_item)
            self.hashcode = trained_filter_hashcode
                
            
        
    def predict(self, data_hashcode:str, data_name:str, data:Any):
        if self.hashcode is None:
            raise Exception("Model not trained, call fit() before calling predict()!")
        else:
            data_name = f'{data_name} -> {self.filter_name}'
            data_hashcode = self.fly.append_to_hashcode(data_hashcode, self.hashcode, is_model=False)
            data_item = self.fly.get_item(data_hashcode)
            
            if data_item is None or self.overwrite:
                # Esto significa que aun no hemos generado los nuevos datos
                if callable(data):
                    data = data()
                    
                if callable(self.filter) and self.filter.__name__ == "<lambda>":
                    self.filter = self.filter()
                
                data = self.filter.predict(data)
                
                if self.store:
                    if data_item is None:
                        if not self.fly.set_item(
                            data_name,
                            data_hashcode,
                            data
                        ):
                            raise Exception("Couldn't save item")
                    else:
                        if not self.fly.set_item(
                            data_name,
                            data_hashcode,
                            data,
                            self.overwrite                    
                        ):
                            raise Exception("Couldn't save item")
                
            else:
                data = lambda : self.fly.get_data_from_item(data_item)
            
            return data_hashcode, data_name, data
                

class PassThroughFilterWrapper(BaseFilterWrapper):
    def __init__(self, clazz:str, params:Dict[str, Any], filter_clazz: BasePlugin, fly: FlyWeight, *args, **kwargs):
        self.clazz:str = clazz
        self.params:Dict[str, Any] = params
        self.filter: BasePlugin = filter_clazz(**params)
        self.fly: FlyWeight = fly
        self.hashcode:Optional[str] = None
        self.filter_name:Optional[str] = f'{self.clazz}{json.dumps(self.params)}[-]'
        self.store:bool = Container.global_config.store
        self.overwrite:bool = Container.global_config.overwrite
        
    def fit(self, *args, **kwargs): ...
        
    def predict(self, data_hashcode:str, data_name:str, data):
        data_name = f'{data_name} -> {self.filter_name}'
        filter_hashcode = self.fly.hashcode_from_config(self.clazz, self.params)
        data_hashcode = self.fly.append_to_hashcode(data_hashcode, filter_hashcode, is_model=False)
        
        data_item = self.fly.get_item(data_hashcode)
            
        if data_item is None or self.overwrite:
            # Esto significa que aun no hemos generado los nuevos datos
            if callable(data):
                data = data()
            
            data = self.filter.predict(data)
            
            if self.store:
                if data_item is None:
                    if not self.fly.set_item(
                        data_name,
                        data_hashcode,
                        data                    
                    ):
                        raise Exception("Couldn't save item")
                else:
                    if not self.fly.set_item(
                        data_name,
                        data_hashcode,
                        data,
                        self.overwrite                    
                    ):
                        raise Exception("Couldn't save item")
                    
        else:
            data = lambda : self.fly.get_data_from_item(data_item)
        
        return data_hashcode, data_name, data
    

class InputFiterWrapper(BaseFilterWrapper):
    def __init__(self, clazz:str, params:Dict[str, Any], filter_clazz: BasePlugin, fly: FlyWeight, *args, **kwargs):
        self.clazz:str = clazz
        self.params:Dict[str, Any] = params
        self.filter: BasePlugin = filter_clazz(**params)
        self.fly: FlyWeight = fly
        self.store:bool = Container.global_config.store
        self.overwrite:bool = Container.global_config.overwrite
        
    def fit(self, *args, **kwargs): ...
    
    
    def predict(self, data_name:str, *args, **kwargs):
        data_hashcode = self.fly.hashcode_from_name(data_name)
        
        data_item = self.fly.get_item(data_hashcode)
        
        if data_item is None or self.overwrite:
            data = self.filter.predict(None)
            
            if self.store:
                
                if data_item is None:
                    if not self.fly.set_item(
                        data_name,
                        data_hashcode,
                        data                    
                    ):
                        raise Exception("Couldn't save item")
                else:
                    if not self.fly.set_item(
                        data_name,
                        data_hashcode,
                        data,
                        self.overwrite                    
                    ):
                        raise Exception("Couldn't save item")
            
        else:
            data = lambda: self.filter.predict(None)
        
        return data_hashcode, data_name, data
        

class DoomyFilterWrapper(BaseFilterWrapper):
    def __init__(self, clazz:str, params:Dict[str, Any], filter_clazz: BasePlugin, fly: FlyWeight, *args, **kwargs):
        self.clazz:str = clazz
        self.params:Dict[str, Any] = params
        self.filter: BasePlugin = filter_clazz(**params)
        self.fly: FlyWeight = fly
        self.hashcode = None
        self.filter_name = None

    def fit(self, data_hashcode:str, data):
        self.filter.fit(data)
        self.filter_name = f'{self.filter.gs.best_estimator_}{json.dumps(self.filter.gs.best_params_)}[Trained]({data_hashcode})'
        self.hashcode = self.fly.hashcode_from_config(self.filter.gs.best_estimator_, self.filter.gs.best_params_)
    
    def predict(self, data_hashcode: str, data_name: str, data):
        data = self.filter.predict(data)
        data_name = f'{data_name} -> {self.filter_name}'
        data_hashcode = self.fly.append_to_hashcode(data_hashcode, self.hashcode, is_model=False)
        return data_hashcode, data_name, data
    
    
class MetricFilterWrapper(BaseFilterWrapper):
    def __init__(self, clazz:str, filter_clazz:BasePlugin):
        self.clazz:str = clazz
        self.filter_clazz:BasePlugin = filter_clazz()
        
    def fit(self, *args, **kwargs): ...
    
    def predict(self, y, predicted):
        if callable(y):
            y = y()
            
        if callable(predicted):
            predicted = predicted()
        
        return self.filter_clazz.predict(y.df['label'].tolist(), predicted)
