from warnings import warn


class Node:
    def __init__(self, value):
        self.value = value
        self.next_node = None
        self.back_node = None


class LinkedList:
    def __init__(self, values: list):
        self.head_node = Node(values[0])
        back_node = self.head_node
        for v in values[1:]:
            temp_node = Node(v)
            back_node.next_node = temp_node
            temp_node.back_node = back_node
            back_node = temp_node
        self.last_node = back_node
        # 默认位置节点初始为头结点
        self.now_node = self.head_node

    # 初始化当前节点位置
    def inin_nownode(self, iflast=False):
        if iflast:
            self.now_node = self.last_node
        else:
            self.now_node = self.head_node

    def next(self, ifback=False) -> Node:
        if ifback:
            if self.now_node.back_node is None:
                warn('已是最前的节点,抛出None', DeprecationWarning)
                return None
            else:
                self.now_node = self.now_node.back_node
                return self.now_node
        else:
            if self.now_node.next_node is None:
                warn('已是最后的节点,抛出None', DeprecationWarning)
                return None
            else:
                self.now_node = self.now_node.next_node
                return self.now_node

    def delete_node(self):
        try:
            self.now_node.back_node.next_node = self.now_node.next_node
            b = True
        except:
            b = False
        try:
            self.now_node.next_node.back_node = self.now_node.back_node
        except:
            pass
        try:
            if b:
                self.now_node = self.now_node.back_node
            else:
                self.now_node = self.now_node.next_node
        except:
            warn('链表中已无节点', DeprecationWarning)

    # 在当前节点后添加新节点
    def add_node(self, value):
        node = Node(value)
        try:
            self.now_node.next_node.back_node = node
            node.next_node = self.now_node.next_node
        except:
            pass
        node.back_node = self.now_node
        self.now_node.next_node = node
        # 当前位置下移
        self.now_node = self.now_node.next_node

    def __len__(self):
        temp_node = self.head_node
        length = 0
        while temp_node:
            length += 1
            temp_node = temp_node.next_node
        return length
