import collections
import os
import flask
import datetime
import pymongo
import json

import route_handlers

george = flask.Blueprint('george', __name__, template_folder='templates')


george.add_url_rule('/',
    view_func=route_handlers.IndexHandler.as_view('users'))

george.add_url_rule('/colleges',
    view_func=route_handlers.CollegesHandler.as_view('colleges'))

george.add_url_rule('/submissions/<post_id>',
    view_func=route_handlers.SubmissionHandler.as_view('submissions'))

george.add_url_rule('/submissions/keyword/<keyword>/<int:page>',
    view_func=route_handlers.KeywordSubmissionHandler.as_view('submissionkeywords'))

george.add_url_rule('/wordsearch/<string:college>',
    view_func=route_handlers.SearchFrequencyHandler.as_view('wordsearch'), methods=['GET'])

george.add_url_rule('/scoresearch/<string:college>',
    view_func=route_handlers.SearchScoreHandler.as_view('scoresearch'), methods=['GET'])

george.add_url_rule('/sentimentsearch/<string:college>',
    view_func=route_handlers.SearchSentimentHandler.as_view('sentimentsearch'), methods=['GET'])

george.add_url_rule('/cokeywords',
    view_func=route_handlers.KeyWordTreeHandler.as_view('cokeywords'))

george.add_url_rule('/keyword/activity/<keyword>',
    view_func=route_handlers.KeywordActivityHandler.as_view('keywordactivity'))

george.add_url_rule('/sentiment/<keyword>',
    view_func=route_handlers.KeywordSentimentHandler.as_view('sentiment'))

george.add_url_rule('/topicgraph/<string:college>',
    view_func=route_handlers.TopicGraphHandler.as_view('topicgraph'))