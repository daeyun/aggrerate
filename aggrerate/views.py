from aggrerate import app
from flask import render_template

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/product/')
@app.route('/product/<productId>')
def enterReview(productId=None):
	return render_template('enterReview.html', productId=productId)

@app.route('/postReview/', methods=['POST'])
def postReview():
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
	return render_template('successfulReview.html')
