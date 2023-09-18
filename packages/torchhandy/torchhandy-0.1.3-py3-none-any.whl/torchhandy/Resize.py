import torch
import torch.nn as nn

class UpSample(nn.Module):
    def __init__(self, channels, in_size, out_size, 
                 upsample_type = 'conv_trans', upsample_mode = 'nearest'):
        super().__init__()
        if upsample_type == 'conv_trans' and out_size == 2 * in_size:
            self.upsample = nn.ConvTranspose2d(channels, 
                                                channels,
                                                kernel_size = (3, 3),
                                                stride = 2,
                                                padding = 1,
                                                output_padding = 1)
        else:
            self.upsample = nn.Upsample((out_size, out_size), mode = upsample_mode)
        
    def forward(self, x):
        return self.upsample(x)
    
class DownSample(nn.Module):
    def __init__(self, channels, in_size, out_size, 
                 downsample_type = 'conv', downsample_mode = 'avg'):
        super().__init__()
        if downsample_type == 'conv' and in_size == 2 * out_size:
            self.downsample = nn.Conv2d(channels, 
                                    channels,
                                    kernel_size = (3, 3),
                                    stride = 2,
                                    padding = 1)
        else:
            if downsample_mode == 'avg':
                self.downsample = nn.AdaptiveAvgPool2d((out_size, out_size))
            else:
                self.downsample = nn.AdaptiveMaxPool2d((out_size, out_size))
        
    def forward(self, x):
        return self.downsample(x)