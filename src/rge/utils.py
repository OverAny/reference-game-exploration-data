from __future__ import print_function

import os
import sys
import numpy as np
import torch
import shutil
from tqdm import tqdm
from itertools import chain
from collections import Counter, OrderedDict

class OrderedCounter(Counter, OrderedDict):
     'Counter that remembers the order elements are first seen'
     def __repr__(self):
         return '%s(%r)' % (self.__class__.__name__,
                            OrderedDict(self))
     def __reduce__(self):
         return self.__class__, (OrderedDict(self),)

class AverageMeter(object):
   """Computes and stores the average and current value"""
   def __init__(self):
       self.reset()

   def reset(self):
       self.val = 0
       self.avg = 0
       self.sum = 0
       self.count = 0

   def update(self, val, n=1):
       self.val = val
       self.sum += val * n
       self.count += n
       self.avg = self.sum / self.count

def save_checkpoint(state, is_best, folder='./', filename='checkpoint.pth.tar'):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    torch.save(state, os.path.join(folder, filename))
    if is_best:
        shutil.copyfile(os.path.join(folder, filename),
                        os.path.join(folder, 'model_best.pth.tar'))
def get_text(i2w, input, length):
  text = ""
  for j in range(1,length - 1):
    text += " " + i2w[input[j]]
  return text