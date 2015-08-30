import os
import json
import flask
from collection.dao import MongoDao

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