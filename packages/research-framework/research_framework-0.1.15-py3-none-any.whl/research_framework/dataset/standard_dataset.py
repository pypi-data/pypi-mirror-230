
from torch.utils.data import Dataset
import pandas as pd
import scipy
from typing import Any

class StandardDataset(Dataset):
    def __init__(self, df:pd.DataFrame, vectors):
        self.df = df
        self.vectors = vectors


    def __len__(self):
        return len(self.df.index)
    
    def __getitem__(self, index) -> Any:
        if scipy.sparse.issparse(self.vectors):
            return self.df.iloc[index].to_dict(), self.vectors.getrow(index)
        else:
            return self.df.iloc[index].to_dict(), self.vectors[index]
            