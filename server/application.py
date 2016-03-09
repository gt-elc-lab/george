import flask
from flask.ext.cors import CORS
from george.server import george
from gthealth.server import gthealth
from gthealth.pipeline.labeling import label_server

application = flask.Flask(__name__)
CORS(application)
application.register_blueprint(george, url_prefix='/george')
application.register_blueprint(gthealth, url_prefix='/gthealth')
application.register_blueprint(label_server, url_prefix='/label')
application.secret_key = 'super secret'




if __name__ == '__main__':
    application.debug = True
    application.run()