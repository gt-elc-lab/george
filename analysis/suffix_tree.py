from collections import deque

class SuffixTree(object):

    def __init__(self, root_word):
        self.root = Node(root_word)

    def insert(self, tokens):
        q = deque(tokens)
        self._traverse(self.root, q)

    def _traverse(self, node, q):
        if not q:
            return
        term = q.popleft()
        if term == node.term:
            self._traverse(node, q)
            return
        if term not in node.children:
            new_node = Node(term)
            node.add_child(new_node)
            self._traverse(new_node, q)
        else:
            self._traverse(node.get_child(term), q)

    def to_json(self):
        return self.root.to_json()

    def join_long_leaves(self):
        return

class Node(object):

    def __init__(self, term):
        self.term = term
        self.children = {}

    def add_child(self, new_node):
        self.children[new_node.term] = new_node
        return

    def get_child(self, term):
        return self.children[term]

    def get_size(self):
        return len(self.children)

    def to_json(self):
        as_json = {'name': self.term}
        if self.children:
            as_json['children'] = [child.to_json() for child in self.children.itervalues()]
        return as_json

    def __repr__(self):
        return '<Node %s>' % self.term


def main():
    sentences = ['if love be rough with you be rough with love',
                 'if love be blind love cannot hit the mark',
                 'if love be blind it best agrees with night']
    tree = SuffixTree('if')
    for s in sentences:
        tree.insert(s.split(' '))
    return tree.to_json()

if __name__ == '__main__':
    main()
