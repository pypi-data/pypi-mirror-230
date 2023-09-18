import torch.nn as nn

class DoomyModel(nn.Module):
    def __init__(self, emb_d, hidden_d=10, out_d=1):
        super().__init__()
        self.layer1 = nn.Linear(emb_d, hidden_d)
        self.layer2 = nn.Linear(hidden_d, out_d)
        self.sigmoid = nn.Sigmoid()


    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        return self.sigmoid(x)
