from aggrerate import app
from flask import render_template, request
import flask
from aggrerate.web_scripts import loginCode

def cookieParams(request):
	params = {"username": request.cookies.get('username')}
	return params

@app.route('/')
def main():
	params = cookieParams(request)
	# params = {'username': request.cookies.get['username']}
	return render_template('main.html', **params)

@app.route('/about')
def about():
	params = cookieParams(request)
	return render_template('about.html', **params)

@app.route('/reviews')
def reviews():
	params = cookieParams(request)
	return render_template('reviews.html', **params)

@app.route('/login')
def login():
	params = cookieParams(request)
	return render_template('login.html', **params)
	
@app.route('/attemptLogin')
def attemptLogin():
	params = cookieParams(request)
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
	params = cookieParams(request)
	return render_template('enterReview.html', productId=productId, **params)

@app.route('/postReview/', methods=['POST'])
def postReview():
	params = cookieParams(request)
	db = MySQLdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
		user='matt',
		passwd='matt',
		db='aggrerate')
	cur = db.cursor()
	dtstr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
	# dtstr = str(dt.year)+"-"+str(dt.month)+"-"+str(dt.day)+" "+str(dt.hour)+":"+str(dt.minute)+":"+str(dt.second)
	query = 'INSERT INTO reviews VALUES (%s, "%s", %s, %s, "%s")' % (8, dtstr, request.form['score'], request.form['productId'], request.form['reviewText'])
	print query
	cur.execute(query)
	db.commit()
	return render_template('successfulReview.html', **params)
