import keyword_extractor
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
        return edges


    @staticmethod
    def keywords_intersection(documents, threshold=1):
        edges = []
        index_lookup = {doc._id: i for i, doc in enumerate(documents)}
        for i, doc in enumerate(documents):
            for other in documents[i:]:
                a = set(doc.keywords)
                b = set(other.keywords)
                intersection = a.intersection(b)
                if len(intersection) > threshold:
                     edge = {'source': index_lookup[doc._id],
                             'target': index_lookup[other._id],
                             'weight': len(intersection)
                                }
                     edges.append(edge)
        return edges




