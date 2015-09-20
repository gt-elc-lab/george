from analysis import keyword_extractor
class GraphGenerator(object):

    def __init__(self):
        return

    @staticmethod
    def create_graph(documents, threshold=0.15):
        tf = keyword_extractor.TFIDFHelper(get_text=lambda x: x.text)
        vectors = tf.perform_tfidf(documents)
        index_lookup = {doc._id: i for i, doc in enumerate(documents)}
        edges = []
        for i, v in enumerate(vectors):
            for j, k in enumerate(vectors):
                if i == j:
                    continue
                else:
                    angle = v.dot(k)
                    if angle >= threshold:
                        doc = documents[i]
                        other = documents[j]
                        # a = set(doc.keywords)
                        # b = set(other.keywords)
                        # intersection = a & b
                        # if intersection:
                        edge = {'source': index_lookup[doc._id],
                                    'target': index_lookup[other._id],
                                    'weight': len([])
                                    }
                        edges.append(edge)
        return edges



