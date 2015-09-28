import os
import json
import flask
import datetime
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

@application.route('/todays_posts')
def send_todays_posts():
    college = flask.request.args.get('college')
    offset = flask.request.args.get('offset')
    handler = route_handlers.TodaysPostsHandler()
    today = get_today_from_offset(int(offset))
    return flask.jsonify({'posts': handler.execute(college, today)})

@application.route('/wordsearch')
def send_frequency_data():
    term = flask.request.args.get('term')
    colleges = flask.request.args.getlist('colleges')
    start = flask.request.args.get('start')
    end = flask.request.args.get('end')
    handler = route_handlers.TermFreqHandler()
    if start:
        start = datetime.datetime.utcfromtimestamp(start)
    if end:
        end = datetime.datetime.utcfromtimestamp(end)
    data = handler.execute(term, colleges, start, end)
    return flask.jsonify({'data': data})

def send_graph():
    college = flask.request.args.get('college')
    handler = route_handlers.GraphHandler()
    return flask.jsonify(handler.execute(college))

@application.route('/daily')
def send_activity():
    college = flask.request.args.get('college')
    offset = flask.request.args.get('offset')
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today += datetime.timedelta(minutes=int(offset))
    handler = route_handlers.DailyActivityHandler()
    return flask.jsonify(handler.execute(college, today))

@application.route('/trending')
def send_trending():
    college = flask.request.args.get('college')
    offset = flask.request.args.get('offset')
    days_ago = flask.request.args.get('days_ago')
    today = datetime.datetime.utcnow()
    today += datetime.timedelta(minutes=int(offset))
    today -= datetime.timedelta(days=int(days_ago))
    handler = route_handlers.TrendingKeyWordHandler()
    return flask.jsonify(data=handler.execute(college, today))

def get_today_from_offset(offset):
    today = datetime.datetime.utcnow().replace(hour=0,
        minute=0, second=0, microsecond=0)
    today += datetime.timedelta(minutes=int(offset))
    return today