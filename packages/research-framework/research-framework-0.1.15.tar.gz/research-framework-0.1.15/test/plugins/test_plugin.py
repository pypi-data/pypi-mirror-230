from research_framework.container.container import Container
from research_framework.base.plugin.base_plugin import BasePlugin
from research_framework.lightweight.wrappers import PassThroughFilterWrapper, FitPredictFilterWrapper


@Container.bind(PassThroughFilterWrapper)
class TestPassThroughFilterWrapper(BasePlugin):

    def fit(self, *args, **kwargs): ...

    def predict(self, _):
        return "Data generated"



@Container.bind(FitPredictFilterWrapper)
class TestFitPredictFilterWrapper(BasePlugin):

    def fit(self, *args, **kwargs):
        return "Model Trained"

    def predict(self, _):
        return "Data generated"
