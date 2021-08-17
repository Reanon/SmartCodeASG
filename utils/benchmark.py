# -*-coding:utf-8-*-
import json
import os


def get_contract_dict(file_dir):
    """
    os.walk 会遍历指定目录下的所有子文件夹和子文件夹中的所有文件
    返回:  sol 的文件名
    """
    contracts = dict()
    for root1, dirs1, files1 in os.walk(file_dir):
        # root:  当前目录路径
        # dirs:  当前路径下所有子目录
        # files: 当前路径下所有非目录子文件
        for contract_type in dirs1:
            contract_files = []
            for root2, dirs2, files in os.walk(os.path.join(file_dir, contract_type)):
                for file in files:
                    if file.endswith('sol'):
                        contract_files.append(os.path.join(root1, contract_type, file))
            contracts[contract_type] = contract_files
    return contracts


def construct_benchmark(contract_dict):
    contract_bench = dict()
    for contract_type1 in contract_dict.keys():
        contract_list = []
        # 遍历下面的每一个合约
        for i in range(len(contract_dict[contract_type1])):
            # 再遍历子合约
            for contract_type2 in contract_dict.keys():
                for j in range(len(contract_dict[contract_type2])):
                    # 如果同类，标签就为 1
                    if contract_type1 == contract_type2:
                        contract_list.append(
                            contract_dict[contract_type1][i] + ' ' +
                            contract_dict[contract_type2][j] + ' '
                                                               '1'
                        )

                    else:
                        contract_list.append(
                            contract_dict[contract_type1][i] + ' ' +
                            contract_dict[contract_type2][j] + ' '
                                                               '-1'
                        )
        contract_bench[contract_type1] = contract_list
    return contract_bench


if __name__ == '__main__':
    contracts_path = '../contracts'
    contract_dict1 = get_contract_dict(contracts_path)
    t_list = construct_benchmark(contract_dict1)
