from aggrerate import app
from flask import render_template, request
import flask, MySQLdb, time
from aggrerate.web_scripts import loginCode

def cookie_params(request):
    params = {"username": request.cookies.get('username')}
    return params

@app.route('/')
def main():
    params = cookie_params(request)
    # params = {'username': request.cookies.get['username']}
    return render_template('main.html', **params)

@app.route('/about')
def about():
    params = cookie_params(request)
    return render_template('about.html', **params)

@app.route('/reviews')
def reviews():
    params = cookie_params(request)
    return render_template('reviews.html', **params)

@app.route('/login')
def login():
    params = cookie_params(request)
    return render_template('login.html', **params)
    
@app.route('/attemptLogin')
def attemptLogin():
    params = cookie_params(request)
    print request.args.keys()
    if 'username' in flask.request.args.keys() and 'password' in request.args.keys():
        if loginCode.validateUser(request.args['username'], request.args['password']):
        # if loginCode.validateUser('a', 'a'):
            resp = flask.make_response(render_template('main.html', username=flask.request.args['username']))
            resp.set_cookie('username', flask.request.args['username'])
            return resp
    return flask.redirect(flask.url_for('login'))

@app.route('/product/')
@app.route('/product/<productId>')
def enterReview(productId=None):
    params = cookie_params(request)
    return render_template('enterReview.html', productId=productId, **params)

@app.route('/postReview/', methods=['POST'])
def postReview():
    params = cookie_params(request)
    username = request.cookies.get('username')

    db = MySQLdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='matt',
        passwd='matt',
        db='aggrerate')
    cur = db.cursor()
    dtstr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    review_query = 'INSERT INTO reviews VALUES (%s, %s, %s, %s, %s)'
    user_review_query = 'INSERT INTO user_reviews VALUES (%s, LAST_INSERT_ID(), %s)'
    cur.execute(review_query, (None, dtstr, request.form['score'], request.form['productId'], request.form['reviewText']))
    db.query('SELECT id FROM users WHERE name = "%s"' % username)
    user_id = db.store_result().fetch_row()
    print "Gotten ID: ", user_id
    user_id = user_id[0][0]
    cur.execute(user_review_query, (None, user_id))
    db.commit()
    return render_template('successfulReview.html', **params)
