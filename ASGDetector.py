# -*-coding:utf-8-*-
import math
import os
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim
import numpy as np
import time
import sys
import argparse
from tqdm import tqdm, trange
from parser import parameter_parser
from graph_generator.generate_gmn_data import contract_data, create_gmn_data
from graph_generator.generate_graph import create_ast, create_separate_graph
from model.GMN import *
from torch_geometric.data import Data, DataLoader

args = parameter_parser()

device = torch.device('cuda:0')


def create_batches(data):
    # random.shuffle(data)
    batches = [data[graph:graph + args.batch_size] for graph in range(0, len(data), args.batch_size)]
    return batches


def main():
    # 文件路径
    contract_path = "contracts/"
    # 测试多个文件输入文件
    files_input_json1 = contract_data(contract_path)
    # tokens_size 词数量、tokens_dict 词字典、files_ast 文件名 -> ast
    files_ast, tokens_size1, tokens_dict1 = create_ast(files_input_json1)
    # 为每个合约生成一个图
    graph_dict1 = create_separate_graph(files_ast, tokens_size1, tokens_dict1)

    # 指定要测试漏洞类型
    data_set = args.dataset
    # 数据集、files_ast 文件名 -> ast
    train_data, valid_data, test_data = create_gmn_data(data_set, graph_dict1)

    if args.model == 'GMN':
        model = GMNNet(tokens_size1, embedding_dim=100, num_layers=4, device=device).to(device)
        optimizer = optim.Adam(model.parameters(), lr=args.lr)
        criterion = nn.CosineEmbeddingLoss()
        criterion2 = nn.MSELoss()

    epochs = trange(args.epochs, leave=True, desc="Epoch")
    for epoch in epochs:  # without batching
        print(epoch)
        batches = create_batches(train_data)
        total_loss = 0.0
        main_index = 0.0
        for index, batch in tqdm(enumerate(batches), total=len(batches), desc="Batches"):
            optimizer.zero_grad()
            batch_loss = 0
            for data, label in batch:
                label = torch.tensor(label, dtype=torch.float, device=device)
                x1, x2, edge_index1, edge_index2, edge_attr1, edge_attr2 = data
                x1 = torch.tensor(x1, dtype=torch.long, device=device)
                x2 = torch.tensor(x2, dtype=torch.long, device=device)
                edge_index1 = torch.tensor(edge_index1, dtype=torch.long, device=device)
                edge_index2 = torch.tensor(edge_index2, dtype=torch.long, device=device)
                if edge_attr1 is not None:
                    edge_attr1 = torch.tensor(edge_attr1, dtype=torch.long, device=device)
                    edge_attr2 = torch.tensor(edge_attr2, dtype=torch.long, device=device)
                data = [x1, x2, edge_index1, edge_index2, edge_attr1, edge_attr2]
                prediction = model(data)
                # batchloss=batchloss+criterion(prediction[0],prediction[1],label)
                cossim = F.cosine_similarity(prediction[0], prediction[1])
                batch_loss = batch_loss + criterion2(cossim, label)
            batch_loss.backward(retain_graph=True)
            optimizer.step()
            loss = batch_loss.item()
            total_loss += loss
            main_index = main_index + len(batch)
            loss = total_loss / main_index
            epochs.set_description("Epoch (Loss=%g)" % round(loss, 5))
        # 测试模型并且给出评估指标
        test_results = test(model, test_data)

        with open('results/' + args.model + '_epoch_' + str(epoch + 1), mode='w') as f:
            for res in test_results:
                f.write(str(res) + '\n')

        # devresults = test(validdata)
        # devfile = open('gmnbcbresult/' + args.graphmode + '_dev_epoch_' + str(epoch + 1), mode='w')
        # for res in devresults:
        #     devfile.write(str(res) + '\n')
        # devfile.close()


# 测试集
def train():
    pass


# 测试集
def test(model, dataset):
    # model.eval()
    count = 0
    correct = 0
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    results = []
    for data, label in dataset:
        label = torch.tensor(label, dtype=torch.float, device=device)
        x1, x2, edge_index1, edge_index2, edge_attr1, edge_attr2 = data
        x1 = torch.tensor(x1, dtype=torch.long, device=device)
        x2 = torch.tensor(x2, dtype=torch.long, device=device)
        edge_index1 = torch.tensor(edge_index1, dtype=torch.long, device=device)
        edge_index2 = torch.tensor(edge_index2, dtype=torch.long, device=device)
        if edge_attr1 is not None:
            edge_attr1 = torch.tensor(edge_attr1, dtype=torch.long, device=device)
            edge_attr2 = torch.tensor(edge_attr2, dtype=torch.long, device=device)
        data = [x1, x2, edge_index1, edge_index2, edge_attr1, edge_attr2]
        prediction = model(data)
        output = F.cosine_similarity(prediction[0], prediction[1])
        results.append(output.item())
        prediction = torch.sign(output).item()

        if prediction > args.threshold and label.item() == 1:
            tp += 1
            # print('tp')
        if prediction <= args.threshold and label.item() == -1:
            tn += 1
            # print('tn')
        if prediction > args.threshold and label.item() == -1:
            fp += 1
            # print('fp')
        if prediction <= args.threshold and label.item() == 1:
            fn += 1
            # print('fn')
    # 训练之后计算表现
    performance(tn, fn, fp, tp)
    return results


def performance(tn, fn, fp, tp):
    """
    评估模型的指标
    """
    print(tn, fn, fp, tp)

    print('Accuracy:', (tn + tp) / (tn + fp + fn + tp))
    recall = tp / (tp + fn)
    print('Recall(TPR): ', recall)
    print('False positive rate(FPR): ', fp / (fp + tn))
    # print('False negative rate(FNR): ', fn / (fn + tp))

    precision = tp / (tp + fp)
    print('Precision: ', precision)
    print('F1 score: ', (2 * precision * recall) / (precision + recall))


if __name__ == '__main__':
    main()
    # performance(244, 150, 98, 342)
