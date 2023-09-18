import torch.nn as nn
import torch
from .utils import select_activation, select_normalization, fea2cha, cha2fea

def select_resconnection(in_channels, out_channels):
    mapping = nn.Identity()
    if in_channels != out_channels:
        mapping = nn.Conv2d(in_channels, out_channels, 1, 1, 0)
    return mapping

'''
    This is a typical module in ResNet with 2 conv layers.
'''
class Res_Conv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, 
                 normalization = None, activation = 'relu', res_connection = True):
        nn.Module.__init__(self)
        self.conv1 = nn.Conv2d(in_channels= in_channels, out_channels= out_channels, 
                            kernel_size= kernel_size, padding= (kernel_size[0] - 1) // 2)
        self.conv2 = nn.Conv2d(in_channels = out_channels, out_channels = out_channels,
                               kernel_size= kernel_size, padding= (kernel_size[0] - 1) // 2)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.res_connection = res_connection
        
        self.norm1 = select_normalization(normalization)
        self.norm2 = select_normalization(normalization)
        self.act = select_activation(activation)
        if self.res_connection:
            self.conv3 = select_resconnection(self.in_channels, self.out_channels)
                
        
    def forward(self, x):
        output = self.conv1(x)
        output = self.norm1(output)
        output = self.act(output)
            
        output = self.conv2(output)
        output = self.norm2(output)
            
        if self.res_connection:
            output = output + self.conv3(x)
            
        return self.act(output)
    
'''
    This is a residual convolution layer with one conv.
'''
class SConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, 
                 normalization = None, activation = 'relu', res_connection = True):
        nn.Module.__init__(self)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.res_connection = res_connection
        
        self.conv1 = nn.Conv2d(in_channels= in_channels, out_channels= out_channels, 
                            kernel_size= kernel_size, padding= (kernel_size[0] - 1) // 2)
        if self.res_connection:
            self.conv2 = select_resconnection(self.in_channels, self.out_channels)
        
        self.norm = select_normalization(normalization)
        self.act = select_activation(activation)
                
        
    def forward(self, input):
        output = self.conv1(input)
        output = self.norm(output)
        if self.res_connection:
            output = output + self.conv2(input)
        return self.act(output)
    
'''
    This is a conv module with self-attention layers.
'''
class Att_Conv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, siz, num_heads, dropout,
                normalization = None, activation = 'relu', res_connection = True):
        nn.Module.__init__(self)
        
        self.conv1 = SConv(in_channels, out_channels, kernel_size, 
                           normalization, activation, res_connection)
        self.conv2 = SConv(out_channels, out_channels, kernel_size, 
                           normalization, activation, res_connection)
        self.norm = select_normalization(normalization)
        self.att = nn.MultiheadAttention(out_channels, num_heads, 
                                         dropout, batch_first = True)
        
        self.in_channels = in_channels
        self.out_channels = out_channels        
        self.res_connection = res_connection
        
        if self.res_connection:
            self.conv3 = select_resconnection(self.in_channels, self.out_channels)
        
        
    def forward(self, x):
        fea = self.conv1(x)
        a_fea = cha2fea(fea)
        att_out, _ = self.att(a_fea, a_fea, a_fea)
        fea = fea2cha(att_out)
        fea = self.norm(fea)
        if self.res_connection:
            fea = fea + self.conv3(x)
        return self.conv2(fea)