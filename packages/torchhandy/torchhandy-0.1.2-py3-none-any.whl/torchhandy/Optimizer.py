from torch.optim import SGD, Adam, AdamW, Adagrad
from .utils import exists

class Optimizer(object):
    def __init__(self, parameters, lr, config):
        '''
            supported optimizer types: sgd, Adam, AdamW
        '''
        if config.optimizer_type == 'sgd':
            self.optimizer = SGD(parameters, 
                                 lr = lr,
                                 momentum = config.momentum,
                                 weight_decay = config.weight_decay)
        elif config.optimizer_type == 'Adam':
            self.optimizer = Adam(parameters, 
                                  lr = lr,
                                  betas = config.adam_betas,
                                  weight_decay = config.weight_decay)
        elif config.optimizer_type == 'AdamW':
            self.optimizer = AdamW(parameters,
                                   lr = lr,
                                   betas = config.adamw_betas,
                                   weight_decay = config.weight_decay)
        else:
            raise NotImplementedError
        
    def step(self):
        self.optimizer.step()
            
    def zero_grad(self):
        self.optimizer.zero_grad()
        
    def state_dict(self):
        return self.optimizer.state_dict()
    
    def load_state_dict(self, state_dict):
        self.optimizer.load_state_dict(state_dict)