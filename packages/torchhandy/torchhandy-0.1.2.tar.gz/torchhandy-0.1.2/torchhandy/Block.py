import torch.nn as nn
import torch
from .utils import get_mask
from .FC import FC

class MultiHeadAttention(nn.Module):
    def __init__(self, input_dim, num_heads = 4):
        nn.Module.__init__(self)
        self.input_dim = input_dim
        self.heads = num_heads
        self.WQ = nn.Linear(input_dim, num_heads * input_dim)
        self.WK = nn.Linear(input_dim, num_heads * input_dim)
        self.WV = nn.Linear(input_dim, num_heads * input_dim)
        self.W = nn.Linear(input_dim * num_heads, input_dim)
        self.sfm = nn.Softmax(dim = -1)
        
    def split_heads(self, Q, K, V, batch_size):
        rQ = Q.view(batch_size, -1, self.heads, self.input_dim).transpose(1, 2)
        rK = K.view(batch_size, -1, self.heads, self.input_dim).transpose(1, 2)
        rV = V.view(batch_size, -1, self.heads, self.input_dim).transpose(1, 2)
        return rQ, rK, rV
    
    def forward(self, Q, K, V, device, mask = None):
        '''
            Q, K, V: [bs, seq_len, dim] -> [bs, seq_len, dim*heads]
            -> [bs, seq_len, heads, dim] -> [bs, heads, seq_len, dim]
            matmul-> [bs, heads, seq_len, seq_len]
        '''
        sQ = self.WQ(Q)
        sK = self.WK(K)
        sV = self.WV(V)
        batch_size = Q.shape[0]

        rQ, rK, rV = self.split_heads(sQ, sK, sV, batch_size)
        Si = torch.matmul(rQ, rK.transpose(2, 3))

        Si = Si / torch.sqrt(torch.tensor([self.input_dim]).to(device))  
        if mask != None:
            Si = Si + mask
            
        sim = self.sfm(Si).to(rV.dtype)
        oV = torch.matmul(sim, rV).transpose(1, 2).reshape(batch_size, -1, self.heads * self.input_dim)
        
        output = self.W(oV)
        return output


class MultiHeadSparseAttention(nn.Module):
    def __init__(self, input_dim, split_length, num_heads):
        nn.Module.__init__(self)
        self.input_dim = input_dim
        self.heads = num_heads
        self.split_length = split_length
        self.WQ = nn.Linear(input_dim, num_heads * input_dim)
        self.WK = nn.Linear(input_dim, num_heads * input_dim)
        self.WV = nn.Linear(input_dim, num_heads * input_dim)
        self.W = nn.Linear(input_dim * num_heads, input_dim)
        self.att = MultiHeadAttention(input_dim, num_heads)
        self.sfm = nn.Softmax(dim = -1)

    def split_heads(self, Q, K, V, batch_size):
        rQ = Q.view(batch_size, Q.shape[1] // self.split_length, self.split_length,
                    self.heads, self.input_dim).transpose(2, 3)
        rK = K.view(batch_size, K.shape[1] // self.split_length, self.split_length, 
                    self.heads, self.input_dim).transpose(2, 3)
        rV = V.view(batch_size, V.shape[1] // self.split_length, self.split_length, 
                    self.heads, self.input_dim).transpose(2, 3)
        return rQ, rK, rV
    
    def forward(self, Q, K, V, device):
        '''
            Q, K, V: [bs, seq_len, dim] -> [bs, seq_len, dim*heads]
            -> [bs, seq_len, heads, dim] -> [bs, heads, seq_len, dim]
            matmul-> [bs, heads, seq_len, seq_len]
        '''
        assert(Q.shape[1] % self.split_length == 0)
        assert(K.shape[1] % self.split_length == 0)
        assert(V.shape[1] % self.split_length == 0)
        sQ = self.WQ(Q)
        sK = self.WK(K)
        sV = self.WV(V)
        bsz = Q.shape[0]
        seq_len = Q.shape[1]

        rQ, rK, rV = self.split_heads(sQ, sK, sV, bsz) #[bsz, split_time, head, split_len, dim]
        Si = torch.matmul(rQ, rK.transpose(3, 4))

        s_mask = get_mask(Si.shape[3])
        Si = Si / torch.sqrt(torch.tensor([self.input_dim]).to(device))
        
        sim = self.sfm(Si + s_mask)  #[bsz, split_time, head, split_len, split_len]
        sim = sim.to(rV.dtype)
        oV = torch.matmul(sim, rV).reshape(bsz, -1, self.heads, 
                                        self.split_length, self.input_dim) 
        #[bsz, split_time, heads, split_len, dim]
        
        pooling = oV.mean(dim = -2).transpose(1, 2) #average-pooling, [bsz, heads, split_tim, dim]
        g_mask = g_mask = get_mask(pooling.shape[2]).to(device)
        g_Si = torch.matmul(pooling, pooling.transpose(2, 3)) / \
                            torch.sqrt(torch.tensor([self.input_dim]).to(device))
                            
        g_sim = self.sfm(g_Si + g_mask).to(pooling.dtype) #[bsz, heads, split_tim, split_tim]
        global_att = torch.matmul(g_sim, pooling).transpose(1, 2) #[bsz, split_tim, heads, dim]
        oV = oV + global_att.unsqueeze(3)
        output = self.W(oV) #[bsz, split_time, split_len, dim]
        output = output.reshape(bsz, -1, self.input_dim)
        return output
    
class DecBlock(nn.Module):
    def __init__(self, dropout, input_dim, num_heads, att_type = '', split_length = 16):
        nn.Module.__init__(self)
        if att_type == 'sparse':
            self.self_att = MultiHeadSparseAttention(input_dim, split_length, num_heads)
        else:
            self.self_att = MultiHeadAttention(input_dim, num_heads)
        self.dropout = nn.Dropout(dropout)
        self.ln2 = nn.LayerNorm(input_dim)
        self.fc = nn.Sequential(
            FC(input_dim, input_dim, dropout, activation = 'gelu'),
            nn.Linear(input_dim, input_dim),
        )
        self.ln3 = nn.LayerNorm(input_dim)

    def forward(self, dec_input, device, mask = None):
        self_att_out = self.self_att(dec_input, dec_input, dec_input, device, mask)
        ln_out2 = self.ln2(self_att_out + dec_input)
        output = self.ln3(self.fc(self.dropout(ln_out2)) + ln_out2)
        return output