from research_framework.container.container import Container
from research_framework.base.plugin.base_plugin import BaseFilterPlugin
import pandas as pd

from research_framework.lightweight.wrappers import InputFiterWrapper

@Container.bind(InputFiterWrapper)
class SaaSPlugin(BaseFilterPlugin):
    def __init__(self, drive_ref=""):
        self.drive_ref = drive_ref

    def fit(self, *args, **kwargs):
        return self

    def predict(self, _):
        obj = Container.storage.download_file(self.drive_ref)
        return obj

    
@Container.bind(InputFiterWrapper)
class CSVPlugin(BaseFilterPlugin):
    def __init__(self, filepath_or_buffer="", sep=',', index_col=False):
        self.filepath_or_buffer = filepath_or_buffer
        self.sep = sep
        self.index_col = index_col

    def fit(self, *args, **kwargs):
        return self

    def predict(self, _):
        obj = pd.read_csv(filepath_or_buffer=self.filepath_or_buffer, sep=self.sep, index_col=self.index_col)
        return obj

        

