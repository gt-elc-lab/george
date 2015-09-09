import datetime
from collections import defaultdict

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
            end = datetime.datetime.today()
            # get rid of the time field
            end = datetime.datetime(end.year, end.month, end.day)
            start = end - datetime.timedelta(days=30)
        post_counts = self.dao.posts_term_frequency(term, colleges, start, end)
        comment_counts = self.dao.comments_term_frequency(
            term, colleges, start, end)
        formatted_data = map(self.transform, list(post_counts) + list(comment_counts))
        buckets = defaultdict(list)
        # bucket the data by college
        [buckets[point['college']].append(point) for point in formatted_data]
        final_form = []
        for college, data in buckets.iteritems():
            collision_buckets = defaultdict(list)
            # First bucket the data point by day. Then reduce the array to a single value.
            # This is to ensure that counts for posts and comments are summed.
            for data_point in data:
                collision_buckets[data_point['date']].append(data_point)
            for date, values in collision_buckets.iteritems():
                collision_buckets[date] = reduce(
                    lambda x, y: {'total': x['total'] + y['total'], 'date': x['date'], 'college': x['college']}, values)
            # Fill in any days that don't appear with a count of 0. This prevents the visualization
            # from being misleading on the front end.
            normalized = []
            period_start = start
            while period_start <= end:
                if period_start not in collision_buckets:
                    normalized.append({'total': 0, 'date': period_start})
                period_start += datetime.timedelta(days=1)
            # Grab the actual values.
            normalized += [v for v in collision_buckets.itervalues()]
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