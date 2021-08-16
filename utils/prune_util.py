# -*-coding:utf-8-*
import re

"""
用以生成带修剪的函数名
"""


def split_function(file):
    """
    将合约拆分为函数段
    :param file: 文件路径
    """
    function_list = []
    f = open(file, 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()
    flag = -1
    flag1 = 0

    for line in lines:
        text = line.strip()  # 去掉末尾的换行符
        if len(text) > 0 and text != "\n":
            if text.split()[0] == "function" and len(function_list) > 0:
                flag1 = 0
        if flag1 == 0:
            if len(text) > 0 and text != "\n":
                if text.split()[0] == "function" or text.split()[0] == "function()":
                    function_list.append([text])
                    flag += 1
                elif len(function_list) > 0 and ("function" in function_list[flag][0]):
                    if text.split()[0] != "modifier" and text.split()[0] != "event":
                        function_list[flag].append(text)
                    else:
                        flag1 += 1
                        continue
        else:
            continue

    return function_list


def get_call_functions(filepath):
    """
    定位包含 call.value 的函数
    :param filepath: 原始合约地址
    """
    # 储存所有函数
    all_function_ist = split_function(filepath)
    # 存储调用 call.value 的 W 函数名
    withdraw_function = []
    # 存储 W 函数以外的函数
    other_function_list = []
    # 存储调用 W 的 C 函数
    delegate_function = []  # 存储一个调用 W 函数的 C 函数
    param = []
    # S 和 W 的关键节点
    key_count = 0
    # 匹配函数名的模式
    fun_name_pattern = re.compile(r'\b([_A-Za-z]\w*)\b(?:(?=\s*\w+\()|(?!\s*\w+))')

    # --------------------------- 处理节点  ----------------------------
    # 存储 W 函数以外的函数
    for i in range(len(all_function_ist)):
        flag = 0
        for j in range(len(all_function_ist[i])):
            text = all_function_ist[i][j]
            if '.call.value' in text:
                flag += 1
        if flag == 0:
            other_function_list.append(all_function_ist[i])

    # 遍历所有函数，找到包含 call.value 的函数, 存储 S 和 W 节点
    for i in range(len(all_function_ist)):
        for j in range(len(all_function_ist[i])):
            # 包含call.value 关键字的语句
            text = all_function_ist[i][j]
            if '.call.value' in text:
                # 获取函数名和函数参数
                fun_signature = all_function_ist[i][0]  # 函数第一行
                fun_param_pattern = re.compile(r'[(](.*?)[)]', re.S)  # 函数参数匹配模式
                result = re.findall(fun_param_pattern, fun_signature)

                result_params = result[0].split(",")  # 参数名

                for n in range(len(result_params)):
                    param.append(result_params[n].strip().split(" ")[-1])

                # 例如：function transfer(address _to, uint _value, bytes _data, string _custom_fallback)
                # 获取函数名 —— transfer
                fun_sign_list = fun_name_pattern.findall(all_function_ist[i][0])
                # 包含 call.value 调用的函数名
                function_name = fun_sign_list[1]
                withdraw_function.append(function_name)
                key_count += 1

    # 判断是否有函数中包含 call.value
    if key_count > 0:
        # 遍历所有函数，找到调用 W 函数的 C 函数节点
        # 通过匹配参数数量来确定函数调用
        for k in range(len(withdraw_function)):
            if withdraw_function[k] == "payable":
                w_name = withdraw_function[k]
            else:
                # 添加 ( 为了避免函数名与变量名重名
                w_name = withdraw_function[k] + "("

            for i in range(len(other_function_list)):
                # 函数至少大于两行
                if len(other_function_list[i]) > 2:
                    for j in range(1, len(other_function_list[i])):
                        text = other_function_list[i][j]  # 其他函数中的每一行
                        if w_name in text:
                            fun_call_pattern = re.compile(r'[(](.*?)[)]', re.S)
                            # 调用参数
                            result = re.findall(fun_call_pattern, text)
                            result_params = result[0].split(",")

                            # 获取函数名 —— transfer
                            fun_sign_list = fun_name_pattern.findall(other_function_list[i][0])
                            # 调用 W 的 C 函数名
                            function_name = fun_sign_list[1]
                            delegate_function.append(function_name)
    return withdraw_function, delegate_function


if __name__ == '__main__':
    test_contract = "../contracts/test/call.sol"
    # list_fun = split_function(test_contract)
    call_functions, delegate_functions = get_call_functions(test_contract)
    print(call_functions, delegate_functions)
