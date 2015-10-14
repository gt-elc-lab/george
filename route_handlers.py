import threading
import logging
import pymongo
from collections import defaultdict
from analysis.graph import GraphGenerator
from analysis.suffix_tree import SuffixTree
from analysis.keyword_extractor import KeyWordExtractor
from collection.dao import MongoDao
from collection import models
from datetime import datetime, timedelta
from Queue import Queue

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


class RouteHandler(object):
    """ Abstract class for defining route handlers """

    def __init__(self):
        self.mongo_dao = MongoDao()

    def execute(self):
        raise NotImplementedError()


class TermFreqHandler(RouteHandler):

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
            end = datetime.utcnow()
            # get rid of the time field
            end = datetime(end.year, end.month, end.day)
            start = end - timedelta(days=30)
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
                period_start += timedelta(days=1)
            # Grab the actual values.
            for v in collision_buckets.itervalues():
                normalized.append(v)
            normalized.sort(key=lambda x: x['date'])
            final_form.append({'college': college, 'data': normalized})
        return final_form

    @staticmethod
    def to_datetime(_id):
        """
            Args:
                _id (dict):

            Returns
        """
        date = '{2}-{1}-{0}'.format(
                _id['year'], _id['month'], _id['day'])
        return datetime.strptime(date, '%d-%m-%Y')

    def transform(self, data):
        """

        Args:
            data (dict):
        """
        return {'college': data['_id']['college'],
                'total': data['total'],
                'date': self.to_datetime(data['_id'])}



class GraphHandler(RouteHandler):

    def execute(self, college, start=None, end=None):
        if not start or not end:
           start = datetime.utcnow() - timedelta(days=1)
        query = {'college': college,
                 'keywords': {'$exists': True},
                 'created_utc': {'$gte': start},
            }
        documents = map(models.Post.from_record, self.mongo_dao.post_collection.find(query))
        if documents:
            return GraphGenerator._with_networkx(documents)


class DailyActivitySummaryHandler(RouteHandler):

    def execute(self, college, today):
        match = {'$match': {
                'college': college,
                'created_utc': {'$gte': today}
        }}
        group = {'$group': {
            '_id': '$stype',
            'activity': {'$sum': 1},
        }}
        pipeline = [match, group]
        query_result = self.mongo_dao.post_collection.aggregate(pipeline)
        counts = defaultdict(int)
        for _type in query_result:
            counts[_type['_id']] = _type['activity']

        return {
            "activity": {
                "posts": counts["POST"],
                "comments": counts["COMMENT"]
            }
        }


class TodaysPostsHandler(RouteHandler):

    def execute(self, college, today):
        query = {
            'college': college,
            'created_utc': {'$gte': today},
            'stype': 'POST'
        }
        query_result = self.mongo_dao.post_collection.find(query)
        return map(lambda x: models.Post.from_record(x).to_json(), list(query_result))

class TrendingKeyWordHandler(RouteHandler):

    def __init__(self):
        self.mongo_dao = MongoDao()

    def execute(self, college,  date_limit):
        match = {'$match': {'college': college, 'created_utc': {'$gte': date_limit}}}
        project = {'$unwind': '$keywords'}
        group = {'$group': {'_id': '$keywords', 'total': {'$sum': 1}}}
        sort = {'$sort': {'total': -1}}
        limit = {'$limit': 10}
        pipeline = [match, project, group, sort, limit]
        query_result = self.mongo_dao.post_collection.aggregate(pipeline)
        format_output = lambda x: {'keyword': x['_id'], 'total': x['total']}
        return map(format_output, query_result)


class ActivityHandler(RouteHandler):

   def execute(self, college, threshold):
        query = {
           'college': college,
           'created_utc': {'$gte': threshold}
        }
        match ={'$match': query}
        project = {'$project': {
                'stype': 1,
                'y': {'$year': '$created_utc'},
                'm': {'$month': '$created_utc'},
                'd': {'$dayOfMonth': '$created_utc'},
                'h': {'$hour': '$created_utc'}
        }}
        group = {'$group': {
         '_id': {
             'year': '$y',
             'month': '$m',
             'day': '$d',
             'hour': '$h',
             'stype': '$stype'
         },
        'total': {'$sum': 1},
         }}
        sort = {'$sort':{
             '_id.year': -1,
             '_id.month': -1,
             '_id.day' : -1,
             '_id.hour': -1
             }}
        pipeline = [match, project, group, sort]
        return self.mongo_dao.post_collection.aggregate(pipeline)

class KeyWordTreeHandler(RouteHandler):

    def execute(self, college, keyword):
        match = {'$match': {'college': college, 'keywords': keyword}}
        project = {'$unwind': '$keywords'}
        group = {'$group': {'_id': '$keywords', 'total': {'$sum': 1}}}
        sort = {'$sort': {'total': -1}}
        limit = {'$limit': 10}
        pipeline = [match, project, group, sort, limit]
        query_result = self.mongo_dao.post_collection.aggregate(pipeline)
        formatted_output = map(lambda x: {'name': x['_id'], 'total': x['total']}, query_result)
        return {
            'name': keyword,
            'children': filter(lambda x: x['name'] != keyword, formatted_output)
        }

class WordTreeHandler(RouteHandler):

    def execute(self, college, term):
        last_week = datetime.utcnow() - timedelta(days=90)
        query = {'college': college,
                '$text': {'$search': term},
                'created_utc': {'$gte': last_week}}
        query_result = self.mongo_dao.post_collection.find(query)
        cleaned_text = SuffixTree.clean(term, [doc['body'] for doc in query_result])
        tree = SuffixTree(term)
        for sent in cleaned_text:
            tree.insert(sent)
        return tree.to_json()

class KeywordSubmissionHandler(RouteHandler):

    def execute(self, college, keyword, page=1):
        query = {'college': college,
                 'keywords': keyword}
        query_result = self.mongo_dao.post_collection.find(query).sort('created_utc', pymongo.ASCENDING).limit(10).skip((page - 1) * 10)
        return [models.Post.from_record(doc).to_json() for doc in query_result]

class KeywordActivityHandler(RouteHandler):

    def execute(self, keyword, college):
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_ago.replace(hour=0, minute=0, second=0)
        match = {'$match': {'college': college,
                            'keywords': keyword,
                            'created_utc': {'$gte': week_ago}}}
        project = {'$project': {
                'y': {'$year': '$created_utc'},
                'm': {'$month': '$created_utc'},
                'd': {'$dayOfMonth': '$created_utc'},
                'h': {'$hour': '$created_utc'}
        }}
        group = {'$group': {
         '_id': {
             'year': '$y',
             'month': '$m',
             'day': '$d',
         },
        'total': {'$sum': 1},
         }}
        sort = {'$sort':{
             '_id.year': -1,
             '_id.month': -1,
             '_id.day' : -1,
             }}
        pipeline = [match, project, group, sort]
        result = list(self.mongo_dao.post_collection.aggregate(pipeline))
        return list(result)