import flask
from flask.ext.cors import CORS
from george.server import george
from gthealth.server import gthealth

application = flask.Flask(__name__)
CORS(application)
application.register_blueprint(george, url_prefix='/george')
application.register_blueprint(gthealth, url_prefix='/gthealth')

if __name__ == '__main__':
    application.debug = True
    application.run()