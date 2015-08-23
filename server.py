import os
from flask import Flask, render_template
from collection.dao import MongoDao

dao = MongoDao()
if not os.environ.get('PROD'):
	application = Flask(__name__, static_url_path='')
else:
	application = Flask(__name__)
	
@application.route('/')
def index():
    return render_template('index.html')

@application.route('/schools')
def show_colleges():
	return dao.get_colleges(self).to_json()

@application.route('/post/<post_id>')	
def show_post(post_id):
	return dao.get_post(self, post_id).to_json()
	
@application.route('/comment/<comment_id>')
def show_comment(comment_id):
	return dao.get_comment(self, comment_id).to_json()
	
@application.route('/comments/<post_id>')
def show_comments(post_id):
	return dao.get_post_comments(self, post_id).to_json()