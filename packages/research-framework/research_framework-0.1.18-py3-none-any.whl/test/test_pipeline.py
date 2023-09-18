from research_framework.base.plugin.base_plugin import BasePlugin
from research_framework.base.wrappers.filter_wrapper import BaseFilterWrapper
from research_framework.container.container import Container
from research_framework.dataset.standard_dataset import StandardDataset
from research_framework.lightweight.lightweight import FlyWeight
from research_framework.lightweight.model.item_model import ItemModel
from research_framework.pipeline.model.pipeline_model import PipelineModel, FilterModel, InputFilterModel, MetricModel
from research_framework.pipeline.pipeline import FitPredictPipeline

import pytest
import pandas as pd
import pprint

test_pipeline = PipelineModel(
    name='pipeline para tests',
    train_input= 
        InputFilterModel(
            clazz='CSVPlugin',
            name='texts_depression_2018.csv',
            params={
                "filepath_or_buffer":"test/data/texts_depression_2018.csv",
                "sep": ",",
                "index_col": 0,
            },
        )
    ,
    test_input =
        InputFilterModel(
            clazz='CSVPlugin',
            name='texts_depression_2022.csv',
            params={
                "filepath_or_buffer":"test/data/texts_depression_2022.csv",
                "sep": ",",
                "index_col": 0,
            }
        )
    ,
    filters= [
        FilterModel(
            clazz="FilterRowsByNwords",
            params={
                "upper_cut": 100,
                "lower_cut": 10,
                "df_headers": ["id", "text", "label"]
            }
        ),
        FilterModel(
            clazz="Tf",
            params={
                "lowercase":True
            }
        ),
        FilterModel(
            clazz="MaTruncatedSVD",
            params={
                "n_components":1024
            } 
        ),
        FilterModel(
            clazz="DoomyPredictor",
            params={
                "n_epoch": 3,
                "batch_size": 500,
                "emb_d": 1024
            }
        )
    ],
    metrics = [
        MetricModel(
            clazz="F1"
        )
    ]
)

@pytest.fixture
def simple_pipeline():
    pp = pprint.PrettyPrinter(indent=4)
    print("\n* Container content: ")
    pp.pprint(Container.BINDINGS)
    print("\n* Pipeline: ")
    pp.pprint(test_pipeline.model_dump())
    Container.fly = FlyWeight()
    pipeline = FitPredictPipeline(test_pipeline)
    pipeline.start()
    return pipeline


def aux_delete_pipeline_generated_items(pipeline):
    print("- Train data:")
    for item in test_pipeline.train_input.items:
        print(item)
        assert Container.fly.unset_item(item.hash_code)
        
    print("- Test data:")
    for item in test_pipeline.test_input.items:
        print(item)
        assert Container.fly.unset_item(item.hash_code)
    
    print("- Trained models:")
    for plugin_filter in pipeline.pipeline.filters:
        if not plugin_filter.item is None:
            print(plugin_filter.item)
            assert Container.fly.unset_item(plugin_filter.item.hash_code)

@pytest.fixture
def delete_pipeline_items(simple_pipeline, request):
    request.addfinalizer(lambda: aux_delete_pipeline_generated_items(simple_pipeline))
    return simple_pipeline

def test_stored_items_types_and_wrappers(delete_pipeline_items):
    pipeline = delete_pipeline_items
    for item in test_pipeline.train_input.items:
        assert type(item) == ItemModel
        obj = Container.fly.get_wrapped_data_from_item(item)
        assert issubclass(type(obj), BaseFilterWrapper)
        obj2 = Container.fly.get_data_from_item(item)
        assert type(obj2) == pd.DataFrame or type(obj2) == StandardDataset

    for item in test_pipeline.test_input.items:
        assert type(item) == ItemModel
        obj = Container.fly.get_wrapped_data_from_item(item)
        assert issubclass(type(obj), BaseFilterWrapper)
        obj2 = Container.fly.get_data_from_item(item)
        assert type(obj2) == pd.DataFrame or type(obj2) == StandardDataset

    for plugin_filter in pipeline.pipeline.filters:
        if not plugin_filter.item is None:
            item = plugin_filter.item
            assert type(item) == ItemModel
            obj = Container.fly.get_wrapped_data_from_item(item)
            assert issubclass(type(obj), BaseFilterWrapper)
            obj2 = Container.fly.get_data_from_item(item)
            assert issubclass(type(obj2), BasePlugin)
            
def test_metrics(delete_pipeline_items):
    pipeline = delete_pipeline_items
    for metric in pipeline.pipeline.metrics:
        print(f'- {metric.clazz} : {metric.value}')

    assert True