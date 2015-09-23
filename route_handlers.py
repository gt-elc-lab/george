import datetime
from collections import defaultdict
from analysis.graph import GraphGenerator
from collection.dao import MongoDao


class RouteHandler(object):
    """ Abstract class for defining route handlers """

    def __init__(self):
        return

    def execute(self):
        raise NotImplementedError()


class TermFreqHandler(RouteHandler):

    def __init__(self, dao=None):
        self.dao =  dao or MongoDao()

    def execute(self, term, colleges, start=None, end=None):
        """
        Args:
            term (str):
            colleges (list<str>):
            start (datetime.datetime):
            end (datetime.datetime):

        Returns:

        """
        if not start or not end:
            end = datetime.datetime.utcnow()
            # get rid of the time field
            end = datetime.datetime(end.year, end.month, end.day)
            start = end - datetime.timedelta(days=30)
        post_counts = self.dao.posts_term_frequency(term, colleges, start, end)
        formatted_data = map(self.transform, list(post_counts))
        buckets = defaultdict(list)
        # bucket the data by college
        [buckets[point['college']].append(point) for point in formatted_data]
        final_form = []
        for college, data in buckets.iteritems():
            collision_buckets = {}
            # First bucket the data point by day.
            for data_point in data:
                collision_buckets[data_point['date']] = data_point
            # Fill in any days that don't appear with a count of 0. This prevents the visualization
            # from being misleading on the front end.
            normalized = []
            period_start = start
            while period_start <= end:
                if period_start not in collision_buckets:
                    normalized.append({'total': 0, 'date': period_start, 'college': college})
                period_start += datetime.timedelta(days=1)
            # Grab the actual values.
            for v in collision_buckets.itervalues():
                normalized.append(v)
            normalized.sort(key=lambda x: x['date'])
            final_form.append({'college': college, 'data': normalized})
        return final_form

    def to_datetime(self, _id):
        """
            Args:
                _id (dict):

            Returns
        """
        date = '{2}-{1}-{0}'.format(
                _id['year'], _id['month'], _id['day'])
        return datetime.datetime.strptime(date, '%d-%m-%Y')

    def transform(self, data):
        """

        Args:
            data (dict):
        """
        return {'college': data['_id']['college'],
                'total': data['total'],
                'date': self.to_datetime(data['_id'])}



class GraphHandler(RouteHandler):

    def __init__(self, dao=None):
        self.dao = dao or MongoDao()

    def execute(self, college, start=None, end=None):
        if not start or not end:
            end = datetime.datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0)
            start = end - datetime.timedelta(days=3)
        query = {'college': college,
                     'keywords': {'$exists': True}}
        documents = self.dao.get_within_range(start, end, query)
        if documents:
            edge_list = GraphGenerator.cosine_similarity(documents)
            documents = [doc.to_json() for doc in documents]
            return {'nodes': documents, 'edges': edge_list}

