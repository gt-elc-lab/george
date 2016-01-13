import networkx as nx
import community
from networkx.readwrite import json_graph
import json
import collections
import itertools

import keyword_extractor


class GraphGenerator(object):

    def __init__(self):
        return

    @staticmethod
    def build_topic_graph(documents):
        G = nx.Graph()
        # used to keep track of and increment the number of connections that
        # exist between any two keywords
        edge_weights = collections.Counter()

        keyword_frequencies = collections.Counter(
            [keyword for document in documents for keyword in document.keywords])
        for document in documents:
            for keyword in document.keywords:
                G.add_node(keyword, frequency=keyword_frequencies[keyword])
            # Its alright to just add the keywords without checking if it is
            # already in the graph. NetworkX doesn't modify the graph if that
            # is the case.
            G.add_nodes_from(document.keywords)
            edges = itertools.combinations(document.keywords, 2)
            for edge in edges:
                # unlike sets frozensets are hashable
                _set = frozenset(edge)
                edge_weights[_set] += 1
                x, y = edge
                if edge_weights[_set] > 1:
                    G.add_edge(x, y, weight=edge_weights[_set])
        for node in G.nodes():
            if keyword_frequencies[node] < 2:
                G.remove_node(node)
        return json_graph.node_link_data(G)

    @staticmethod
    def _with_networkx(documents, threshold=1):
        G = nx.Graph()
        G.add_nodes_from(documents)
        nodes = G.nodes()
        for i, node in enumerate(nodes):
            for other in nodes[i+1:]:
                a = set(node.keywords)
                b = set(other.keywords)
                intersection = a.intersection(b)
                if len(intersection) > threshold:
                    G.add_edge(node, other)
                    G[node][other]['weight'] = len(intersection)

        # remove any isolated vertices before we perform community detection
        orphans = []
        for node in G.nodes():
            if not G.neighbors(node):
                G.remove_node(node)
                orphans.append(node)
        partition_lookup = community.best_partition(G).iteritems()
        G.add_nodes_from(orphans)
        partitions = {node.r_id: value for node, value in partition_lookup}
        as_json = json_graph.node_link_data(G)
        frontend_compatable = {}
        frontend_compatable['nodes'] = [node['id'] for node in as_json['nodes']]
        for node in frontend_compatable['nodes']:
            if G.neighbors(node):
                node.partition = partitions[node.r_id]
        frontend_compatable['nodes'] = [json.loads(node.to_json()) for node in frontend_compatable['nodes']]
        for node in frontend_compatable['nodes']:
            if node['_id'] in partitions:
                node['partition'] = partitions[node['_id']]
        frontend_compatable['edges'] = as_json['links']
        return frontend_compatable




