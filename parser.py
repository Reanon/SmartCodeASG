# -*-coding:utf-8-*-
import argparse


# 解析字符串
def parameter_parser():
    # Experiment parameters
    # 工具描述
    parser = argparse.ArgumentParser(description='Smart Contracts Vulnerability Detection')
    # 指定数据集 data_setting
    parser.add_argument('-D', '--dataset', type=str, default='reentrancy',
                        choices=['reentrancy', 'unchecked_low_level_calls'])
    # 指定模型
    parser.add_argument('-M', '--model', type=str, default='GMN',
                        choices=['GMN', 'GGNN'])
    # 学习率
    parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
    # 阈值
    parser.add_argument("--threshold", default=0)
    # 迭代数 num_epochs
    parser.add_argument('--epochs', type=int, default=10, help='number of epochs')
    # 批数据量
    parser.add_argument('-b', '--batch_size', type=int, default=32, help='batch size')

    parser.add_argument('-d', '--dropout', type=float, default=0.2, help='dropout rate')

    # -------
    # parser.add_argument("--cuda", default=True)
    # parser.add_argument("--graphmode", default='astandnext')
    #
    # parser.add_argument("--data_setting", default='11')
    # parser.add_argument("--batch_size", default=32)
    # parser.add_argument("--num_layers", default=4)
    # parser.add_argument("--num_epochs", default=10)

    return parser.parse_args()
