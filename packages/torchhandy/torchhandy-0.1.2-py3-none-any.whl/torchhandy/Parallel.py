import torch
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data import DataLoader, DistributedSampler
import os

class Parallel_Trainer(object):
    def __init__(self, synch, config):
        self.synch = synch
        if synch:
            local_rank = int(os.environ['LOCAL_RANK'])
            torch.cuda.set_device(local_rank)
            self.device = torch.device("cuda", local_rank)
            self.local_rank = local_rank
            torch.distributed.init_process_group("nccl", world_size = config.n_gpus, 
                                                rank = local_rank, init_method = 'env://')
        else:
            self.device = config.device
    
    def get_device(self):
        '''
            Get your current process's corresponding device, which is useful 
            for both single and multiple GPUs training.
        '''
        return self.device

    def model_parallel(self, model):
        '''
            Set the model to train mode, put it on the corresponding device and 
            initialize it to DDP if synch is set to True.
        '''
        model = model.to(self.device)
        model.train()
        if self.synch:
            model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model)   
            model = DistributedDataParallel(model.cuda(self.local_rank), device_ids=[self.local_rank],
                                            find_unused_parameters=True)
            return model
        else:
            return model
    
    def dataset_parallel(self, dataset):
        '''
            Get a distributed dataset sampler for DDP.
        '''
        if self.synch:
            train_sampler = DistributedSampler(dataset)
            return train_sampler
        else:
            return None
    
    def get_loader(self, dataset, epoch, bsz, num_workers, train_sampler = None):
        '''
            Get dataloader for both DDP or non-DDP. 
        '''
        if self.synch:
            train_sampler.set_epoch(epoch)
            dataloader = DataLoader(dataset, bsz, pin_memory=True,
                                num_workers= num_workers, sampler=train_sampler)
            return dataloader
        else:
            dataloader = DataLoader(dataset, bsz, num_workers = num_workers, shuffle = True,
                                    drop_last = False)
        return dataloader
    
    def save_model(self, ckpt, model, path):
        ''''
            Put the model's state_dict to ckpt and save the ckpt at path.
            If you'd like to store other information, you can put them into 
            ckpt outside this function. Only process running on the first GPU
            needs to actually save the model.
        '''
        if self.synch:
            if self.local_rank == 0:
                ckpt['state_dict'] = model.module.state_dict()
                torch.save(ckpt, path)
        
        else:
            ckpt['state_dict'] = model.state_dict()
            torch.save(ckpt, path)
        
    def write_log(self, log_file, content):
        '''
            Similar to saving checkpoints, write content to log_file. Only
            process running on the first GPU really does the work this function.
        '''
        if self.synch:
            if self.local_rank == 0:
                log_file.write(content + '\n')
                log_file.flush()
            
        else:
            log_file.write(content + '\n')
            log_file.flush()
    
    def call_func(self, func, *args, **kwargs):
        '''
            This is a general function caller that assures only the process running 
            on the first GPU actually calls the func.
        '''
        if self.synch:
            if self.local_rank == 0:
                func(*args, **kwargs)
        
        else:
            func(*args, **kwargs)
        
    def get_model(self, model):
        '''
            Returns the actual model. In single GPU training, it's model; in DDP,
            it's model.module.
        '''
        if self.synch:
            return model.module

        else:
            return model