from flask import Flask

application = Flask(__name__)
@application.route('/')
def index():
    return 'Coming soon..'

if __name__ == '__main__':
    application.debug = True
    application.run()
