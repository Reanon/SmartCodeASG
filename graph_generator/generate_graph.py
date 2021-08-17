# -*-coding:utf-8-*-
import copy
import json
import solcx
import solcast
from anytree import AnyNode
from utils.prune_util import *
from collections import defaultdict
from utils.file_util import get_one_file

"""
从智能合约中生成树
"""

NODE_NAME = ['FunctionDefinition', 'PrimaryExpression', 'VariableDeclaration']
# 赋值语句
Assignment = ['Assignment', 'BinaryOperation', 'UnaryOperation']
MemberAccess = ['MemberAccess']
# 基本表达式 node.name
PrimaryExpression = ['Identifier', 'ElementaryTypeName', 'VariableDeclaration', 'UserDefinedTypeName']

# 边类型
EdgeType = {
    'FatherSon': 0,
    'SonFather': 1,
    'NextSibling': 2,
    'PrevSibling': 3,
    'IFStatement': 4,
    'ConditionTrue': 5,
    'ConditionFalse': 6,
    'WhileStatement': 7,
    'ForStatement': 8,
    'NextToken': 9,
    'PrevToken': 10,
    'NextUse': 11,
    'PrevUse': 12,
    'FunCall': 13
}


def get_input_jsons():
    """
    遍历数据集，生成标准输入 json
    :return:
    """
    pass


# ===================================================================== #
# --------------------------  抽象语法树修剪 ---------------------------- #
# =====================================================================  #

def prune_ast(source_ast, filepath):
    """
    修剪抽象语法树
    :param source_ast: 原始生成的抽象语法树
    :param filepath:
    :return:
    """
    # 保存修改之后的节点
    pruned_ast = copy.deepcopy(source_ast)
    # 调用 call.value 的 W 函数、调用 W 的 C 函数
    call_function, delegate_function = get_call_functions(filepath)
    for child in pruned_ast._children:
        source_node = set()
        if child.nodeType == 'ContractDefinition':
            key = 0
            contract_node = set()
            # 函数内节点
            for node in child:
                if node.nodeType == 'FunctionDefinition':
                    # 查看当前函数是否包含 call.value
                    if node.name in call_function or node.name in delegate_function:
                        # 函数则不添加当前节点继续
                        key += 1
                        contract_node.add(node)
                else:
                    contract_node.add(node)
            child._children = contract_node
            if key > 0:
                source_node.add(child)
        else:
            source_node.add(child)
    pruned_ast._children = source_node

    return pruned_ast


def create_ast(files_input_json):
    """
    生成抽象语法树
    :param files_input_json: 字典，文件路径 -> AST 的 json 格式
    :return:
        ast_dict   : 文件名 -> 合约源节点
        tokens_size: 所有合约中的 token, 也即不同的节点数
        tokens_dict: token -> id
    """
    paths_ast = []  # 路径 -> AST
    paths = []
    asts = []
    tokens = []  # 所有节点的信息
    # 指定编译版本
    solcx.set_solc_version('v0.4.25')
    for filepath, input_json in files_input_json.items():
        # 调用 py-solc-x 生成标准的输出
        output_json = solcx.compile_standard(input_json)
        # 生成 AST 的节点,一个文件生成一个节点
        source_nodes = solcast.from_standard_output(output_json)
        for source_ast in source_nodes:
            # 文件名
            paths.append(source_ast.absolutePath)
            # 修剪抽象语法树
            pruned_ast = prune_ast(source_ast, filepath)
            # 添加抽象语法树
            asts.append(pruned_ast)
            # 为当前的抽象语法树生成 token
            get_sequence(pruned_ast, tokens)

    # 文件路径 -> 抽象语法树
    paths_ast = dict(zip(paths, asts))
    # token 去重, 并维持一定顺序
    tokens = sorted(set(tokens), key=tokens.index)
    # token 数
    tokens_size = len(tokens)
    # token 的 id
    tokens_id = range(tokens_size)
    # token -> id
    tokens_dict = dict(zip(tokens, tokens_id))
    return paths_ast, tokens_size, tokens_dict


# ===================================================================== #
# ---------------------------  生成树  --------------------------------- #
# =====================================================================  #
def create_tree(root, node, node_list, parent=None):
    """
    生成树
    :param root: 树根
    :param node: AST 的节点
    :param node_list: 节点列表
    :param parent: 父节点
    :return:
    """
    id = len(node_list)
    token, children = get_token(node), get_children(node)
    if id == 0:
        root.token = token
        root.data = node
    else:
        new_node = AnyNode(id=id, token=token, data=node, parent=parent)
    node_list.append(node)
    for child in children:
        # 当前是根节点
        if id == 0:
            create_tree(root, child, node_list, parent=root)
        else:
            create_tree(root, child, node_list, parent=new_node)


def get_token(node):
    """
    生成当前节点的 token
    :param node:
    :return:
    """
    if hasattr(node, 'nodeType'):
        if node.nodeType == 'FunctionDefinition':
            if node.name == '':
                return 'payable'
            return node.name
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

    return None


def get_children(node):
    """
    获取节点的子节点
    :param node:
    :return:
    """
    # 调用 solc-ast 的节点内部属性
    children = node._children
    return children


def get_sequence(node, tokens):
    """
    从抽象语法树中获取标记（token)
    :param node: 抽象语法树的节点
    :param tokens: 标记集合
    :return:
    """
    # 获取当期节点的 token
    token = get_token(node)
    # 获取当前节点的子节点
    children = get_children(node)
    # 添加 token
    if token is not None:
        tokens.append(token)
    # 继续遍历子节点的生成 token
    for child in children:
        get_sequence(child, tokens)


# ======================================================================#
# ---------------------------  生成控制流  ------------------------------#
# ======================================================================#

def get_node_edge(node, node_index_list, tokens_dict, edge_source, edge_target, edge_type):
    """
    为树生成父节点与子节点的边
    :param node: AnyTree 的 node
    :param node_index_list: 节点 id 列表
    :param tokens_dict: token -> id
    :param edge_source: 边起点 列表
    :param edge_target: 边终点 列表
    :param edge_type: 边类型
    :return:
    """
    token = node.token
    node_index_list.append(tokens_dict[token])
    for child in node.children:
        edge_source.append(node.id)
        edge_target.append(child.id)
        edge_type.append(EdgeType['FatherSon'])
        # 添加反向流
        edge_source.append(child.id)
        edge_target.append(node.id)
        edge_type.append(EdgeType['SonFather'])
        get_node_edge(child, node_index_list, tokens_dict, edge_source, edge_target, edge_type)


def get_node_sibling_edge(node, tokens_dict, edge_source, edge_target, edge_type):
    """
    在兄弟节点之间生成边
    """
    token = node.token
    for i in range(len(node.children) - 1):
        edge_source.append(node.children[i].id)
        edge_target.append(node.children[i + 1].id)
        edge_type.append(EdgeType['NextSibling'])
        # 添加反向边
        edge_source.append(node.children[i + 1].id)
        edge_target.append(node.children[i].id)
        edge_type.append(EdgeType['PrevSibling'])
    for child in node.children:
        get_node_sibling_edge(child, tokens_dict, edge_source, edge_target, edge_type)


def get_node_if_edge(node, tokens_dict, edge_source, edge_target, edge_type):
    """
    生成节点之间 IF 语句的边
    """
    token = node.token
    if token == 'IfStatement':
        # 当期节点的数据
        data = node.data
        # IF 语句的判断节点
        condition = data.condition
        falseBody = data.falseBody[0] if data.falseBody is not None and len(data.falseBody) else None
        trueBody = data.trueBody[0] if len(data.trueBody) else None
        conditionToken, falseToken, trueToken = get_token(condition), get_token(falseBody), get_token(trueBody),
        condition_node, false_node, true_node = None, None, None
        # 从solc-ast 节点中找出 AnyTree 对应的节点
        for child in node.children:
            if child.token == conditionToken:
                condition_node = child
            if child.token == falseToken:
                false_node = child
            if child.token == trueToken:
                true_node = child
            # IfStatement 分别给子节点都添加上边
            edge_source.append(node.id)
            edge_target.append(child.id)
            edge_type.append(EdgeType['IFStatement'])
            # 反向
            edge_source.append(child.id)
            edge_target.append(node.id)
            edge_type.append(EdgeType['IFStatement'])

        # 在给不同 IF 语句之间添加不同的条件边
        if condition_node is not None:
            if true_node is not None:
                edge_source.append(condition_node.id)
                edge_target.append(true_node.id)
                edge_type.append(EdgeType['ConditionTrue'])
                # 反向
                edge_source.append(true_node.id)
                edge_target.append(condition_node.id)
                edge_type.append(EdgeType['ConditionTrue'])
            if false_node is not None:
                edge_source.append(condition_node.id)
                edge_target.append(false_node.id)
                edge_type.append(EdgeType['ConditionFalse'])
                # 反向
                edge_source.append(false_node.id)
                edge_target.append(condition_node.id)
                edge_type.append(EdgeType['ConditionFalse'])


def get_node_while_edge(node, tokens_dict, edge_source, edge_target, edge_type):
    """
    生成节点之间 WHILE 语句的边
    """
    token = node.token
    if token == 'WhileStatement':
        # 当期节点的数据
        data = node.data
        # while 语句的判断节点
        condition = data.condition
        conditionToken = get_token(condition)
        # 找出 AnyTree 对应的节点
        for child in node.children:
            if child.token == conditionToken:
                condition_node = child
            # WhileStatement 分别给子节点都添加上边
            edge_source.append(node.id)
            edge_target.append(child.id)
            edge_type.append(EdgeType['WhileStatement'])
            # 反向
            edge_source.append(child.id)
            edge_target.append(node.id)
            edge_type.append(EdgeType['WhileStatement'])

        # TODO: 将 Condition 与 Body 相连接


def get_node_for_edge(node, tokens_dict, edge_source, edge_target, edge_type):
    """
    生成节点之间 For 语句的边
    """
    token = node.token
    if token == 'ForStatement':
        # 当期节点的数据
        data = node.data
        # For 语句的循环判断节点
        loopExpression = data.loopExpression
        loopExpressionToken = get_token(loopExpression)
        # 找出 AnyTree 对应的节点
        for child in node.children:
            if child.token == loopExpressionToken:
                loopExpression_node = child
            # ForStatement 分别给子节点都添加上边
            edge_source.append(node.id)
            edge_target.append(child.id)
            edge_type.append(EdgeType['ForStatement'])
            # --反向--
            edge_source.append(child.id)
            edge_target.append(node.id)
            edge_type.append(EdgeType['ForStatement'])


def get_control_flow_edge(node, tokens_dict, edge_source, edge_target, edge_type):
    """
    获取控制流节点
    """
    # 生成 IF 控制流
    get_node_if_edge(node, tokens_dict, edge_source, edge_target, edge_type)
    # 生成 While 控制流
    get_node_while_edge(node, tokens_dict, edge_source, edge_target, edge_type)
    # 生成 For 控制流
    get_node_for_edge(node, tokens_dict, edge_source, edge_target, edge_type)
    for child in node.children:
        get_control_flow_edge(child, tokens_dict, edge_source, edge_target, edge_type)


# ======================================================================#
# --------------------------- 生成数据流  -------------------------------#
# ======================================================================#

def get_leaf_node_edge(node, tokens_dict, edge_source, edge_target, edge_type):
    """
    为叶子节点之间连接边
    """
    leaf_node_id = []

    def get_leaf_node_list(node, leaf_node_id):
        """
        内部函数: 获取叶子节点的 token id
        """
        token = node.token
        if len(node.children) == 0:
            leaf_node_id.append(node.id)
        for child in node.children:
            get_leaf_node_list(child, leaf_node_id)

    get_leaf_node_list(node, leaf_node_id)
    for i in range(len(leaf_node_id) - 1):
        # 给叶子节点之间添加上边
        edge_source.append(leaf_node_id[i])
        edge_target.append(leaf_node_id[i + 1])
        edge_type.append(EdgeType['NextToken'])
        # --反向--
        edge_source.append(leaf_node_id[i + 1])
        edge_target.append(leaf_node_id[i])
        edge_type.append(EdgeType['PrevToken'])


def get_variables_token(tree):
    """
    获取用户变量的节点
    :param tree: 根节点
    """
    # 获取抽象语法树中变量定义的节点
    variable_nodes = tree.children(
        include_children=False,
        filters={'nodeType': "VariableDeclaration"})
    variables_token = []
    for node in variable_nodes:
        variables_token.append(get_token(node))

    return variables_token


def get_variables_node_edge(node, tokens_dict, edge_source, edge_target, edge_type, variables_token):
    """
    为变量节点之间生成边
    """
    # var -> 节点 id 列表
    variables_dict = defaultdict(list)

    def get_variables_node_dict(node, variables_token, variables_dict):
        token = node.token
        if token in variables_token:
            variables_dict[token].append(node.id)
        for child in node.children:
            get_variables_node_dict(child, variables_token, variables_dict)

    get_variables_node_dict(node, variables_token, variables_dict)

    for v in variables_dict.keys():
        for i in range(len(variables_dict[v]) - 1):
            # 给变量节点之间添加上边
            edge_source.append(variables_dict[v][i])
            edge_target.append(variables_dict[v][i + 1])
            edge_type.append(EdgeType['NextUse'])
            # --反向--
            edge_source.append(variables_dict[v][i + 1])
            edge_target.append(variables_dict[v][i])
            edge_type.append(EdgeType['PrevUse'])

    token = node.token


def create_separate_graph(files_ast, tokens_size, tokens_dict):
    """
    为单个合约生成图
    :param files_ast:  文件名 -> 抽象语法树
    :param tokens_size: 所有合约中的 token 大小
    :param tokens_dict: token -> id
    :return: graph_dict: 合约名 -> 合约图结构
        graph_dict 包含三个维度的数据
            node_index_list: 图节点的 id
            edges: 节点与节点之间的边
            edge_type: 边的类型
    """
    graph_dict = {}
    file_list = []
    graph_list = []
    for file, tree in files_ast.items():
        # 节点列表
        node_list = []
        # 新树, 根节点 id 为 0
        new_tree = AnyNode(id=0, token=None, data=None)
        # 从抽象语法树中构造出树来: 树根、AST、节点列表
        create_tree(new_tree, tree, node_list)
        # 节点索引列表，保存该树 token 的 id
        node_index_list = []
        edge_source = []  # 边的起始
        edge_target = []  # 边的终结节点
        edge_type = []  # 边类型

        # 为树生成节点访问的边
        get_node_edge(new_tree, node_index_list, tokens_dict, edge_source, edge_target, edge_type)
        # 生成兄弟节点之间的边
        get_node_sibling_edge(new_tree, tokens_dict, edge_source, edge_target, edge_type)
        # 获取 控制流 边: for、while、if
        get_control_flow_edge(new_tree, tokens_dict, edge_source, edge_target, edge_type)
        # 获取叶子节点之间的边
        get_leaf_node_edge(new_tree, tokens_dict, edge_source, edge_target, edge_type)
        # 获取 AST 中变量节点
        variables_token = get_variables_token(tree)
        # 生成变量之间的边
        get_variables_node_edge(new_tree, tokens_dict, edge_source, edge_target, edge_type, variables_token)

        # TODO: 生成函数调用边

        # ======================================================================#
        # --------------------------- 整理数据  ---------------------------------#
        # ======================================================================#
        # 边: source -> target
        edges = [edge_source, edge_target]
        # 图节点的数
        graph_length = len(node_index_list)
        # 文件列表
        file_list.append(file)
        # 图列表
        graph_list.append([[node_index_list, edges, edge_type], graph_length])
        # 合约名 -> 图
        graph_dict[file] = [[node_index_list, edges, edge_type], graph_length]

    # 打印节点
    print(edge_source)
    print(edge_target)
    # print(edge_type)
    return graph_dict


if __name__ == '__main__':
    # 测试单个文件
    files_input_json1 = get_one_file()
    # 创建 AST 树
    # tokens_size 词数量、tokens_dict 词字典、files_ast 文件名 -> ast
    files_ast1, tokens_size1, tokens_dict1 = create_ast(files_input_json1)
    # 为每个合约生成一个图
    graph_dict1 = create_separate_graph(files_ast1, tokens_size1, tokens_dict1)

    print(graph_dict1)
