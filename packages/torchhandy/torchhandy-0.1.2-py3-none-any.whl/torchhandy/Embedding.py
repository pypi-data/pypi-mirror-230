import torch
import torch.nn as nn
from copy import deepcopy

class SinPositionalEmbedding(nn.Module):
    def __init__(self, embedding_pos, embedding_dim):
        super().__init__()
        if embedding_dim % 2 != 0:
            raise ValueError("given dim should be even!")
        self.pos = embedding_pos
        self.dim = embedding_dim
        self.embedding = nn.Embedding(embedding_pos, embedding_dim)
        self.init_parameters()
    
    def init_parameters(self):
        pos = torch.arange(self.pos).reshape(-1, 1).repeat(1, self.dim)
        div = 2 * torch.arange(self.dim // 2).reshape(1, -1) / self.dim
        
        div_pos = torch.zeros((self.dim // 2, 2))
        sin_pos = deepcopy(div_pos)
        sin_pos[:, 0] = div 
        
        sin_use = torch.zeros_like(sin_pos)
        sin_use[:, 0] = 1
        
        cos_pos = deepcopy(div_pos)
        cos_pos[:, 1] = div
        
        sin_pos = sin_pos.reshape(-1, 1).repeat(1, self.pos).T
        cos_pos = cos_pos.reshape(-1, 1).repeat(1, self.pos).T
        sin_use = sin_use.reshape(-1, 1).repeat(1, self.pos).T

        sin_embedding = torch.sin(pos / (10000 ** sin_pos))
        cos_embedding = torch.cos(pos / (10000 ** cos_pos))
        self.embedding.weight.data = torch.where(sin_use > 0, sin_embedding, cos_embedding).detach()
        
    def forward(self, x):
        return self.embedding(x)