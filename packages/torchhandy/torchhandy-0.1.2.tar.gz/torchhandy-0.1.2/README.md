# TorchHandy

## Installation

```bash
    pip install torchhandy
```

## Introduction
This is a handy implementation of some useful pytorch modules and functions, which can be helpful for both students and researchers, especially in simplifying 
repeating coding procedure.

It's worth mentioning that most of the wrapped modules are written in a way the author is familiar with (currently), which means that some modules may be hard to use for some users, which the author should apologize in advance.

### Config
Some modules requires a "config", which is actually a python class that has the corresponding attributes. This README will continue to update the details about the attributes.  

The simplest way to use config is adding a python class called Config, and instantiate it into an object named "config", then pass this object as a argument to the module and everything will be fine. (Probably)

An example of how to write "config":

```python
    class Config(object):
        '''
            Put the attributes you'd like to specified here
        '''
        dropout = 0.1
    
    config = Config()
    module = Module(config) # Module is a module in torchhandy that requires a "config" as a argument. 
```

### Error Checking and Debugging
Please note that for the author's convenience almost no error checking is made and there're only few failure reports, which means that if you made some wrong configurations, you may come up with some really weird errors and have to read the f**king source code to solve them. Again, the author apologizes for this and this will be improved (sooner or later).

But there's not that much to worry about - the code written is so simple that you can easily understand what the author is doing. So do not hesitate to read or even modify the code for your covenience. The author sincerely believe that most users (if any but the author himself) has a better coding skill than the author.

## Parallel

PyTorch offers simple interfaces for parallel training, and one of the most popular one is distributed data parallel (DDP). However, it's still not easy for learners to use and a boring task for even experts (because they have to write the same frame over and over again). 

So the author comes up with this Parallel_Trainer. It's an extremely useful helper to simplify DDP training. The most amazing part of it is that it unifies the training procedure on one GPU or more than one GPUs. You can write the same training code and ignore the details about GPU settings, which will be handled by the Parallel_Trainer.

### Initialization
The Parallel_Trainer accepts two arguments - a boolean value called "synch" and a config. If "synch" is set to True, then multiple GPUs will be used, otherwise only a single GPU will be used. For your convenience, I recommend passing the argument as a commandline argument, which can be done as follows:

```python
    '''
        In this example, if you run your code with "... --synch ..." 
        (or "... -s ..."), "synch" will be set to True (otherwise False).
        Thus you can easily choose whether to use DDP when running your code.
    '''
    import argparse
    parser = argparse.ArgumentParser(description = 'yourdescription')
    parser.add_argument('--synch',
                        '-s',
                        action = 'store_true')
    args, unknown = parser.parse_known_args()
    synch = args.synch
```

For the "config", 2 attributes shoule be specified : n_gpus (which is useful in DDP training, indicating how many gpus you'd like to use) and device (which is useful in single device training, indicating the certain device you'd like to put your model and data on). The author suggest setting them both which will release your effort in changing from one training type to another.

Therefore, a typical initialization of a parallel trainer can be seen as follows:

```python
    from torchhandy.Parallel import Parallel_Trainer
    import argparse

    class Config(object):
        n_gpus = 2
        device = 'cuda'

    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description = 'yourdescription')
        parser.add_argument('--synch',
                            '-s',
                            action = 'store_true')
        args, unknown = parser.parse_known_args()
        synch = args.synch
        config = Config()
        trainer = Parallel_Trainer(synch, config)
```

### GPU settings and program starting

How to start DDP training? Suppose your main code's filename is "main.py" and your n_gpus = n, then you can start DDP training with the command:

```bash
    python3 -m torch.distributed.launch --nproc_per_node=n --master_port="29501" --use_env main.py --synch 
```

If you meet some weird bugs relating to communication port, you can change 29501 to other ports such as 29500, 29502, etc. If you do not want to use DDP, you can start your code like: 

```bash
    python3 main.py
```

And if you use the Parallel_Trainer properly, no change will be needed in your main code!

You may wonder which gpus will this trainer use? Typically it will use the first n_gpus GPU for training. So if cuda:0 (normally the first GPU) cannot be used, will this trainer be useless?

The answer is absolutely no! We recommend the users to specify the visible GPUs to the ones they can use. For example, if cuda:0 and cuda:2 is busy for some reasons, you should change your code's visible GPUs to all GPUs except cuda:0 and cuda:2. There are many ways to do so, two of the most useful ways are setting inside your code or in your command line. The first way is tricky and sometimes lead to weird bugs (not restricted to the parallel_trainer, I've met this bug everywhere so I'm strongly against this method.)

The second one is also simple and clear. You can specify CUDA_VISIBLE_DEVICES=.... before you run your code. Then your code can only see GPUs you specified, and reorder them to cuda:0, cuda:1, ...

For example, you can run command:

```bash
    CUDA_VISIBLE_DEVICES=2,4,6,8 python3 -m torch.distributed.launch --nproc_per_node=2 --master_port="29501" --use_env main.py --synch
```

(suppose you have a good server with many GPUs on it).

And if you run ```nvidia-smi```, you may find that cuda:2 and cuda:4 is busy, while in your code you should still call them cuda:0 and cuda:1!(which is important. If you use cuda:8 in your code, your code will fail to find the correct GPU in the example above because it has already reordered cuda:8 to cuda:3!)

Of course, it's still tiring to set the GPUs every time you start the training, so you can use:

```bash
    export CUDA_VISIBLE_DEVICES=...
```

And all the rode running under this terminal will only see GPUs you specified above, while code running under other terminals are not influenced.

However, in case web failure or other failure cases, we'd like our code to continue running even if we've quitted until we explicitly stop them or the code itself stops. The most common way to do so is using nohup:

```bash
    nohup python3 main.py
```

And all the outputs of the code will be redirected to a file called "nohup.out". However, this doesn't work when you start a DDP training. For DDP training, the simplest way is using "tmux", which can be viewed as a terminal. You can use tmux as follows:

```bash
    tmux new -s [session_name]
```

This command creates a new tmux session, which is similar to a terminal, and everything happening in this session will not be bothered by common failures such as tuning off the terminal, etc. If you want to reconnect to this session in a normal terminal, you can use:

```bash
    tmux attach -t [session_name]
```

If you forget your session_name, you can call:

```bash
    tmux list-sessions
```

In tmux, do not scroll your mouse because it has different meanings. If you'd like to view the input and output above, you should call "ctrl+b+[" first. Then you can naturally scroll your mouse to view the input and output. If you want to quit this mode, you should call "ctrl+c" (please be careful because if you press ctrl+c too many times you may accidentally stop the currently running program, which is another sad story.) If you want to quit tmux session, you should call "ctrl+b+d". 

One thing you should notice is that in PyTorch < 2.0 the "local_rank" (which is the GPU corresponding to its certain process) is set in command line. However in PyTorch >= 2.0 it's set in environment variables, and this code is written under PyTorch >= 2.0, so if you have PyTorch < 2.0, you may have to modify some part of this code for using. (BTW, this is the only part in this package that requires PyTorch >= 2.0, other parts are safe to use with PyTorch < 2.0, probably...)