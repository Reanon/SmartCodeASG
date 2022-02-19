import json
import solcx
import solcast
from utils.file_util import *

NODE_NAME = ['FunctionDefinition', 'PrimaryExpression', 'VariableDeclaration']
# 赋值语句
Assignment = ['Assignment', 'BinaryOperation']
MemberAccess = ['MemberAccess']
# 基本表达式 node.name
PrimaryExpression = ['Identifier', 'ElementaryTypeName', 'VariableDeclaration']


def get_token(node):
    """
    生成当前节点的 token
    :param node:
    :return:
    """
    if hasattr(node, 'nodeType'):
        if node.nodeType in NODE_NAME:
            return node.name
        if node.nodeType in PrimaryExpression:
            return node.name
        if node.nodeType in MemberAccess:
            return node.memberName
        if node.nodeType in Assignment:
            return node.operator
        if node.nodeType is not None:
            # 其余的直接返回
            return node.nodeType


if __name__ == '__main__':
    # 测试文件
    files_input_json = get_one_test_file()
    # files_input_json = get_one_file()
    for filename, input_json in files_input_json.items():
        # 生成标准的输出

        solcx.set_solc_version('v0.4.25')
        output_json = solcx.compile_standard(input_json)
        # 输出 AST 的节点
        source_nodes = solcast.from_standard_output(output_json)
        for source_node in source_nodes:
            # children = source_node.children(filters=None)
            # children = source_node.children()
            # children = source_node.children(
            #     include_children=False,
            #     filters={'nodeType': "VariableDeclaration"})
            children = source_node.children(
                include_children=False,
                # filters={'nodeType': "FunctionCall", "expression.name": "value"})
                filters={'nodeType': "FunctionCall"})
            # filters={'nodeType': "Function",
             #
            #          "typeDescriptions.typeIdentifier": "t_function_barecall_payable$__$returns$_t_bool_$value"})

            tokens = []
            for child in children:
                # 不为空
                tokens.append(get_token(child))
            print(tokens)
