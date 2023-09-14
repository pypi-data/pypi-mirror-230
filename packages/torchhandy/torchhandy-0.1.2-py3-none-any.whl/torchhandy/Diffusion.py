import torch
import torch.nn as nn
import numpy as np
from .utils import exists
from copy import deepcopy

class Diffusion(object):
    def __init__(self, config):
        self.steps = config.steps
        
        try:
            self.alpha_mul = torch.tensor(np.load(config.alpha_mul_path))
            assert(len(self.alpha_mul) == self.steps)
            
        except Exception as e:
            if config.sample_strategy == 'linear':
                self.betas = np.linspace(config.begin_beta, config.end_beta, config.steps)
                self.betas = torch.tensor(self.betas)
                self.alphas = 1 - self.betas
                self.alpha_mul = torch.cumprod(self.alphas, dim = 0)
            elif config.sample_strategy == 'cos':
                t = torch.arange(self.steps + 1)
                f = torch.cos(((t / self.steps + config.bias) / (1 + config.bias) * torch.pi / 2)) ** 2
                self.alpha_mul = f[1:] / f[0].item()
        
        self.alphas = deepcopy(self.alpha_mul)
        self.alphas[1:] = self.alpha_mul[1:] / self.alpha_mul[:-1]
        self.betas = 1 - self.alphas
        if config.sample_strategy == 'cos':
            self.betas[self.betas > 0.999] = 0.999
        self.alphas = 1 - self.betas
        np.save(config.alpha_mul_path, self.alpha_mul.numpy())
        
    def add_noise(self, x, device, given_tim = None):
        self = self.to(device)
        x = x.to(device)
        
        bsz = x.shape[0]
        ori_shape = x.shape
        x = x.reshape(bsz, -1)

        tim = torch.randint(0, self.steps, (bsz, )).to(device)
        if exists(given_tim):
            tim = torch.tensor(given_tim).to(device)
        alpha_muls = torch.gather(self.alpha_mul, dim = 0, index = tim).to(device).unsqueeze(1)
        noise = torch.randn_like(x).to(device)
        noised_x = torch.sqrt(alpha_muls) * x + torch.sqrt(1 - alpha_muls) * noise
        
        noised_x = noised_x.reshape(*ori_shape)
        noise = noise.reshape(*ori_shape)
        return noised_x.detach().to(torch.float), noise.detach().to(torch.float), tim.detach()

    def to(self, device):
        self.alphas = self.alphas.to(device)
        self.betas = self.betas.to(device)
        self.alpha_mul = self.alpha_mul.to(device)
        return self

    def denoise(self, x, step, pred_noise, device):
        x = x.to(device)
        pred_noise = pred_noise.to(device)
        self = self.to(device)
        
        x_now = (x - self.betas[step] * pred_noise / (torch.sqrt(1 - self.alpha_mul[step]))) * torch.sqrt(1 / self.alphas[step]) 
        if step > 0:
            z = torch.randn_like(x).to(device)
            x_now += torch.sqrt((1 - self.alpha_mul[step - 1]) / (1 - self.alpha_mul[step]) * self.betas[step]) * z
        return pred_noise, x_now
        