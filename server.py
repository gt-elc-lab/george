import collections
import os
import flask
import datetime
import pymongo
import json

from collection.dao import MongoDao
from collection import models
import route_handlers

if os.environ.get('PROD'):
    application = flask.Flask(__name__)
else:
    application = flask.Flask(__name__, static_url_path='')


application.add_url_rule('/',
    view_func=route_handlers.IndexHandler.as_view('users'))

application.add_url_rule('/colleges',
    view_func=route_handlers.CollegesHandler.as_view('colleges'))

application.add_url_rule('/submissions/<post_id>',
    view_func=route_handlers.SubmissionHandler.as_view('submissions'))

application.add_url_rule('/submissions/keyword/<keyword>/<int:page>',
    view_func=route_handlers.KeywordSubmissionHandler.as_view('submissionkeywords'))

application.add_url_rule('/wordsearch/<string:college>',
    view_func=route_handlers.SearchFrequencyHandler.as_view('wordsearch'), methods=['GET'])

application.add_url_rule('/scoresearch/<string:college>',
    view_func=route_handlers.SearchFrequencyHandler.as_view('scoresearch'), methods=['GET'])

application.add_url_rule('/sentimentsearch/<string:college>',
    view_func=route_handlers.SearchSentimentHandler.as_view('sentimentsearch'), methods=['GET'])

application.add_url_rule('/cokeywords',
    view_func=route_handlers.KeyWordTreeHandler.as_view('cokeywords'))

application.add_url_rule('/keyword/activity/<keyword>',
    view_func=route_handlers.KeywordActivityHandler.as_view('keywordactivity'))

application.add_url_rule('/sentiment/<keyword>',
    view_func=route_handlers.KeywordSentimentHandler.as_view('sentiment'))

application.add_url_rule('/topicgraph/<string:college>',
    view_func=route_handlers.TopicGraphHandler.as_view('topicgraph'))