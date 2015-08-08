import os
from flask import Flask, render_template

if not os.environ.get('PROD'):
	application = Flask(__name__, static_url_path='')
else:
	application = Flask(__name__)
	
@application.route('/')
def index():
    return render_template('index.html')


