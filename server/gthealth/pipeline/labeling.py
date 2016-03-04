import flask

from gthealth import model

app = flask.Blueprint('label', __name__, template_folder='templates')

@app.route('/', defaults={'page': 0})
@app.route('/<int:page>')
def index(page):
    sample = model.Sample.objects(subreddit='gatech')[page:].first()
    flask.session['page'] = page + 1
    return flask.render_template('sample.html', sample=sample)

@app.route('/label/<string:r_id>', methods=['GET'])
def label(r_id):
    sample = model.Sample.objects.get(r_id=r_id)
    if flask.request.args.get('label') == 'True':
        sample.label = True
    else:
        sample.label = False
    sample.save()
    return flask.redirect(flask.url_for('label.index', page=flask.session['page']))