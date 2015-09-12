import os
import json
import flask
from collection.dao import MongoDao
import route_handlers

if os.environ.get('PROD'):
    application = flask.Flask(__name__)
else:
    application = flask.Flask(__name__, static_url_path='')

dao = MongoDao()

@application.route('/')
def index():
    return flask.render_template('index.html')

@application.route('/colleges')
def send_colleges():
    return flask.jsonify({'colleges': dao.get_colleges()})

@application.route('/post/<post_id>')
def send_post(post_id):
    return flask.jsonify(dao.get_post(str(post_id)).to_json())

@application.route('/comment/<comment_id>')
def send_comment(comment_id):
    return flask.jsonify(dao.get_comment(str(comment_id)).to_json())

@application.route('/comments/<post_id>')
def send_comments(post_id):
	comments = [comment_model.to_json()
				for comment_model in dao.get_post_comments(str(post_id))]
	return flask.jsonify({'comments': comments})

@application.route('/wordsearch')
def send_frequency_data():
    term = flask.request.args.get('term')
    colleges = flask.request.args.getlist('colleges')
    start = flask.request.args.get('start')
    end = flask.request.args.get('end')
    handler = route_handlers.TermFreqHandler()
    data = handler.execute(term, colleges, start, end)
    return flask.jsonify({'data': data})

@application.route('/trending')
def send_graph():
    colleges = flask.request.args('college')
    date = flask.request.args('date')
    return
