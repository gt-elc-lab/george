import threading
import logging
import pymongo
import datetime
import flask
import json
from collections import defaultdict
from flask.views import MethodView

from analysis.graph import GraphGenerator
from analysis.suffix_tree import SuffixTree
from collection.dao import MongoDao
from collection import models
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

class IndexHandler(MethodView):
    
    def get(self):
        return flask.render_template('index.html')

        
class CollegesHandler(MethodView):
    
    def get(self):
        colleges = models.Submission.objects.distinct('college')
        colleges.sort()
        return flask.jsonify({'colleges': colleges})
        
        
class SubmissionHandler(MethodView):
    
    def get(self, post_id):
        return flask.jsonify(data=models.Submission.objects.get(r_id=post_id).to_json())


class KeywordSubmissionHandler(MethodView):

    def get(self, keyword, page=1):
        college = flask.request.args.get('college')
        mongo_dao = MongoDao()
        query = {'college': college,
                 'keywords': keyword}
        query_result = mongo_dao.post_collection.find(query).sort('created_utc', pymongo.ASCENDING).limit(10).skip((page - 1) * 10)
        data = []
        for doc in query_result:
            data.append(models.Post.from_record(doc).to_json())
        #data = [models.Post.from_json(doc).to_json() for doc in query_result]
        return flask.jsonify(data=data)


class TodaysPostsHandler(MethodView):

    def get(self):
        college = flask.request.args.get('college')
        offset = flask.request.args.get('offset')
        today = get_today_from_offset(int(offset))
        mongo_dao = MongoDao()
        query = {
            'college': college,
            'created_utc': {'$gte': today},
            'stype': 'POST'
        }
        query_result = mongo_dao.post_collection.find(query)
        data = map(lambda x: models.Post.from_record(x).to_json(), list(query_result))
        return flask.jsonify({'posts':data})


class TermFreqHandler(MethodView):

    def get(self):
        term = flask.request.args.get('term')
        colleges = flask.request.args.getlist('colleges')
        start = flask.request.args.get('start')
        end = flask.request.args.get('end')
        if not start or not end:
            end = datetime.datetime.utcnow()
            # get rid of the time field
            end = datetime.datetime(end.year, end.month, end.day)
            start = end - datetime.timedelta(days=30)
        mongo_dao = MongoDao()
        post_counts = mongo_dao.posts_term_frequency(term, colleges, start, end)
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
        return flask.jsonify({'data': final_form})

    @staticmethod
    def to_datetime(_id):
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


class GraphHandler(MethodView):

    def get(self, college):
        start = flask.request.args.get('start')
        end = flask.request.args.get('end')
        if not start or not end:
           start = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        documents = models.Submission.objects(college=college, keywords__exists=True, created__gte=start)
        if documents:
            data = GraphGenerator._with_networkx(documents)
            return flask.jsonify(data)


class DailyActivitySummaryHandler(MethodView):

    def get(self):
        college = flask.request.args.get('college')
        offset = flask.request.args.get('offset')
        today = get_today_from_offset(offset)
        
        mongo_dao = MongoDao()
        match = {'$match': {
                'college': college,
                'created_utc': {'$gte': today}
        }}
        group = {'$group': {
            '_id': '$stype',
            'activity': {'$sum': 1},
        }}
        pipeline = [match, group]
        query_result = mongo_dao.post_collection.aggregate(pipeline)
        counts = defaultdict(int)
        for _type in query_result:
            counts[_type['_id']] = _type['activity']

        data = {
            "activity": {
                "posts": counts["POST"],
                "comments": counts["COMMENT"]
            }
        }
        return flask.jsonify(data)


class ActivityHandler(MethodView):

   def get(self):
        college = flask.request.args.get('college')
        offset = flask.request.args.get('offset')
        desired_date = get_today_from_offset(int(offset))

        mongo_dao = MongoDao()
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
        data = mongo_dao.post_collection.aggregate(pipeline)
        buckets = collections.defaultdict(list)
        for item in data:
            date = datetime.datetime(year=item['_id']['year'],
                                     month=item['_id']['month'], day=item['_id']['day'], hour=item['_id']['hour'])
            date += datetime.timedelta(minutes=int(offset))
            buckets[date].append(item)
        formatted_data = []
        for k, v in buckets.iteritems():
            data_point = {'date': str(k), 'comment': 0, 'post': 0}
            for submission in v:
                stype = submission['_id']['stype'].lower()
                data_point[stype] += submission['total']
            formatted_data.append(data_point)
        return flask.jsonify(data=formatted_data)

        
class TrendingKeyWordHandler(MethodView):

    def get(self):
        college = flask.request.args.get('college')
        offset = flask.request.args.get('offset')
        days_ago = flask.request.args.get('days_ago')
        today = datetime.datetime.utcnow()
        today += datetime.timedelta(minutes=int(offset))
        today -= datetime.timedelta(days=int(days_ago))
        match = {'$match': {'college': college, 'created': {'$gte': date_limit}}}
        project = {'$unwind': '$keywords'}
        group = {'$group': {'_id': '$keywords', 'total': {'$sum': 1}}}
        sort = {'$sort': {'total': -1}}
        limit = {'$limit': 10}
        query_result = models.Submission.objects.aggregate(match, project, group, sort, limit)
        format_output = lambda x: {'keyword': x['_id'], 'total': x['total']}
        data = map(format_output, query_result)
        return flask.jsonify(data=data)

        
class KeyWordTreeHandler(MethodView):

    def get(self):
        college = flask.request.args.get('college')
        keyword = flask.request.args.get('keyword')
        match = {'$match': {'college': college, 'keywords': keyword}}
        project = {'$unwind': '$keywords'}
        group = {'$group': {'_id': '$keywords', 'total': {'$sum': 1}}}
        sort = {'$sort': {'total': -1}}
        limit = {'$limit': 10}
        pipeline = [match, project, group, sort, limit]
        query_result = models.Submission.objects.aggregate(*pipeline)
        formatted_output = map(lambda x: {'name': x['_id'], 'total': x['total']}, query_result)
        data = {
            'name': keyword,
            'children': filter(lambda x: x['name'] != keyword, formatted_output)
        }
        return flask.jsonify(data=data)


class WordTreeHandler(MethodView):

    def get(self):
        college = flask.request.args.get('college')
        term = flask.request.args.get('term')
        last_week = datetime.datetime.utcnow() - datetime.timedelta(days=90)
        
        mongo_dao = MongoDao()
        query = {'college': college,
                '$text': {'$search': term},
                'created_utc': {'$gte': last_week}}
        query_result = mongo_dao.post_collection.find(query)
        cleaned_text = SuffixTree.clean(term, [doc['body'] for doc in query_result])
        tree = SuffixTree(term)
        for sent in cleaned_text:
            tree.insert(sent)
        return flask.jsonify(data=tree.to_json())
        
        
class KeywordActivityHandler(MethodView):

    def get(self, keyword):
        college = flask.request.args.get('college')
        
        mongo_dao = MongoDao()
        week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
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
        result = list(mongo_dao.post_collection.aggregate(pipeline))
        return flask.json.dumps(list(result))

        
class WordCountHandler(MethodView):

    def get(self, college):
        word_count_db = pymongo.MongoClient('mongodb://elc:yak@ds047652.mongolab.com:47652/redditdump')['redditdump']['wordcount']
        query = {'_id.college': college}
        word_counts = word_count_db.find(query).sort('value', pymongo.DESCENDING).limit(1000)
        return flask.render_template('wordcount.html', college=college, data=word_counts)
        
        
class BigQuerySubredditsHandler(MethodView):

    def get(self):
        db = pymongo.MongoClient('mongodb://45.55.235.216:27017/')['reddit']
        subreddits = list(db.data_dump.distinct('subreddit'))
        subreddits.sort()
        return json.dumps(subreddits)
        

class BigQueryScoreHandler(MethodView):

    def get(self):
        subreddits = flask.request.args.getlist('subreddits')
        db = pymongo.MongoClient('mongodb://45.55.235.216:27017/')['reddit']

        match = {'$match': {'subreddit': {'$in': subreddits}}}
        group = {'$group': {
             '_id': {
                 'year': {'$year': '$created_utc'},
                 'month': {'$month': '$created_utc'},
                 'subreddit': '$subreddit'
                },
            'average_score': {'$avg': '$score'},
            'total_activity': {'$sum': 1}
            }
        }
        flatten = {'$project': {
                '_id': 0,
                'year': '$_id.year',
                'month': '$_id.month',
                'subreddit': '$_id.subreddit',
                'average_score': '$average_score',
                'total_activity': '$total_activity'
            }
        }
        query_result = db.data_dump.aggregate([match, group, flatten])
        buckets = defaultdict(list)
        for doc in query_result:
            buckets[doc['subreddit']].append(doc)
        response = [{'subreddit': k, 'data': v} for k, v in buckets.iteritems()]
        return json.dumps(response)
        
def get_today_from_offset(offset):
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today += datetime.timedelta(minutes=int(offset))
    return today