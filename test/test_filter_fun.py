# -*-coding:utf-8-*-
import copy
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
    for filename, input_json in files_input_json.items():
        # 生成标准的输出
        solcx.set_solc_version('v0.4.25')
        output_json = solcx.compile_standard(input_json)
        # 输出 AST 的节点
        source_nodes = solcast.from_standard_output(output_json)

        for source_node in source_nodes:
            contract_node = None
            for child in source_node._children:
                if child.nodeType == 'ContractDefinition':
                    contract_node = child
            # 节点筛选
            pruned_node = copy.deepcopy(source_node)
            li_set = set()
            for child in contract_node._children:
                if child.nodeType == 'FunctionDefinition':
                    if child.name not in ['withdraw', '']:
                        continue
                li_set.add(child)
            pruned_node._children = li_set

            pruned_node._children
