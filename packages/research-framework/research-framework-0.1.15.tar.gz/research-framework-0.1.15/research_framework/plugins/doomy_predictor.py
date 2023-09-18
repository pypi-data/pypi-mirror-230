from research_framework.base.plugin.base_plugin import BaseFilterPlugin
from research_framework.container.container import Container
from research_framework.dataset.standard_dataset import StandardDataset
from research_framework.neural_models.doomy_model import DoomyModel
from research_framework.lightweight.wrappers import FitPredictFilterWrapper

from tqdm import tqdm
from torch.optim import Adam
from torch.nn import BCELoss
from torch.utils.data import DataLoader

import scipy
import torch
import traceback
import numpy as np

@Container.bind(FitPredictFilterWrapper)
class DoomyPredictor(BaseFilterPlugin):
    def __init__(self, n_epoch=1, batch_size=5, emb_d=128, hidden_d=10, out_d=1):
        super().__init__()
        self.device = torch.device('cuda:{}'.format(0) if torch.cuda.is_available() else 'cpu')
        self.hidden_d = hidden_d
        self.n_epoch = n_epoch
        self.batch_size = batch_size
        self.out_d = out_d
        self.emb_d = emb_d
        self.model = DoomyModel(emb_d, hidden_d, out_d)
        self.optimizer = Adam(self.model.parameters(), lr=0.0001)
        self.loss_f = BCELoss()
        self.model = self.model.to(self.device)
        
    def set_params(self, **params):
        aux = super().set_params(**params)
        self.model = DoomyModel(self.emb_d, self.hidden_d, self.out_d)
        self.model = self.model.to(self.device)
        return aux

    def fit(self, x, y=None):
        losses = []
        for epoch in range(self.n_epoch):
            self.model.train()
            try:
                if y is not None:
                    train_dataloader = DataLoader(list(zip(x,y)), batch_size=self.batch_size, shuffle=True)
                else:
                    train_dataloader = DataLoader(x, batch_size=self.batch_size, shuffle=True)
                    
                pbar = tqdm(train_dataloader)
                pbar.set_description(f"DoomyPredictor epoch {epoch} - {self.get_params(deep=False)}")
                
                for idx, batch in enumerate(pbar):
                    self.optimizer.zero_grad()
                    
                    if type(x) == np.ndarray or type(x) == list:
                        vectors, y_ = batch
                    else:
                        df, vectors = batch
                        y_ = df['label']
                        
                    y_ = y_.to(self.device)
                    
                    
                    if scipy.sparse.issparse(vectors):
                        vectors = vectors.todense()

                    vectors = vectors.type(torch.float32)
                    vectors = vectors.to(self.device)
                    
                    y_pred = self.model(vectors)
                    y_pred = torch.reshape(y_pred, (-1,))
                
                    y_ = y_.type(torch.float32)
                
                    loss = self.loss_f(y_pred, y_)
                    loss.backward()
                    losses.append(loss.item())
                    self.optimizer.step()

            except Exception as ex:
                print(ex)
                traceback.print_exc()

            print(f'Average loss > {np.mean(losses)}')
        return self
                    
    def predict(self, x):
        self.model.eval()
        results = []
        with torch.no_grad():
            try:
                print(type(x))
                test_dataloader = DataLoader(x, batch_size=self.batch_size, shuffle=False)
                pbar = tqdm(test_dataloader)
                pbar.set_description(f"DoomyPredictor[Eval] - {self.get_params(deep=False)}")
                for batch in pbar:
                    if type(x) == np.ndarray or type(x) == list:
                        vectors = batch
                    else:
                        _, vectors = batch
                        
                    vectors = vectors.type(torch.float32)
                    vectors = vectors.to(self.device)
                        
                    y_pred = self.model(vectors)
                    y_pred = torch.reshape(y_pred, (-1,))
                    y_pred = (y_pred > 0.5).float()
                    results.append(y_pred)

                results = torch.concat(results).tolist()

            except Exception as ex:
                print(ex)
                traceback.print_exc()
        return results