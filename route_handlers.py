import threading
import logging
from collections import defaultdict
from analysis.graph import GraphGenerator
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
            end = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            start = end - timedelta(days=3)
        query = {'college': college,
                 'keywords': {'$exists': True},
                 'created_utc': {'$gte': start, '$lte': end},
            }
        documents = map(models.Post.from_record, self.mongo_dao.post_collection.find(query))
        if documents:
            edge_list = GraphGenerator.keywords_intersection(documents)
            documents = [doc.to_json() for doc in documents]
            return {'nodes': documents, 'edges': edge_list}

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


class MultiThreadedExtraction(object):
    def __init__(self, colleges):
        self.colleges = colleges
    
    def start(self):
        q = Queue()
        for i in range(len(self.colleges)):
            logger.info('Spawned #{}'.format(i))
            client = MongoDao()
            worker = ExtractionWorker(client, q)
            worker.daemon = True
            worker.start()
        for college in self.colleges:
            logger.info('Queueing {}'.format(college['name']))
            q.put(college)
            
        q.join()

class ExtractionWorker(threading.Thread):
    def __init__(self, database_client, q, interval=timedelta(days=2)):
        threading.Thread.__init__(self)
        self.database_client = database_client
        self.q = q
        self.interval = interval
        return
    
    def run(self):
        while True:
            college_info = self.q.get()
            logging.info('Started {}'.format(college_info['name']))
            start_date = datetime.now()
            end_date = start_date - timedelta(days=3)
            self.extract(college_info, start_date, end_date)
            logger.info('Finished {} from {} to {}'.format(college_info['name'], start_date, end_date))
            self.q.task_done()
    
    def extract(self, college_info, start, end):
        match = {'$match': {
            'college' : college_info['name'], 
            '$or': [
                {'keywords': {'$exists': False}},
                {'created_utc': {'$gte': start, '$lte': end}},
            ]
        }}
        pipeline = [match]
        query_result = self.database_client.post_collection.aggregate(pipeline)
        documents = map(models.Post.from_record, query_result)
        corpus = [doc for doc in documents if doc.body]
        if corpus:
            keyword_extractor = KeyWordExtractor(corpus, text_accessor=lambda x: x.body)
            for index, document in enumerate(corpus):
                document.keywords = list(keyword_extractor.get_keywords(index))
                self.database_client.insert(document.to_record())