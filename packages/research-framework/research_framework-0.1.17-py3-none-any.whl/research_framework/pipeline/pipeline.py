from research_framework.base.flyweight.base_flyweight import BaseFlyweight

from research_framework.base.wrappers.filter_wrapper import BaseFilterWrapper
from research_framework.container.container import Container
from research_framework.pipeline.model.pipeline_model import PipelineModel
from research_framework.lightweight.lightweight import FlyWeight
from research_framework.lightweight.model.item_model import ItemModel

class FitPredictPipeline:
    def __init__(self, doc:PipelineModel):
        self.pipeline:PipelineModel = doc 
        self.fly:BaseFlyweight = FlyWeight()
    
        
    def start(self) -> None:
        try:
            train_input = self.pipeline.train_input
            test_input = self.pipeline.test_input
            
            train_input_wrapper = Container.get_filter(train_input.clazz,train_input.params)
            test_input_wrapper = Container.get_filter(test_input.clazz, test_input.params)
            
            train_hash, train_name, train_f = train_input_wrapper.predict(data_name=train_input.name)
            test_hash, test_name, test_f = test_input_wrapper.predict(data_name=test_input.name)
            
            train_input.items.append(Container.fly.get_item(train_hash))
            test_input.items.append(Container.fly.get_item(test_hash))
            
            for filter_model in self.pipeline.filters:
                filter_wrapper:BaseFilterWrapper = Container.get_filter(filter_model.clazz, filter_model.params)
                
                filter_wrapper.fit(train_hash, train_f)
                
                if not filter_wrapper.hashcode is None:
                    filter_model.item = Container.fly.get_item(filter_wrapper.hashcode)
                test_f_minus_1 = test_f
                train_hash, train_name, train_f = filter_wrapper.predict(train_hash, train_name, train_f)
                test_hash, test_name, test_f = filter_wrapper.predict(test_hash, test_name, test_f)
                
                train_input.items.append(Container.fly.get_item(train_hash))
                test_input.items.append(Container.fly.get_item(test_hash))
                
            for metric in self.pipeline.metrics:
                m_wrapper = Container.get_metric(metric.clazz)
                metric.value = m_wrapper.predict(test_f_minus_1, test_f)
                
        except Exception as ex:
            raise ex
