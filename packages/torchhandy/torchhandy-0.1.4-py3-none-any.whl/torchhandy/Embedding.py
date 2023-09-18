import torch
import torch.nn as nn
from .FC import FC
import math
from copy import deepcopy

class SinPositionalEmbedding(nn.Module):
    def __init__(self, embedding_dim, train = True):
        super().__init__()
        self.dim = embedding_dim
        if train:
            self.mlp = nn.Sequential(
                FC(self.dim, self.dim, dropout = 0, activation = 'silu'),
                nn.Linear(self.dim, self.dim)
            )    
        else:
            self.mlp = nn.Identity()
    
    def forward(self, x):
        x = x.reshape(-1, 1)
        dtype, device = x.dtype, x.device
        half_dim = self.dim // 2
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device = device, dtype = dtype) * -emb)
        emb = x.unsqueeze(1) * emb.unsqueeze(0)
        emb = torch.cat((emb.sin(), emb.cos()), dim = -1).type(dtype)
        return self.mlp(emb)