from torch.optim.lr_scheduler import CosineAnnealingLR, StepLR, ConstantLR
from .utils import exists

class Scheduler(object):
    def __init__(self, optimizer, config):
        '''
            supported scheduler types: cos_lr, step_lr, const_lr
        '''
        if config.scheduler_type == 'cos_lr':
            self.scheduler = CosineAnnealingLR(optimizer, T_max = config.T_max, eta_min = config.eta_min)
        elif config.scheduler_type == 'step_lr':
            self.scheduler = StepLR(optimizer, step_size = config.step_size, gamma = config.gamma)
        elif config.scheduler_type == 'const_lr':
            self.scheduler = ConstantLR(optimizer, factor = config.factor, total_iters = config.total_iters)
        else:
            self.scheduler = None
        
    def step(self):
        if exists(self.scheduler):
            self.scheduler.step()