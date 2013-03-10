import MySQLdb as mdb

from flask import render_template, request
import flask, time

from aggrerate import app
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

@app.route('/users/<username>')
def userPage(username=None):
    params = cookie_params(request)
    db = mdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='jeff',
        passwd='jeff',
        db='aggrerate')
    cur = db.cursor(mdb.cursors.DictCursor)
    cur.execute("""
    SELECT
        reviews.date AS date,
        reviews.score AS score,
        reviews.product_id AS prod_id,
        reviews.body_text AS text,
        reviews.id AS rev_id
    FROM
        users
    INNER JOIN user_reviews
    INNER JOIN reviews
    ON
        users.id = user_reviews.user_id
    AND user_reviews.review_id = reviews.id;
    ORDER BY
        reviews.datetime DESC
    """)
    products = cur.fetchall()
    params['reviews'] = []
    for product in products:
        params['reviews'].append(product)
    params['dispUsername'] = username
    return render_template('user.html', **params)

@app.route('/deleteReview', methods=["POST"])
def deleteReview():
    params = cookie_params(request)
    id_to_delete = request.form['review']
    db = mdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='jeff',
        passwd='jeff',
        db='aggrerate')
    cur = db.cursor(mdb.cursors.DictCursor)
    cur.execute("""
    DELETE FROM
        reviews
    WHERE
        id = %s
    """, (id_to_delete))
    cur.execute("""
    DELETE FROM
        user_reviews
    WHERE
        review_id = %s
    """, (id_to_delete))
    db.commit()
    return flask.redirect(flask.url_for('about'))
    # Make this work, dunno how to redirect to variable things
    # return flask.redirect(flask.url_for('users', username=params['username']))

@app.route('/login')
def login():
    params = cookie_params(request)
    return render_template('login.html', **params)

@app.route('/attemptLogin')
def attemptLogin():
    params = cookie_params(request)
    if 'username' in flask.request.args.keys() and 'password' in request.args.keys():
        if loginCode.validateUser(request.args['username'], request.args['password']):
            resp = flask.make_response(render_template('main.html', username=flask.request.args['username']))
            resp.set_cookie('username', flask.request.args['username'])
            return resp
    return flask.redirect(flask.url_for('login'))

@app.route('/logout')
def logout():
    resp = flask.make_response(render_template('main.html'))
    resp.set_cookie('username', '', expires=0)
    return resp

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/attemptSignup', methods=["POST"])
def attemptSignup():
    if not ('username' in request.form.keys() and 'password' in request.form.keys() and request.form['username'] and request.form['password']):
        return flask.redirect(flask.url_for('signup', retry=True))
    # It's time to add the user's new username and password to the table
    if loginCode.addUser(request.form['username'], request.form['password']):
        return flask.redirect(flask.url_for('login'))
    else:
        return flask.redirect(flask.url_for('signup', retry=True))

@app.route('/products/')
def products_list():
    params = cookie_params(request)

    db = mdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='jeff',
        passwd='jeff',
        db='aggrerate')
    cur = db.cursor(mdb.cursors.DictCursor)
    cur.execute("""
    SELECT
        manufacturers.name AS manufacturer,
        products.id AS id
        products.name AS name,
        product_categories.name AS category
    FROM
        products
    INNER JOIN product_categories
    INNER JOIN manufacturers
    ON
        products.category_id = product_categories.id
    AND products.manufacturer_id = manufacturers.id;
    ORDER BY
        products.id DESC
    """)
    products = cur.fetchall()
    params['products'] = []
    for product in products:
        params['products'].append(product)
    return render_template('reviews.html', **params)

@app.route('/products/<productId>/')
def enterReview(productId=None):
    params = cookie_params(request)
    return render_template('enterReview.html', productId=productId, **params)

@app.route('/postReview/', methods=['POST'])
def postReview():
    params = cookie_params(request)
    username = request.cookies.get('username')

    db = mdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='matt',
        passwd='matt',
        db='aggrerate')
    cur = db.cursor()

    dtstr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    cur.execute("""
    INSERT INTO
        reviews
    VALUES (%s, %s, %s, %s, %s)
    """, (None, dtstr, request.form['score'], request.form['productId'],
            request.form['reviewText'])
    )

    cur.execute("""
    SELECT
        id
    FROM
        users
    WHERE
        name = %s
    """, (username,)
    )

    cur.execute("""
    INSERT INTO
        user_reviews
    VALUES
        (
            %s,
            LAST_INSERT_ID(),
            (
                SELECT
                    users.id
                FROM
                    users
                WHERE
                    users.name = %s
            )
        )
    """, (None, username)
    )

    db.commit()

    return render_template('successfulReview.html', **params)
