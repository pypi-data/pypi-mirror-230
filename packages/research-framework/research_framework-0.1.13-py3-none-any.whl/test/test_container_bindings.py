import pytest
from typing import Any, Tuple
from research_framework.lightweight.lightweight import FlyWeight

from test.plugins.test_plugin import TestPassThroughFilterWrapper, TestFitPredictFilterWrapper
from research_framework.pipeline.wrappers import FitPredictFilterWrapper, PassThroughFilterWrapper
from research_framework.container.container import Container



def test_get_bindings():
    Container.fly = FlyWeight()
    
    wrapper1 = Container.get_filter(TestPassThroughFilterWrapper.__name__, {})
    
    assert type(wrapper1) == PassThroughFilterWrapper
    assert type(wrapper1.filter) == TestPassThroughFilterWrapper
    
    wrapper2 = Container.get_filter(TestFitPredictFilterWrapper.__name__, {})
    
    assert type(wrapper2) == FitPredictFilterWrapper
    assert type(wrapper2.filter) == TestFitPredictFilterWrapper