import torch
import torch.nn as nn
from torchhandy.Parallel import Parallel_Trainer
import numpy as np
import random
import time
from torchhandy.utils import clear_cuda

class Trainer(object):
    def __init__(self, model, trainset, valset, trainconfig, args, loss_dict):
        self.trainset = trainset
        self.valset = valset
        self.trainer = Parallel_Trainer(args.synch, trainconfig)
        self.seed = trainconfig.seed
        self.resume = args.resume
        self.log_file = self.open_log(trainconfig)
        
        self.resume_path = trainconfig.resume_path
        self.cur_path = trainconfig.cur_path
        self.best_path = trainconfig.best_path
        self.model_name = trainconfig.model_name
        
        self.model = self.trainer.model_parallel(model)
        self.start_epoch = 0
        self.lr = trainconfig.lr
        self.weight_decay = trainconfig.weight_decay
        self.T_max = trainconfig.T_max
        self.eta_min = trainconfig.eta_min
        
        self.epochs = trainconfig.epochs
        self.train_bsz = trainconfig.train_bsz
        self.test_bsz = trainconfig.test_bsz
        self.num_workers = trainconfig.num_workers
        self.accumulation = trainconfig.accumulation
        self.loss_dict = loss_dict
        self.best_val = 1e10
    
        self.set_seed(self.seed)
        
        self.optimizer = torch.optim.AdamW(filter(lambda p : p.requires_grad, self.model.parameters()),
                                    lr = self.lr, weight_decay = self.weight_decay)
        
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, 
                                                                    T_max = self.T_max, 
                                                                    eta_min = self.eta_min)
        if self.resume:
            self.resume_model()
        
    def open_log(self, trainconfig):
        if self.resume:
            log_file = open(trainconfig.log_path, 'a')
        else:
            log_file = open(trainconfig.log_path, 'w+')
        return log_file
    
    def resume_model(self):
        ckpt = torch.load(self.resume_path, map_location = 'cpu')
        self.model.load_state_dict(ckpt['state_dict'])
        self.start_epoch = ckpt['epoch'] + 1
        self.lr = ckpt['lr']
    
    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True   
            
    def forward_one_epoch(self, epoch, dataset, type = 'train'):
        if type == 'train':
            self.model.train()
        else:
            self.model.eval()
            
        st_time = time.time()
        self.trainer.call_func(print, f'start {type} model {self.model_name} epoch = {epoch}')
    
        sampler = self.trainer.dataset_parallel(dataset)
        dataloader = self.trainer.get_loader(dataset, epoch, self.train_bsz,
                                            self.num_workers, sampler)
        for k in self.loss_dict:
            self.loss_dict[k] = 0
            
        batches = 0
        
        for data in dataloader:
            batches += 1
            if type == 'train':
                output = self.model(data, self.trainer.get_device())
                losses = self.trainer.get_model(self.model).calc_loss(output, data, self.trainer.get_device())
            else:
                with torch.no_grad():
                    output = self.model(data, self.trainer.get_device())
                    losses = self.trainer.get_model(self.model).calc_loss(output, data, self.trainer.get_device())
            
            for id, k in enumerate(self.loss_dict):
                self.loss_dict[k] += losses[id].item()
                
            if type == 'train':
                batch_loss = losses[-1] / self.accumulation
                batch_loss.backward()
                
                if batches % self.accumulation == 0:
                    self.optimizer.step()
                    self.optimizer.zero_grad()
        
        if type == 'train':
            self.optimizer.step()
            self.optimizer.zero_grad()
            self.scheduler.step()
        
        content = f'{epoch} {type}:\n'
        for k in self.loss_dict:
            content += f'{k} = {self.loss_dict[k] / batches}\n'
        
        self.trainer.write_log(self.log_file, content)
        ckpt = {
            'lr' : self.lr,
            'epoch' : epoch,
            'loss' : self.loss_dict['total_loss'] / batches,
        }
        
        if type == 'train':
            self.trainer.save_model(ckpt, self.model, self.cur_path)
        else:
            if ckpt['loss'] < self.best_val:
                self.best_val = ckpt['loss']
                self.trainer.save_model(ckpt, self.model, self.best_path)
        ed_time = time.time()
        dur = ed_time - st_time
        self.trainer.call_func(print, f'this epoch cost {dur} seconds, which is {dur / 60} minutes or {dur / 3600} hours')
        self.trainer.call_func(self.trainer.get_model(self.model).generate_cases, dataset, 1, 
                            self.trainer.get_device(), f'{self.model_name}_{type}_{epoch}')
        
    def train_model(self):
        for epoch in range(self.start_epoch, self.start_epoch + self.epochs):
            clear_cuda()
            self.forward_one_epoch(epoch, self.trainset, type = 'train')
            self.forward_one_epoch(epoch, self.valset, type = 'valid')
    
    def eval_model(self, dataset):
        if dataset is not None:
            self.forward_one_epoch(0, dataset, type = 'test')
        else:
            self.forward_one_epoch(0, self.valset, type = 'test')
    
        