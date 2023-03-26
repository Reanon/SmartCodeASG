# -*-coding:utf-8-*
import os

from graph_generator.generate_graph import create_ast, create_separate_graph
from common.utils.file import get_standard_json


def create_gmn_data(dataset, graph_dict):
    """
    生成用于 GMN 匹配的数据集
    :param dataset: 数据集类型
    :param graph_dict: 文件标识 -> ASG
    :return:
    """
    # 数据标签所在位置, 相对路径在单个文件测试的时候有效
    # dataset_directory = '../benchmark/'
    # 绝对路径, 在检测的时候有效
    dataset_directory = './benchmark/'
    filepath = dataset_directory + dataset + '/'
    if dataset in ['reentrancy', 'overflow']:
        train_file = open(filepath + 'train.txt')
        valid_file = open(filepath + 'valid.txt')
        test_file = open(filepath + 'test.txt')
    else:
        print('file not exist')
        quit()
    # 将基准读出来
    train_list = train_file.readlines()
    valid_list = valid_file.readlines()
    test_list = test_file.readlines()

    print('train data')
    train_data = create_pair_data(graph_dict, train_list)
    print('valid data')
    valid_data = create_pair_data(graph_dict, valid_list)
    print('test data')
    test_data = create_pair_data(graph_dict, test_list)
    return train_data, valid_data, test_data


def create_pair_data(graph_dict, filepath_list):
    """
    生成训练对
    :param graph_dict: 文件名 -> asg
    :param filepath_list: 文件列表
    :return:
    """
    datalist = []
    count_lines = 1
    for line in filepath_list:
        count_lines += 1
        pair_info = line.split()
        # code1path = pair_info[0].replace('\\', '/')
        # code2path = pair_info[1].replace('\\', '/')
        try:
            code1path = pair_info[0]
            code2path = pair_info[1]
            label = int(pair_info[2])
            if code1path in graph_dict.keys() and code2path in graph_dict.keys():
                # 从数据集汇总获取对应的数据
                data1 = graph_dict[code1path]
                data2 = graph_dict[code2path]
                # 图节点 id, 图的两个边向量、边对应的类型、整个图的大小
                asg1_node_list, asg1_edges, asg1_edge_type, asg1_length = data1[0][0], data1[0][1], data1[0][2], data1[
                    1]
                asg2_node_list, asg2_edges, asg2_edge_type, asg2_length = data2[0][0], data2[0][1], data2[0][2], data2[
                    1]
                # 图的边类型为空时,
                if not asg1_edge_type:
                    asg1_edge_type = None
                    asg2_edge_type = None
                # 生成对应的数据
                data = [[asg1_node_list, asg2_node_list, asg1_edges, asg2_edges, asg1_edge_type, asg2_edge_type], label]
                datalist.append(data)
        except IndexError:
            print("Error")

    return datalist


def contract_data(contract_path):
    """
    标准 json 文件
    """
    filepath_input = dict()

    contract_files = []
    for root1, dirs1, files1 in os.walk(contract_path):
        # root:  当前目录路径
        # dirs:  当前路径下所有子目录
        # files: 当前路径下所有非目录子文件
        for contract_type in dirs1:
            for root2, dirs2, files in os.walk(os.path.join(contract_path, contract_type)):
                for file in files:
                    if file.endswith('sol'):
                        # 只添加文件名
                        filepath = os.path.join(root1, contract_type, file)
                        filepath_input[file] = get_standard_json(filepath)
                        # contract_files.append()

                        # contract_files.append(file)

    # for filepath in contract_files:
    #     # 将文件路径传入
    #     filepath_input[filepath] =
    return filepath_input


if __name__ == '__main__':
    # 文件路径
    contract_path = "../contracts/"
    # 测试多个文件输入文件
    files_input_json1 = contract_data(contract_path)
    # tokens_size 词数量、tokens_dict 词字典、files_ast 文件名 -> ast
    files_ast, tokens_size1, tokens_dict1 = create_ast(files_input_json1)
    # 为每个合约生成一个图
    graph_dict1 = create_separate_graph(files_ast, tokens_size1, tokens_dict1)

    # 数据集、files_ast 文件名 -> ast
    train_data1, valid_data1, test_data1 = create_gmn_data('reentrancy', graph_dict1)
