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

class KeywordActivityHandler(MethodView):

    def get(self, keyword):
        college = flask.request.args.get('college')

        week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        week_ago.replace(hour=0, minute=0, second=0)
        match = {'$match': {'college': college,
                            'keywords': keyword,
                            'created': {'$gt': week_ago}}}
        project = {'$project': {
                'y': {'$year': '$created'},
                'm': {'$month': '$created'},
                'd': {'$dayOfMonth': '$created'},
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
        result = models.Submission.objects.aggregate(*pipeline)
        return flask.json.dumps(list(result))

class TopicGraphHandler(MethodView):

    def get(self, college):
        date_filter = flask.request.args.get('date_filter')
        if not date_filter:
            date_filter = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        else:
            date_filter = json_to_date(date_filter)
        submissions = models.Submission.objects(college=college, created__gte=date_filter)
        graph = GraphGenerator.build_topic_graph(submissions)
        return json.dumps(graph)

class SentimentTableHandler(MethodView):

    def get(self, keyword):
        college = flask.request.args.get('college')

        week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        week_ago.replace(hour=0, minute=0, second=0)
        match = {'$match': {'college': college,
                            'keywords': keyword,
                            'created': {'$gt': week_ago}}}
        project = {'$project': {
                'y': {'$year': '$created'},
                'm': {'$month': '$created'},
                'd': {'$dayOfMonth': '$created'},
        }}
        group = {'$group': {
         '_id': {
             'year': '$y',
             'month': '$m',
             'day': '$d',
         },
        'pos': {'$avg': '$pos'},
        'neg': {'$avg': '$neg'},
        'neu': {'$avg': '$neu'}
         }}
        sort = {'$sort':{
             '_id.year': -1,
             '_id.month': -1,
             '_id.day' : -1,
             }}
        pipeline = [match, project, group, sort]
        result = models.Submission.objects.aggregate(*pipeline)
        return flask.json.dumps(list(result))


def json_to_date(date_string):
    return datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")

def get_today_from_offset(offset):
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today += datetime.timedelta(minutes=int(offset))
    return today