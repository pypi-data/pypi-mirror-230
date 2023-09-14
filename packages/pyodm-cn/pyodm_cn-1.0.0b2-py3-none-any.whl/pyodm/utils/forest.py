from functools import reduce
from typing import Union, List

from pyodm.utils.node import Node


class Forest:
    """
    Forest 为自定义的数据结构.

    它的目标是把传入的数组，转化为树形结构

    branch.

    degree.

    level.

    node_values.

    """

    def __init__(self):
        self._degree = 1
        self.nodes: list[list[Node]] = [[]]

    @property
    def degree(self):
        return self._degree

    def root(self) -> Node:
        return self.get_level_nodes(0)[0]

    @property
    def is_empty(self):
        return len(self.nodes[0]) == 0

    def __create_node(self, parent_index: int = None, level: int = 0, **node_values):
        """
        创建子节点，并返回子节点在对应层的索引值

        :param parent_index: 父节点的索引值

        :type parent_index: int

        :param level: 层级

        :type level: int

        :param node_values: 节点的值

        :type node_values:

        :return: 子节点的索引值

        :rtype: int
        """
        node = Node.new(self, parent_index, level, **node_values)
        index = self.__add_node(parent_index, level, node)
        if node.has_parent():
            node.parent().add_child(index)
        return index

    def add_branch(self, branch: list[dict]) -> None:
        """
        添加树的子节点

        :param branch: 从根节点开始的一个分支,该列表包含该分支每一个经过的节点

        :type branch: list[dict]

        :return: None
        :rtype: None
        """

        """验证新加的分支的第一个节点是否为根节点"""
        # if not self.is_empty:
        #     if not self.root().satisfy(**branch[0]): raise Exception(f'{branch[0]} is not root')
        """如果新加的分支的度数>当前树的度数"""
        while len(branch) > self.degree:
            self.nodes.append([])
            self._degree += 1
        """每个数组的第一位都表示根节点，所以每次进入函数时 parent 设置为 None"""
        parent = None
        for level in range(self.degree):
            """每一个分支深度不一样, 为避免越界"""
            if level <= len(branch) - 1:
                parent = self.__create_node(parent, level, **branch[level])

    def clean(self):
        self.nodes: list[list[Node]] = [[]]
        self._degree = 1

    def index(self, level, i) -> Node:
        return self.get_level_nodes(level)[i]

    def find(self, level: int, xrange: set,fuzzy: bool = False, **node_values) -> Union[None, Node]:
        """
        指定索引搜索满足props条件的值

        :param fuzzy: 是否模糊匹配， 默认为关闭 False
        :type fuzzy:
        :param level: 指定查询的层级
        :type level: int
        :param xrange: 查询的范围
        :type xrange:
        :param node_values: 满足条件的值
        :type node_values: dict
        :return:
        :rtype:
        """
        result = None
        if fuzzy: result = list(filter(lambda i: self.nodes[level][i].fuzzy_matching(**node_values), xrange))
        else: result = list(filter(lambda i: self.nodes[level][i].satisfy(**node_values), xrange))
        if not result: return None
        return self.nodes[level][result[0]]

    def search(self, level: int, fuzzy: bool = False, **node_values) -> list[Node]:
        """
        在指定层级搜索满足条件的节点

        :param fuzzy: 是否模糊搜索，默认是关闭为 False
        :type fuzzy: Boolean
        :param level: 指定的层级
        :type level: int
        :param node_values: 满足条件的值
        :type node_values: dict
        :return: 如果有满足的条件的值，则返回 list, 如果没有的话，则返回一个空 list
        :rtype: list[Node]
        """
        if fuzzy: return list(filter(lambda node: node.fuzzy_matching(**node_values), self.nodes[level]))
        return list(filter(lambda node: node.satisfy(**node_values), self.nodes[level]))

    def get_level_nodes(self, level: int) -> list[Node]:
        """
        获取 指定层级下的所有节点

        :param level: 指定的层级
        :type level:  int
        :return: 指定层级的节点列表
        :rtype: list[Node]
        """
        return self.nodes[level]

    def __add_node(self, parent_index: int, level: int, node: Node) -> int:
        """
        添加节点，并返回新加节点的索引值.

        如果是已经存在的节点，则直接返回已存在的索引值.

        如果是未存在的节点，则新建节点，并返回新的索引值.

        :param parent_index:
        :type parent_index:
        :param level:
        :type level:
        :param node:
        :type node:
        :return:
        :rtype:
        """
        level_nodes = self.nodes[level]

        if parent_index is None:
            # level = 0 的层级节点. 根节点
            # 因为level = 0 层级的节点，没有父节点，所以直接判断是否已存在相同节点，如果存在直接返回索引值
            for i in range(len(level_nodes)):
                if level_nodes[i].eql(node): return i
        else:
            # level != 0 的层级节点. 非根节点
            # 因为是有父节点的，所以判断有相同父节点的兄弟节点中是否已存在相同节点，如果存在直接返回索引值
            for i in self.nodes[level - 1][parent_index].children_index:
                if level_nodes[i].eql(node): return i
        # 节点为新节点,加入对应层级的节点列表，并返回索引
        node.index = len(level_nodes)
        self.nodes[level].append(node)
        return node.index

    def reset(self, branches: list[list[dict]]):
        """
        用新的分支 重置 Forest
        :param branches: 新传入的分支
        :type branches: list[list[dict]]
        :return:
        :rtype:
        """
        self.clean()
        self.nodes = [[]]
        for branch in branches: self.add_branch(branch)

    @classmethod
    def factory(cls, branch: list[dict] = None):
        """
        构建一个度数为 degree 的森林

        :param branch: 可选参数, 分支

        :type branch: list[dict]

        :return: 一个度数为 degree 的空的森林 或 有一个分支度数为 degree的森林

        :rtype: Forest
        """
        __tree = Forest()
        if branch is not None: __tree.add_branch(branch)
        return __tree

    @classmethod
    def transform(cls, branches: list[list[dict]]):
        """
        把 2维 数组转化为森林.

        该 2 维数组每一行为一个从根节点开始的一个分支

        :param branches: 2维数组
        :type branches: list[list[dict]]
        :return: 森林
        :rtype: Forest
        """
        __degree = reduce(lambda x, y: x if x > y else y, [len(branch) for branch in branches])
        __tree = Forest()
        for branch in branches:
            __tree.add_branch(branch)
        return __tree
