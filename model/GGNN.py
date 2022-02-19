# -*-coding:utf-8-*-
from abc import ABC

import torch
import torch.nn as nn
from torch.nn import Parameter
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing, GatedGraphConv
from torch_geometric.utils import degree, remove_self_loops, add_self_loops, softmax
from torch_geometric.nn.inits import glorot, zeros
from torch_geometric.nn.glob import GlobalAttention
import sys
import inspect


class GGNN(torch.nn.Module):
    def __init__(self, vocablen, embedding_dim, num_layers, device):
        super(GGNN, self).__init__()
        self.device = device
        # self.num_layers=num_layers
        self.embed = nn.Embedding(vocablen, embedding_dim)
        self.edge_embed = nn.Embedding(20, embedding_dim)
        # self.gmn=nn.ModuleList([GMNlayer(embedding_dim,embedding_dim) for i in range(num_layers)])
        self.ggnnlayer = GatedGraphConv(embedding_dim, num_layers)
        self.mlp_gate = nn.Sequential(nn.Linear(embedding_dim, 1), nn.Sigmoid())
        self.pool = GlobalAttention(gate_nn=self.mlp_gate)

    def forward(self, data):
        x, edge_index, edge_attr = data
        x = self.embed(x)
        x = x.squeeze(1)
        if type(edge_attr) == type(None):
            edge_weight = None
        else:
            edge_weight = self.edge_embed(edge_attr)
            edge_weight = edge_weight.squeeze(1)
        x = self.ggnnlayer(x, edge_index)
        batch = torch.zeros(x.size(0), dtype=torch.long).to(self.device)
        hg = self.pool(x, batch=batch)
        return hg
