# -*-coding:utf-8-*-
from graph_generator.generate_graph import create_ast, create_separate_graph
from utils.file_util import get_one_file


def create_gmn_data(dataset_id, graph_dict, tokens_size, tokens_dict, device):
    """
    生成用于 GMN 匹配的数据集
    :param dataset_id: 数据集类型
    :param graph_dict: 文件标识 -> ASG
    :param tokens_size: 词数量
    :param tokens_dict: 词字典
    :param device: 设备
    :return:
    """
    # 数据标签所在位置
    dataset_path = 'javadata/'
    if dataset_id == '0':
        train_file = open(dataset_path + 'trainall.txt')
        valid_file = open(dataset_path + 'valid.txt')
        test_file = open(dataset_path + 'valid.txt')
    elif dataset_id == '13':
        train_file = open(dataset_path + 'train13.txt')
        valid_file = open(dataset_path + 'valid.txt')
        test_file = open(dataset_path + 'valid.txt')
    elif dataset_id == '11':
        train_file = open(dataset_path + 'train11.txt')
        valid_file = open(dataset_path + 'valid.txt')
        test_file = open(dataset_path + 'valid.txt')
    elif dataset_id == '0small':
        train_file = open(dataset_path + 'trainsmall.txt')
        valid_file = open(dataset_path + 'valid.txt')
        test_file = open(dataset_path + 'valid.txt')
    elif dataset_id == '13small':
        train_file = open(dataset_path + 'train13small.txt')
        valid_file = open(dataset_path + 'validsmall.txt')
        test_file = open(dataset_path + 'testsmall.txt')
    elif dataset_id == '11small':
        train_file = open(dataset_path + 'train11small.txt')
        valid_file = open(dataset_path + 'validsmall.txt')
        test_file = open(dataset_path + 'testsmall.txt')
    else:
        print('file not exist')
        quit()
    train_list = train_file.readlines()
    valid_list = valid_file.readlines()
    test_list = test_file.readlines()
    train_data = []
    valid_data = []
    test_data = []
    print('train data')
    train_data = create_pair_data(graph_dict, train_list, device=device)
    print('valid data')
    valid_data = create_pair_data(graph_dict, valid_list, device=device)
    print('test data')
    test_data = create_pair_data(graph_dict, test_list, device=device)
    return train_data, valid_data, test_data


def create_pair_data(graph_dict, filepath_list, device):
    """
    生成训练对
    :param graph_dict:
    :param filepath_list:
    :param device:
    :return:
    """
    datalist = []
    count_lines = 1
    for line in filepath_list:
        count_lines += 1
        pair_info = line.split()
        code1path = pair_info[0].replace('\\', '/')
        code2path = pair_info[1].replace('\\', '/')
        label = int(pair_info[2])
        # 从数据集汇总获取对应的数据
        data1 = graph_dict[code1path]
        data2 = graph_dict[code2path]
        # 图节点 id, 图的两个边向量、边对应的类型、整个图的大小
        asg1_node_list, asg1_edges, asg1_edge_type, asg1_length = data1[0][0], data1[0][1], data1[0][2], data1[1]
        asg2_node_list, asg2_edges, asg2_edge_type, asg2_length = data2[0][0], data2[0][1], data2[0][2], data2[1]
        # 图的边类型为空时,
        if not asg1_edge_type:
            asg1_edge_type = None
            asg2_edge_type = None
        # 生成对应的数据
        data = [[asg1_node_list, asg2_node_list, asg1_edges, asg2_edges, asg1_edge_type, asg2_edge_type], label]
        datalist.append(data)
    return datalist


if __name__ == '__main__':
    # 测试文件
    files_input_json1 = get_one_file()
    # tokens_size 词数量、tokens_dict 词字典、files_ast 文件名 -> ast
    files_ast, tokens_size1, tokens_dict1 = create_ast(files_input_json1)
    # 为每个合约生成一个图
    graph_dict1 = create_separate_graph(files_ast, tokens_size1, tokens_dict1)

    # tokens_size 词数量、tokens_dict 词字典、files_ast 文件名 -> ast
    create_gmn_data('0small', graph_dict1, tokens_size1, tokens_dict1, device='cpu')
