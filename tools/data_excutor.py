import json

"""
从 json 提取有效的得数据集
"""


def build_test_valid_set():
    f = open('../dataset/reentrancy/train_rsc.json', 'r')
    content = f.read()
    train = json.loads(content)
    print(len(train))

    f = open('../dataset/reentrancy/valid_rsc.json', 'r')
    content = f.read()
    valid = json.loads(content)
    print(len(valid))

    train_data = {}
    valid_data = {}

    for item in train:
        if item['contract_name'] in train_data:
            continue
        train_data[item['contract_name']] = item['targets']
    print(len(train_data))

    with open("../dataset/reentrancy/train.json", "w") as f:
        json.dump(train_data, f)

    for item in valid:
        if item['contract_name'] in valid_data:
            continue
        valid_data[item['contract_name']] = item['targets']
    print(len(valid_data))
    with open("../dataset/reentrancy/valid.json", "w") as f:
        json.dump(valid_data, f)

    print("加载入文件完成...")


def construct_contracts_set():
    """
    从 test和 valid 集中找出所有不重入的智能合约
    :return:
    """


if __name__ == '__main__':
    f = open('../dataset/reentrancy/train.json', 'r')
    content = f.read()
    train = json.loads(content)
    print(len(train))

    f = open('../dataset/reentrancy/valid.json', 'r')
    content = f.read()
    valid = json.loads(content)
    print(len(valid))

    data = {}
    for key in train.keys():
        if key in data:
            continue
        data[key] = train[key]

    for key in valid.keys():
        if key in data:
            continue
        data[key] = valid[key]

    print(len(data))
