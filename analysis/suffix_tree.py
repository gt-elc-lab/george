
from nltk import tokenize
from collections import deque

class SuffixTree(object):

    def __init__(self, root_word):
        self.root = Node(root_word)

    def insert(self, tokens):
        q = deque(tokens)
        self._traverse(self.root, q)

    def _traverse(self, node, q):
        node.total += 1
        if not q:
            return
        term = q.popleft()
        if term == node.term:
            self._traverse(node, q)
            return
        if term not in node.children:
            child = Node(term)
            node.add_child(child)
            self._traverse(child, q)
        else:
            self._traverse(node.get_child(term), q)

    def to_json(self):
        self.root.collapse()
        return self.root.to_json()

    @staticmethod
    def clean(term, documents):
        tokenized_sents = [tokenize.word_tokenize(sentence)
                           for document in documents
                           for sentence in tokenize.sent_tokenize(document.lower())]
        contain_term = [sent for sent in tokenized_sents if term in sent]
        return [sent[sent.index(term):] for sent in contain_term]

class Node(object):

    def __init__(self, term):
        self.term = term
        self.children = {}
        self.total = 0

    def add_child(self, new_node):
        self.children[new_node.term] = new_node
        return

    def get_child(self, term):
        return self.children[term]

    def get_size(self):
        return len(self.children)

    def to_json(self):
        as_json = {'name': self.term, 'total': self.total}
        if self.children:
            as_json['children'] = [child.to_json() for child in self.children.itervalues()]
        return as_json

    def collapse(self):
        if len(self.children) == 1:
            child = list(self.children.itervalues())[0]
            self.term = self.term + ' ' + child.term
            self.children.update(child.children)
            self.children.pop(child.term)
            self.collapse()
        for child in self.children.itervalues():
            child.collapse()
        return


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
