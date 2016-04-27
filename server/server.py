import collections
import os
import flask
from flask.ext.cors import CORS
import datetime
import pymongo
import json

import route_handlers

application = flask.Flask(__name__)
CORS(application)

api = flask.Blueprint('api', __name__,template_folder='templates')

api.add_url_rule('/',
    view_func=route_handlers.IndexHandler.as_view('users'))

api.add_url_rule('/colleges',
    view_func=route_handlers.CollegesHandler.as_view('colleges'))

api.add_url_rule('/submissions/<post_id>',
    view_func=route_handlers.SubmissionHandler.as_view('submissions'))

api.add_url_rule('/submissions/keyword/<keyword>/<int:page>',
    view_func=route_handlers.KeywordSubmissionHandler.as_view('submissionkeywords'))

api.add_url_rule('/wordsearch/<string:college>',
    view_func=route_handlers.SearchFrequencyHandler.as_view('wordsearch'), methods=['GET'])

api.add_url_rule('/scoresearch/<string:college>',
    view_func=route_handlers.SearchScoreHandler.as_view('scoresearch'), methods=['GET'])

api.add_url_rule('/sentimentsearch/<string:college>',
    view_func=route_handlers.SearchSentimentHandler.as_view('sentimentsearch'), methods=['GET'])

api.add_url_rule('/cokeywords',
    view_func=route_handlers.KeyWordTreeHandler.as_view('cokeywords'))

api.add_url_rule('/keyword/activity/<keyword>',
    view_func=route_handlers.KeywordActivityHandler.as_view('keywordactivity'))

api.add_url_rule('/sentiment/<keyword>',
    view_func=route_handlers.KeywordSentimentHandler.as_view('sentiment'))

api.add_url_rule('/topicgraph/<string:college>',
    view_func=route_handlers.TopicGraphHandler.as_view('topicgraph'))

application.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    application.debug = True
    application.run()