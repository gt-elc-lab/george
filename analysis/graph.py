import keyword_extractor
import networkx as nx
import community
from networkx.readwrite import json_graph
from scipy.stats.stats import pearsonr


class GraphGenerator(object):

    def __init__(self):
        return

    @staticmethod
    def cosine_similarity(documents, threshold=0.2):
        tf = keyword_extractor.TFIDFHelper(get_text=lambda x: x.body)
        vectors = tf.perform_tfidf(documents)
        index_lookup = {doc._id: i for i, doc in enumerate(documents)}
        edges = []
        for i, v in enumerate(vectors):
            for j, k in enumerate(vectors):
                if i == j:
                    continue
                else:
                    coeff = pearsonr(v, k)[0]
                    # angle = pearsonr(v, k)
                    if abs(coeff) >= threshold:
                        doc = documents[i]
                        other = documents[j]
                        a = set(doc.keywords)
                        b = set(other.keywords)
                        intersection = a.intersection(b)
                        edge = {'source': index_lookup[doc._id],
                                    'target': index_lookup[other._id],
                                    'weight': len(intersection)
                                }
                        edges.append(edge)
        documents = [doc.to_json() for doc in documents]
        return {'nodes': documents, 'edges': edges}


    @staticmethod
    def keywords_intersection(documents, threshold=1):
        edges = []
        index_lookup = {doc._id: i for i, doc in enumerate(documents)}
        for i, doc in enumerate(documents):
            for other in documents[i:]:
                a = set(doc.keywords)
                b = set(other.keywords)
                intersection = a.intersection(b)
                if len(intersection) >= threshold:
                     edge = {'source': index_lookup[doc._id],
                             'target': index_lookup[other._id],
                             'weight': len(intersection)
                                }
                     edges.append(edge)
        documents = [doc.to_json() for doc in documents]
        return {'nodes': documents, 'edges': edges}

    @staticmethod
    def _with_networkx(documents, threshold=1):
        G = nx.Graph()
        G.add_nodes_from(documents)
        nodes = G.nodes()
        for i, node in enumerate(nodes):
            for other in nodes[i:]:
                a = set(node.keywords)
                b = set(other.keywords)
                intersection = a.intersection(b)
                if len(intersection) > threshold:
                    G.add_edge(node, other)
        partition_lookup = community.best_partition(G).iteritems()
        partitions = {node._id: value for node, value in partition_lookup}
        as_json = json_graph.node_link_data(G)
        frontend_compatable = {}
        frontend_compatable['nodes'] = [node['id'] for node in as_json['nodes']]
        for node in frontend_compatable['nodes']:
            node.partition = partitions[node._id]
        frontend_compatable['nodes'] = [node.to_json() for node in frontend_compatable['nodes']]
        frontend_compatable['edges'] = as_json['links']
        return frontend_compatable




