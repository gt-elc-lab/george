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

class SearchFrequencyHandler(MethodView):

    def get(self, college):
        term = flask.request.args.get('term')
        date_filter = flask.request.args.get('date_filter')
        if not date_filter:
            date_filter = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        else:
            date_filter = json_to_date(date_filter)
        match = {'$match':
                     {'college': college,
                      'created': {'$gte': date_filter},
                      '$text': {'$search': term}}}
        group = {'$group': {
            '_id': { '$dateToString': { 'format': '%Y-%m-%d', 'date': '$created' }},
            'total': {'$sum': 1},
         }}
        mongo_dao = MongoDao()
        pipeline = [match, group]
        query_results = mongo_dao.db.submissions.aggregate(pipeline)
        return json.dumps(list(query_results))

class SearchScoreHandler(MethodView):

    def get(self, college):
        term = flask.request.args.get('term')
        date_filter = flask.request.args.get('date_filter')
        if not date_filter:
            date_filter = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        else:
            date_filter = json_to_date(date_filter)
        match = {'$match':
                     {'college': college,
                      'created': {'$gte': date_filter},
                      '$text': {'$search': term}}}
        group = {'$group': {
            '_id': { '$dateToString': { 'format': '%Y-%m-%d', 'date': '$created' }},
            'total': {'$avg': '$score'},
         }}
        mongo_dao = MongoDao()
        pipeline = [match, group]
        query_results = mongo_dao.db.submissions.aggregate(pipeline)
        return json.dumps(list(query_results))

class SearchSentimentHandler(MethodView):

    def get(self, college):
        term = flask.request.args.get('term')
        date_filter = flask.request.args.get('date_filter')
        if not date_filter:
            date_filter = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        else:
            date_filter = json_to_date(date_filter)
        match = {'$match':
                     {'college': college,
                      'created': {'$gte': date_filter},
                      '$text': {'$search': term}}}
        group = {'$group': {
            '_id': { '$dateToString': { 'format': '%Y-%m-%d', 'date': '$created' }},
            'positive': {'$avg': '$pos'},
            'neutral': {'$avg': '$neu'},
            'neg': {'$avg': '$neg'},
         }}
        mongo_dao = MongoDao()
        pipeline = [match, group]
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
                            'keywords.text': keyword,
                            'created': {'$gt': week_ago}
                            }
                }
        group = {'$group': {
            '_id': { '$dateToString': { 'format': '%Y-%m-%d', 'date': '$created' }},
            'total': {'$sum': 1}
        }}
        pipeline = [match, group]
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

class KeywordSentimentHandler(MethodView):

    def get(self, keyword):
        college = flask.request.args.get('college')
        week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        week_ago.replace(hour=0, minute=0, second=0)
        match = {'$match': {'college': college,
                            'keywords.text': keyword,
                            'created': {'$gt': week_ago}}}
        project = {'$project': {'keywords': 1, '_id': 0}}
        unwind = {'$unwind': '$keywords'}
        match_keyword = {'$match': {'keywords.text': keyword}}
        group = {'$group': {
            '_id': '$keywords.sentiment.type',
            'total': {'$sum': 1}
        }}
        # project_sentiment = {'$project': {'keywords.sentiment': 1}}
        # group = {'$group': {
        #     '_id': None,
        #     'pos': {'$avg': '$pos'},
        #     'neg': {'$avg': '$neg'},
        #     'neu': {'$avg': '$neu'}
        # }}
        pipeline = [match, project, unwind, match_keyword, group]
        result = models.Submission.objects.aggregate(*pipeline)
        data = list(result)
        total = sum([x['total'] for x in data])
        response = { k['_id'] : k['total'] / float(total) for k in data}
        return flask.json.dumps(response)


def json_to_date(date_string):
    return datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")

def get_today_from_offset(offset):
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today += datetime.timedelta(minutes=int(offset))
    return today