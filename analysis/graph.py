import networkx as nx
import community
from networkx.readwrite import json_graph
import json

import keyword_extractor


class GraphGenerator(object):

    def __init__(self):
        return

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




