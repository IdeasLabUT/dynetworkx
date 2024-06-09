import operator

class Node:

    def __init__(self, low, high):
        self.low = low
        self.high = high
        self.max = high
        self.edges = []

        self.left = None
        self.right = None
        self.height = 0

    def inInterval(self, begin, end):
        return (self.low < end and self.high > begin) or self.low == begin

class IntervalTree:

    def __init__(self):
        self.nodes = {}
        self.root = None
        self.number_of_edges = 0
        self.begin = float("inf")
        self.end = float("-inf")

    def __getitem__(self, item):
        return self.slice(item.start, item.stop, self.root)

    def updateMax(self, node):

        if node.right and node.left:
            node.max = max(node.high, node.right.max, node.left.max)
        elif node.left:
            node.max = max(node.high, node.left.max)
        elif node.right:
            node.max = max(node.high, node.right.max)
        else:
            node.max = node.high

    def inOrder(self, root):

        if not root:
            return

        yield from self.inOrder(root.left)
        yield root
        yield from self.inOrder(root.right)

    def insert(self, root, node):
        if root is None:
            return node

        if node.low < root.low or (node.low == root.low and node.high < root.high):
            root.left = self.insert(root.left, node)
        else:
            root.right = self.insert(root.right, node)

        root.height = 1 + max(self.getHeight(root.left), self.getHeight(root.right))

        balance = self.getBalance(root)

        if balance > 1:
            if root.left.right == node:
                root.left = self.leftRotate(root.left)
            return self.rightRotate(root)

        elif balance < -1:
            if root.right.left == node:
                root.right = self.rightRotate(root.right)
            return self.leftRotate(root)

        self.updateMax(root)

        return root

    def discard(self, root, node):
        if root is node:
            if root.left:
                return root.left
            if root.right:
                return root.right
            return None

        if node.low < root.low or (node.low == root.low and node.high < root.high):
            root.left = self.discard(root.left, node)
        else:
            root.right = self.discard(root.right, node)

        root.height = 1 + max(self.getHeight(root.left), self.getHeight(root.right))

        balance = self.getBalance(root)

        if balance > 1:
            if root.left.right == node:
                root.left = self.leftRotate(root.left)
            return self.rightRotate(root)

        elif balance < -1:
            if root.right.left == node:
                root.right = self.rightRotate(root.right)
            return self.leftRotate(root)

        self.updateMax(root)

        return root

    def leftRotate(self, x):

        y = x.right
        t = y.left

        y.left = x
        x.right = t

        x.height = 1 + max(self.getHeight(x.left), self.getHeight(x.right))
        y.height = 1 + max(self.getHeight(y.left), self.getHeight(y.right))

        self.updateMax(x)
        self.updateMax(y)

        return y

    def rightRotate(self, x):
        y = x.left
        t = y.right

        y.right = x
        x.left = t

        x.height = 1 + max(self.getHeight(x.left), self.getHeight(x.right))
        y.height = 1 + max(self.getHeight(y.left), self.getHeight(y.right))

        self.updateMax(x)
        self.updateMax(y)

        return y

    def getHeight(self, node):

        if not node:
            return 0
        return node.height

    def getBalance(self, node):

        if not node:
            return 0
        return self.getHeight(node.left) - self.getHeight(node.right)

    def query(self, node, begin, end):
        if node.left and node.left.max >= begin:
            yield from self.query(node.left, begin, end)

        if node.inInterval(begin, end):
            yield node

        if node.right and node.low <= end and node.right.max >= begin:
            yield from self.query(node.right, begin, end)

    def add(self, edge):
        # edge = (u, v, begin, end)
        start = edge[2]
        end = edge[3]

        if (start, end) in self.nodes:
            node = self.nodes[(start, end)]
            node.edges.append(edge)
            self.number_of_edges += 1
            return

        node = Node(start, end)
        node.edges.append(edge)
        self.nodes[(start, end)] = node

        self.root = self.insert(self.root, node)
        self.number_of_edges += 1
        self.begin = min(self.begin, start)
        self.end = max(self.end, end)
        return

    def add_from(self, edges):
        for edge in edges:
            self.add(edge)
        return

    def remove(self, edge):
        # edge = (u, v, begin, end)
        start = edge[2]
        end = edge[3]

        node = self.nodes[(start, end)]
        if edge not in node.edges:
            return

        node.edges.remove(edge)
        self.number_of_edges -= 1
        if len(node.edges) == 0:
            self.discard(self.root, node)
        if self.begin == start:
            traversal_node = self.root
            while traversal_node.left != None:
                self.begin = traversal_node.left.low
                traversal_node = traversal_node.left
        if self.end == end:
            traversal_node = self.root
            while traversal_node.right != None:
                self.end = traversal_node.right.high
                traversal_node = traversal_node.right

        return

    def slice(self, interval_start, interval_end, root=None):
        if not root:
            root = self.root
            if not root:
                return []
        if not interval_start:
            interval_start = self.begin
        if not interval_end:
            interval_end = self.end

        for node in self.query(root, interval_start, interval_end):
            yield from node.edges

    def unique_timestamps(self, begin=None, end=None, inclusive=(True, True)):
        timestamps = set()

        if not begin:
            begin = self.begin
        if not end:
            end = self.end

        if inclusive[0]:
            begin_operator = operator.__le__
        else:
            begin_operator = operator.__lt__
        if inclusive[1]:
            end_operator = operator.__le__
        else:
            end_operator = operator.__lt__

        for n in self.query(self.root, begin, end):
            if n.low not in timestamps and begin_operator(begin, n.low) and end_operator(n.low, end):
                timestamps.add(n.low)
            if n.high not in timestamps and begin_operator(begin, n.high) and end_operator(n.high, end):
                timestamps.add(n.high)

        return sorted(timestamps)

    def unique_begin_timestamps(self, begin=None, end=None, inclusive=(True, True)):
        timestamps = set()

        if not begin:
            begin = self.begin
        if not end:
            end = self.end

        if inclusive[0]:
            begin_operator = operator.__le__
        else:
            begin_operator = operator.__lt__
        if inclusive[1]:
            end_operator = operator.__le__
        else:
            end_operator = operator.__lt__

        for n in self.query(self.root, begin, end):
            if n.low not in timestamps and begin_operator(begin, n.low) and end_operator(n.low, end):
                timestamps.add(n.low)

        return sorted(timestamps)

    def unique_end_timestamps(self, begin=None, end=None, inclusive=(True, True)):
        timestamps = set()

        if not begin:
            begin = self.begin
        if not end:
            end = self.end

        if inclusive[0]:
            begin_operator = operator.__le__
        else:
            begin_operator = operator.__lt__
        if inclusive[1]:
            end_operator = operator.__le__
        else:
            end_operator = operator.__lt__

        for n in self.query(self.root, begin, end):
            if n.high not in timestamps and begin_operator(begin, n.high) and end_operator(n.high, end):
                timestamps.add(n.high)

        return sorted(timestamps)
