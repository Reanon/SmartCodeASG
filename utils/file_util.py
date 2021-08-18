import json
import os
import sys


# ===================================================================== #
# --------------------------  基本文件操作   ---------------------------  #
# ===================================================================== #
def file_walk(file_dir):
    """
    os.walk 会遍历指定目录下的所有子文件夹和子文件夹中的所有文件
    返回:  sol 的文件名
    """
    for root, dirs, files in os.walk(file_dir):
        # root:  当前目录路径
        # dirs:  当前路径下所有子目录
        # files: 当前路径下所有非目录子文件
        contract_files = []
        for file in files:
            if file.endswith('sol'):
                contract_files.append(file)
        return contract_files


def get_files_name(contract_path):
    """
    返回所有智能合约文件名
    :param contract_path: 合约所在文件夹
    :return:
    """
    # 获取所有合约文件
    files = file_walk(contract_path)
    filenames = []
    for file in files:
        # 获取合约的文件名
        # 只获取合约名, 去掉后缀
        filename = file.split(".")[0]
        filenames.append(filename + '.sol')
    return filenames


# ===================================================================== #
# -----------------------  solc 标准输入格式   -------------------------  #
# ===================================================================== #

def get_standard_json(filepath):
    """
    生成该合约的标准输入
    """
    # 读取文件内容
    content = ''
    with open(filepath, 'r') as f:
        content = f.read()
    # 标准 json 输入
    standard_json = '''
    {
        "language": "Solidity",
        "sources": {},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["*"]
                },
                "*": {
                    "": [ "ast" ]
                }
            }
        }
    }
    '''
    # json 数据转成 dict 字典
    standard_input = json.loads(standard_json)
    # 添加文件
    sources = {filepath: {'content': content}}
    standard_input["sources"] = sources
    return standard_input


def get_standard_json_old(contract_path, filename):
    """
    生成该合约的标准输入
    """
    filepath = contract_path + '/' + filename
    # 读取文件内容
    content = ''
    with open(filepath, 'r') as f:
        content = f.read()
    # 标准 json 输入
    standard_json = '''
    {
        "language": "Solidity",
        "sources": {},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["*"]
                },
                "*": {
                    "": [ "ast" ]
                }
            }
        }
    }
    '''
    # json 数据转成 dict 字典
    standard_input = json.loads(standard_json)
    # 添加文件
    sources = {filename: {'content': content}}
    standard_input["sources"] = sources
    return standard_input


# ===================================================================== #
# --------------------------  生成测试文件   ---------------------------- #
# =====================================================================  #

def get_one_file():
    """
    返回一个测试用的标准 json 文件
    """
    contract_path = "../contracts_test/test/"
    # filename = "Ballot.sol"
    # filename = "reentrance.sol"
    # 多个合约
    filename = "0x4320e6f8c05b27ab4707cd1f6d5ce6f3e4b3a5a1.sol"
    filepath_input = {contract_path + filename: get_standard_json(contract_path, filename)}
    return filepath_input


def get_one_test_file():
    """
    返回一个测试用的标准 json 文件
    """
    contract_path = "../contracts_test/test/"
    filename = "call.sol"
    file_input = {contract_path + filename: get_standard_json(contract_path, filename)}
    return file_input


if __name__ == '__main__':
    test = get_one_file()
    print(test)
