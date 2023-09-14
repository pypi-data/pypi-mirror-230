import torch
import torch.nn as nn
from copy import deepcopy

class EMA(object):
    def __init__(self, alpha = 0.99, step_range = 1):
        self.alpha = alpha
        self.step_range = step_range
        self.total_steps = 0
        self.shadow = {}
        self.ori = {}
    
    def register(self, model):
        for name, para in model.named_parameters():
            self.shadow[name] = para.cpu().data.clone()
        
    def resume(self, ckpt):
        self.total_steps = ckpt['ema_total_steps']
        for k in ckpt['ema_shadow']:
            self.shadow[k] = ckpt['ema_shadow'][k].cpu()
        
    def update(self, model):
        self.total_steps += 1
        if self.total_steps % self.step_range != 0:
            return
        for name, para in model.named_parameters():
            if name not in self.shadow:
                raise ValueError("unexpected model parameter!")
            self.shadow[name] = self.alpha * self.shadow[name] + (1 - self.alpha) * para.cpu().data.clone()
        return model
    
    def load_model(self, model):
        self.ori = {}
        for name, para in model.named_parameters():
            if name not in self.shadow:
                raise ValueError("unexpected model parameter!")
            self.ori[name] = para.cpu().data.clone()
            para.data = self.shadow[name].to(para.data.device)
        return model

    def restore_model(self, model):
        for name, para in model.named_parameters():
            if name not in self.shadow or name not in self.ori:
                raise ValueError("unexpected model parameter or not stored!")
            para.data = self.ori[name].to(para.data.device)
        return model
    
    def store_ema(self, ckpt):
        ckpt['ema_total_steps'] = self.total_steps
        ckpt['ema_shadow'] = self.shadow
        return ckpt