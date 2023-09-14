"""
level 0: site
level 1 :subject
level 2 :visit
level 3 :form
level 4 :ig
level 5 :item (variable, item_id, question)
"""

class Node:

    def __init__(self, tree, parent_index=None, level=0):
        self.children_index: set[int] = set()
        self.parent_index = parent_index
        self.values = dict()
        self.level = level
        self.tree = tree
        self.index = -1

    def add_child(self, index):
        self.children_index.add(index)

    def has_child(self) -> bool:
        return len(self.children_index) != 0

    def has_parent(self) -> bool:
        return self.parent_index is not None

    def set(self, key, value):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)

    def children(self) -> list:
        if not self.has_child():
            return []
        return [self.tree.nodes[self.level + 1][i] for i in self.children_index]

    '''
    搜寻特定的子节点
    '''

    def find_child(self, fuzzy: bool = False, **kwargs):
        if not self.has_child():
            return None
        for i in self.children_index:
            node = self.tree.nodes[self.level + 1][i]
            if fuzzy:
                if node.fuzzy_matching(**kwargs):
                    return node
            else:
                if node.satisfy(**kwargs):
                    return node
        return None

    def get_child(self, index):
        if index in self.children_index:
            return self.tree.nodes[self.level + 1][index]
        return None

    def parent(self):
        if not self.has_parent():
            return None
        return self.tree.nodes[self.level - 1][self.parent_index]

    """
    判断两个节点是否相同
    """

    def eql(self, node):
        return self.satisfy(**node.values)

    def satisfy(self, **node_values) -> bool:
        """
        根据传入的参数来判断该节点是否满足条件
        :param node_values: 需要比较的值
        :type node_values:
        :return: True 全部匹配 否则 False
        :rtype: bool
        """
        for k, v in node_values.items():
            if self.values[k] != v:
                return False
        return True

    def fuzzy_matching(self, **node_values) -> bool:
        """
        模糊匹配判断是否满足条件
        :param node_values:
        :type node_values:
        :return: True 只要满足一个，
        :rtype: bool
        """
        for k, v in node_values.items():
            if self.values[k] == v:
                return True
        return False

    @classmethod
    def new(cls, tree, parent_index=None, level=0, **node_values):
        __node = Node(tree, parent_index, level)
        for key, value in node_values.items(): __node.set(key, value)
        return __node
