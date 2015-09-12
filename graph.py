class GraphGenerator(object):

    def __init__(self):
        return

    def create_graph(self, documents):
        nodes = [document._id for document in documents]
        edges = []
        for index, doc in enumerate(documents):
            for other in documents[index:]:
                a = set(doc.keywords)
                b = set(other.keywords)
                intersection = a & b
                if intersection:
                    edge = {'source': doc._id,
                            'target': other._id,
                            'weight': len(intersection)
                            }
                    edges.append(edge)
        return {'nodes': nodes, 'edges': edges}


    def serialize_to_json(self, graph):
        index_lookup = {doc._id: i for i, doc in enumerate(graph['nodes'])}
        for edge in graph['edges']:
            edge['source'] = index_lookup[edge.pop('source')]
            edge['target'] = index_lookup[edge.pop('target')]
        return {'nodes': graph['nodes'], 'edges': graph['edges']}


