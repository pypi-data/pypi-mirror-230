from typing import List
from research_framework.base.plugin.base_plugin import BasePlugin

from research_framework.container.container import Container
from sklearn.pipeline import Pipeline
from research_framework.pipeline.model.pipeline_model import GridSearchFilterModel
from research_framework.lightweight.wrappers import DoomyFilterWrapper 
from sklearn.model_selection import GridSearchCV, ShuffleSplit

import pprint as pp

@Container.bind(DoomyFilterWrapper)
class CrossValGridSearch(BasePlugin):
    def __init__(self, n_splits=3, test_size=0.3, random_state=43, scorer="f1", refit=True, filters=[]):
        self.n_splits = n_splits
        self.test_size = test_size
        self.random_state = random_state
        self.filters = filters
        self.scorer = scorer
        self.refit = refit


    def fit(self, x):
        if callable(x) and x.__name__ == "<lambda>":
            x = x()

        filters:List[GridSearchFilterModel] = self.filters
        print("\n--------------------[CrossValGridSearch]-----------------------\n")
        pp.pprint(filters)
        print("\n-------------------------------------------\n")
        search_space = {}
        for f in filters:
            for p_nam, p_val in f.params.items():
                search_space[f"{f.clazz}__{p_nam}"] = p_val
        
        pp.pprint(search_space)
        print("\n-------------------------------------------\n")
        
        pipeline = Pipeline(
            steps=[(f.clazz, Container.get_clazz(f.clazz)())for f in filters]
        )
        
        pp.pprint(pipeline)
        print("\n-------------------------------------------\n")
        cv = ShuffleSplit(
            n_splits=self.n_splits, 
            test_size=self.test_size, 
            random_state=self.random_state
        )
        self.gs = GridSearchCV(pipeline, search_space, scoring=self.scorer, refit=self.refit, cv=cv)
        self.gs.fit(x.text.values.tolist(), x.label.values.tolist())

        print("\n-------------------------------------------\n")
        print("- Results: ")
        print(f'\t * Best estimator > {self.gs.best_estimator_}')
        print(f'\t * Best params    > {self.gs.best_params_}')
        print(f'\t * Best score     > {self.gs.best_score_}')
    
    def predict(self, x): 
        if callable(x) and x.__name__ == "<lambda>":
            x = x()
        return self.gs.predict(x.text.values.tolist())
        
         