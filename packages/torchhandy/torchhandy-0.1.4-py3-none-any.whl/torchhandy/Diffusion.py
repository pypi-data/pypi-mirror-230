'''
    Code borrowed from https://github.com/lucidrains/DALLE2-pytorch/tree/main/dalle2_pytorch
'''

import torch
import torch.nn as nn
import numpy as np
from .utils import exists
from copy import deepcopy

def cosine_beta_schedule(timesteps, s = 0.008):
    """
    cosine schedule
    as proposed in https://openreview.net/forum?id=-NEXDKk8gZ
    """
    steps = timesteps + 1
    x = torch.linspace(0, timesteps, steps, dtype = torch.float64)
    alphas_cumprod = torch.cos(((x / timesteps) + s) / (1 + s) * torch.pi * 0.5) ** 2
    alphas_cumprod = alphas_cumprod / alphas_cumprod[0].item()
    betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
    return torch.clip(betas, 0, 0.999)


def linear_beta_schedule(timesteps):
    scale = 1000 / timesteps
    beta_start = scale * 0.0001
    beta_end = scale * 0.02
    return torch.linspace(beta_start, beta_end, timesteps, dtype = torch.float64)


def quadratic_beta_schedule(timesteps):
    scale = 1000 / timesteps
    beta_start = scale * 0.0001
    beta_end = scale * 0.02
    return torch.linspace(beta_start**0.5, beta_end**0.5, timesteps, dtype = torch.float64) ** 2


def sigmoid_beta_schedule(timesteps):
    scale = 1000 / timesteps
    beta_start = scale * 0.0001
    beta_end = scale * 0.02
    betas = torch.linspace(-6, 6, timesteps, dtype = torch.float64)
    return torch.sigmoid(betas) * (beta_end - beta_start) + beta_start

class Diffusion(object):
    def __init__(self, config):
        self.steps = config.steps
        try:
            self.betas = torch.tensor(np.load(config.betas))
            assert(len(self.betas) == self.steps)
            
        except Exception as e:
            if config.sample_strategy == 'linear':
                self.betas = linear_beta_schedule(self.steps)
            elif config.sample_strategy == 'cos':
                self.betas = cosine_beta_schedule(self.steps)
            elif config.sample_strategy == 'quadratic':
                self.betas = quadratic_beta_schedule(self.steps)
            elif config.sample_strategy == 'sigmoid':
                self.betas = sigmoid_beta_schedule(self.steps)
            else:
                raise NotImplementedError
        
        self.alphas = 1.0 - self.betas
        self.alpha_mul = torch.cumprod(self.alphas, dim = 0)
        np.save(config.beta_path, self.betas.numpy())
        
    def add_noise(self, x, device, given_tim = None, given_prob = None):
        '''
            given_prob can be specified to sample time steps at a given probability.
        '''
        self = self.to(device).to(torch.float64)
        x = x.to(device).to(torch.float64)
        
        bsz = x.shape[0]
        ori_shape = x.shape
        x = x.reshape(bsz, -1)

        if not exists(given_prob):
            given_prob = torch.arange(self.steps)
        given_prob = torch.softmax(given_prob, dim = 0, dtype = torch.float64)
        
        tim = np.random.choice(self.steps, size = bsz, 
                               replace = True, p = given_prob)
        tim = torch.tensor(tim).to(device)
        if exists(given_tim):
            tim = torch.tensor(given_tim).to(device)
        alpha_muls = torch.gather(self.alpha_mul, dim = 0, index = tim).to(device).unsqueeze(1)
        noise = torch.randn_like(x, dtype = torch.float64, device = device)
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
        x = x.to(device).to(torch.float64)
        pred_noise = pred_noise.to(device).to(torch.float64)
        self = self.to(device).to(torch.float64)
        
        x_now = (x - self.betas[step] * pred_noise / (torch.sqrt(1 - self.alpha_mul[step]))) * torch.sqrt(1 / self.alphas[step]) 
        if step > 0:
            z = torch.randn_like(x, dtype = torch.float64, device = device)
            x_now += torch.sqrt((1 - self.alpha_mul[step - 1]) / (1 - self.alpha_mul[step]) * self.betas[step]) * z
        return x_now.to(torch.float)
        