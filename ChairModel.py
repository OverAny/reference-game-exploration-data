from __future__ import print_function

import numpy as np
from copy import deepcopy

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
import torch.nn.utils.rnn as rnn_utils

class ChairModel(nn.Module):
    """
    x: text, y: image, z: latent
    Model p(z|x,y)
    @Param embedding_module: nn.Embedding
                             pass the embedding module (share with decoder)
    @Param z_dim: number of latent dimensions
    @Param hidden_dim: integer [default: 256]
                       number of hidden nodes in GRU
    """
    def __init__(self, embedding_module, rgb_dim=3, hidden_dim=256):
        super(ChairModel, self).__init__()
        assert (rgb_dim == 3)

        self.rgb_dim = rgb_dim
        self.embedding = embedding_module
        self.embedding_dim = embedding_module.embedding.embedding_dim
        self.hidden_dim = hidden_dim
        self.gru = nn.GRU(self.embedding_dim, self.hidden_dim, batch_first=True)
        self.txt_lin = nn.Linear(hidden_dim, hidden_dim // 2)
        self.rgb_seq = nn.Sequential(nn.Linear(rgb_dim, hidden_dim), \
                                        nn.ReLU(),  \
                                        nn.Linear(hidden_dim, hidden_dim // 2))
        self.linear = nn.Linear(hidden_dim, 1)
    
    def forward(self, rgb, seq, length):
        batch_size = seq.size(0)

        if batch_size > 1:
            sorted_lengths, sorted_idx = torch.sort(length, descending=True)
            seq = seq[sorted_idx]

        # embed sequences
        embed_seq = self.embedding(seq)

        # pack padded sequences
        packed = rnn_utils.pack_padded_sequence(
            embed_seq,
            sorted_lengths.data.tolist() if batch_size > 1 else length.data.tolist(), batch_first=True)

        # forward RNN
        _, hidden = self.gru(packed)
        hidden = hidden[-1, ...]
        
        if batch_size > 1:
            _, reversed_idx = torch.sort(sorted_idx)
            hidden = hidden[reversed_idx]

        txt_hidden = self.txt_lin(hidden)
        rgb_hidden = self.rgb_seq(rgb)
        print(txt_hidden)
        print(rgb_hidden)

        concat = torch.cat((txt_hidden, rgb_hidden), 1)
        # breakpoint()
        z_mu, z_logvar = torch.chunk(self.linear(concat), 2, dim=1)

        return z_mu, z_logvar

chair = ChairModel()