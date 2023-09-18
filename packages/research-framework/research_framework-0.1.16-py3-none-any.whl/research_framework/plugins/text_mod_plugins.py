from research_framework.container.container import Container
from research_framework.base.plugin.base_plugin import BaseFilterPlugin
from research_framework.lightweight.wrappers import PassThroughFilterWrapper

from tqdm import tqdm

import pandas as pd


@Container.bind(PassThroughFilterWrapper)
class FilterRowsByNwords(BaseFilterPlugin):
    def __init__(self, df_headers=["id", "text", "label"], upper_cut=100, lower_cut=10):
        self.evr = None
        self.upper_cut=upper_cut
        self.lower_cut=lower_cut
        self.df_headers=df_headers
        
    def fit(self, *args, **kwargs):
        return self
    
    def transform(self, x):
        return self.predict(x)
    
    def predict(self, x):
        if type(x) == pd.DataFrame:
            aux = {}
            x.reset_index()
            pbar = tqdm(x.itertuples(index=False))
            pbar.set_description(f"FilterRowsByNwords - {self.get_params(deep=False)}")
            for sentence in pbar:
                try:
                    if len(str(sentence.text)) > self.lower_cut\
                    and (len(str(sentence.text)) < self.upper_cut or self.upper_cut < 0):
                        for k,v in sentence._asdict().items():
                            inner = aux.get(k, [])
                            inner.append(v)
                            aux[k] = inner
                except Exception as ex:
                    print(sentence.text)
                    raise ex

            return pd.DataFrame(aux)
        elif type(x) == list:
            aux = []
            pbar = tqdm(x)
            pbar.set_description(f"FilterRowsByNwords - {self.get_params(deep=False)}")
            
            for sentence in pbar:
                if len(str(sentence)) > self.lower_cut\
                    and (len(str(sentence)) < self.upper_cut or self.upper_cut < 0):
                        aux.append(sentence)
                        
            return aux
        else:
            raise TypeError("Input should be a list or pd.DataFrame")