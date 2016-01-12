import threading
import logging
import pymongo
import datetime
import flask
import json
import collections
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


class WordSearchView(MethodView):

    def get(self, college):
        term = flask.request.args.get('term')
        offset = int(flask.request.args.get('offset'))
        days_ago = int(flask.request.args.get("elapsedTime"))
        end = datetime.datetime.utcnow() + datetime.timedelta(minutes=offset)

        start = end - datetime.timedelta(days=days_ago)
        match = {'$match':
                     {'college': college,
                      'created': {'$gte': start, '$lte': end},
                      '$text': {'$search': term}}}
        project = {'$project': {
                'y': {'$year': '$created'},
                'm': {'$month': '$created'},
                'd': {'$dayOfMonth': '$created'}
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
             '_id.day' : -1
             }}
        mongo_dao = MongoDao()
        pipeline = [match, project, group, sort]
        query_results = mongo_dao.db.submissions.aggregate(pipeline)
        return json.dumps(list(query_results))


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
        match = {'$match': {'college': college, 'created': {'$gte': today}}}
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

    def get(self, college, term):
        term = term.lower()
        last_week = datetime.datetime.utcnow() - datetime.timedelta(days=90)
        query = {'college': college,
                '$text': {'$search': term},
                'created': {'$gte': last_week}}
        query_result = models.Submission.objects(__raw__=query)
        cleaned_text = SuffixTree.clean(term, [doc.get_content() for doc in query_result])
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

class TopRatedView(MethodView):

    def get(self, college):
        term = flask.request.args.get('term')
        date = datetime.datetime.strptime(flask.request.args.get('date'), '%a %b %d %Y')
        date += datetime.timedelta(minutes=int(flask.request.args.get('offset')))
        end_of_day = date + datetime.timedelta(days=1)
        query = {
            'college': college,
            'created': {'$gte': date, '$lte': end_of_day},
            '$text': {'$search': term}
        }
        highest_scoring = models.Submission.objects(__raw__=query).order_by('-score').limit(1).first()
        return highest_scoring.to_json()

class TopicGraphHandler(MethodView):

    def get(self, college):
        date_filter = flask.request.args.get('date_filter')
        if not date_filter:
            date_filter = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        else:
            date_filter = json_to_date(date_filter)
        submissions = models.Submission.objects(college=college, created__gte=date_filter)
        graph = GraphGenerator.build_topic_graph(submissions)
        return flask.jsonify(data=graph)


def json_to_date(date_string):
    return datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")

def get_today_from_offset(offset):
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today += datetime.timedelta(minutes=int(offset))
    return today