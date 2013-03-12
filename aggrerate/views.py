from flask import render_template, request
import flask, time

from aggrerate import app, util
from aggrerate.web_scripts import loginCode
from aggrerate.scraper import ReviewScraper

def cookie_params(request):
    params = {"username": request.cookies.get('username')}
    return params

@app.route('/')
@util.templated("main.html")
def main():
    params = cookie_params(request)
    # params = {'username': request.cookies.get['username']}
    return params

@app.route("/about/")
@util.templated("about.html")
def about():
    params = cookie_params(request)
    return params

@app.route("/reviews/")
@util.templated("reviews.html")
def reviews():
    params = cookie_params(request)
    return params

@app.route("/users/<username>/")
@util.templated("user.html")
def user_profile(username):
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        reviews.date AS date,
        reviews.score AS score,
        reviews.product_id AS product_id,
        reviews.body_text AS body_text,
        reviews.id AS id,
        users.id AS user_id,
        products.id AS product_id,
        products.name AS product_name,
        manufacturers.name AS manufacturer
    FROM
        users
    INNER JOIN user_reviews
    INNER JOIN reviews
    INNER JOIN products
    INNER JOIN manufacturers
    ON
        users.id = user_reviews.user_id
    AND user_reviews.review_id = reviews.id
    AND products.id = reviews.product_id
    AND manufacturers.id = products.manufacturer_id
    WHERE
        users.name = %s
    ORDER BY
        reviews.date DESC,
        products.name ASC
    """, username)
    products = cur.fetchall()

    params['reviews'] = []
    for product in products:
        params['reviews'].append(product)
    params['dispUsername'] = username

    return params

@app.route('/delete_review/<review_id>/')
def delete_review(review_id):
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor(None)
    deleted = cur.execute("""
    DELETE FROM
        reviews
    WHERE
        id = %s
    AND id IN
        (
            SELECT
                review_id
            FROM
                user_reviews
            INNER JOIN users ON (users.id = user_reviews.user_id)
            WHERE
                users.name = %s
        )
    """, (review_id, params['username']))
    db.commit()

    if deleted:
        flask.flash('Review deleted', 'success')
    else:
        flask.flash('Unable delete review (written by somebody else?)', 'error')
    if request.args.has_key('product_id'):
        return flask.redirect(flask.url_for('product', product_id=request.args['product_id']))
    elif request.args.has_key('username'):
        return flask.redirect(flask.url_for('user_profile', username=request.args['username']))
    else:
        flask.abort(404)

@app.route("/login/")
@util.templated("login.html")
def login():
    params = cookie_params(request)
    return params

@app.route("/attemptLogin/")
def attemptLogin():
    params = cookie_params(request)
    if 'username' in flask.request.args.keys() and 'password' in request.args.keys():
        if loginCode.validateUser(request.args['username'], request.args['password']):
            resp = flask.make_response(render_template('main.html', username=flask.request.args['username']))
            resp.set_cookie('username', flask.request.args['username'])
            return resp
    return flask.redirect(flask.url_for('login'))

@app.route("/logout/")
def logout():
    resp = flask.make_response(render_template('main.html'))
    resp.set_cookie('username', '', expires=0)
    return resp

@app.route("/signup/")
@util.templated("signup.html")
def signup():
    return {}

@app.route('/attemptSignup', methods=["POST"])
def attemptSignup():
    if not ('username' in request.form.keys() and 'password' in request.form.keys() and request.form['username'] and request.form['password']):
        return flask.redirect(flask.url_for('signup', retry=True))
    # It's time to add the user's new username and password to the table
    if loginCode.addUser(request.form['username'], request.form['password']):
        return flask.redirect(flask.url_for('login'))
    else:
        return flask.redirect(flask.url_for('signup', retry=True))

@app.route("/products/")
@util.templated("products_list.html")
def products_list():
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        products.id AS id,
        products.name AS name,
        manufacturers.name AS manufacturer,
        product_categories.id AS category_id,
        product_categories.name AS category,
        COUNT(DISTINCT scraped_reviews.id) AS scraped_reviews_count,
        CAST(AVG(reviews.score) AS DECIMAL(3, 1)) AS avg_score,
        COUNT(DISTINCT user_reviews.id) AS user_reviews_count,
        CAST(AVG(reviews_u.score) AS DECIMAL(3, 1)) AS avg_user_score
    FROM
        products
    INNER JOIN product_categories
        ON (products.category_id = product_categories.id)
    INNER JOIN manufacturers
        ON (products.manufacturer_id = manufacturers.id)
    LEFT JOIN (reviews, scraped_reviews)
        ON (reviews.product_id = products.id AND scraped_reviews.review_id = reviews.id)
    LEFT JOIN (reviews AS reviews_u, user_reviews)
        ON (reviews_u.product_id = products.id AND user_reviews.review_id = reviews_u.id)
    GROUP BY
        products.id
    ORDER BY
        avg_score DESC,
        products.name ASC
    """)
    params['products'] = cur.fetchall()
    params['categories'] = util.get_product_categories()

    cur.execute("""
    SELECT
        id,
        name
    FROM
        manufacturers
    """)
    params['manufacturers'] = cur.fetchall()

    params['has_categories'] = True
    params['has_avg_scores'] = True

    # Uncomment this to include average user scores in the products table
    # params['has_avg_user_scores'] = True

    return params

@app.route('/products/add_product/', methods=['POST'])
def add_product():
    params = cookie_params(request)

    redir = flask.redirect(flask.url_for('products_list'))

    # Prepare form values
    product_name = request.form['product_name']
    category_id  = request.form['category_id']

    mfg_in_db     = request.form['manufacturer_present']
    mfg_not_in_db = request.form['manufacturer_not_present']

    # Verify data
    invalid = False
    if not product_name:
        flask.flash('Product name required', 'error')
        invalid = True
    if not (mfg_in_db or mfg_not_in_db):
        flask.flash('Manufacturer must either be selected or written', 'error')
        invalid = True

    if invalid:
        return redir

    # Insert into database
    (db, cur) = util.get_dict_cursor()
    if mfg_in_db:
        cur.execute("""
        INSERT INTO
            products
        VALUES
            (
                NULL,
                %s,
                %s,
                %s
            )
        """, (product_name, category_id, mfg_in_db)
        )
    else:
        util.add_manufacturer(cur, request.form['manufacturer_not_present'])
        cur.execute("""
        INSERT INTO
            products
        VALUES
            (
                NULL,
                %s,
                %s,
                LAST_INSERT_ID()
            )
        """, (product_name, category_id)
        )
    db.commit()

    flask.flash('Added new product!', 'success')
    return redir

@app.route('/products/<product_id>/edit/', methods=['GET', 'POST'])
def edit_product(product_id):
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor()

    if request.method == 'GET':
        # We need to query the database for all the existing properties so that
        # we can autofill the form. We also need the options for the
        # manufacturers, etc.
        cur.execute("""
        SELECT
            id,
            name,
            category_id,
            manufacturer_id
        FROM
            products
        WHERE
            id = %s
        """, (product_id,)
        )
        params['product'] = cur.fetchone()
        params['manufacturers'] = util.get_manufacturers(cur)
        params['categories'] = util.get_product_categories(cur)
        return render_template('product_edit.html', **params)

    # Otherwise we're a POST. Did they click cancel?
    if request.form.has_key('cancel'):
        flask.flash('Chankes canceled', 'info')
        return flask.redirect(flask.url_for('product', product_id=product_id))

    # Prepare form values
    product_name = request.form['product_name']
    category_id  = request.form['category_id']

    mfg_in_db     = request.form['manufacturer_present']
    mfg_not_in_db = request.form['manufacturer_not_present']

    # Verify data
    invalid = False
    if not product_name:
        flask.flash('Product name required', 'error')
        invalid = True
    if not (mfg_in_db or mfg_not_in_db):
        flask.flash('Manufacturer must either be selected or written', 'error')
        invalid = True

    if invalid:
        # We need to rerender the form with what they submitted. This is a
        # pain in the ass.
        #
        # The `manufacturer_id` is the tricky bit. It should only be possible
        # to have an invalid state when they selected nothing in both fields,
        # so I think we can just not give an ID here.
        params['product'] = {
            'id': product_id,
            'name': product_name,
            'category_id': category_id,
            'manufacturer_id': None
        }
        params['manufacturers'] = util.get_manufacturers(cur)
        params['categories'] = util.get_product_categories(cur)
        return render_template('product_edit.html', **params)

    # FIXME: Delete the old manufacturer if it is now orphaned. (Can this be
    # done in SQL?)

    # FIXME: Don't let duplicates get into the manufacturers database! Ew ew ew!

    # Update the database
    if mfg_in_db:
        cur.execute("""
        UPDATE
            products
        SET
            name = %s,
            category_id = %s,
            manufacturer_id = %s
        WHERE
            id = %s
        """, (product_name, category_id, mfg_in_db, product_id)
        )
    else:
        util.add_manufacturer(cur, request.form['manufacturer_not_present'])
        cur.execute("""
        UPDATE
            products
        SET
            name = %s,
            category_id = %s,
            manufacturer_id = LAST_INSERT_ID()
        WHERE
            id = %s
        """, (product_name, category_id, product_id)
        )
    db.commit()

    flask.flash('Updated product!', 'success')
    return flask.redirect(flask.url_for('product', product_id=product_id))

@app.route("/products/<product_id>/", methods=["GET"])
@util.templated("product.html")
def product(product_id=None):
    params = cookie_params(request)

    # Find the product properties
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        manufacturers.name AS manufacturer,
        products.id AS id,
        products.name AS name,
        product_categories.name AS category
    FROM
        products
    INNER JOIN product_categories
    INNER JOIN manufacturers
    ON
        products.category_id = product_categories.id
    AND products.manufacturer_id = manufacturers.id
    WHERE
        products.id = %s
    """, (product_id,))
    params['product'] = cur.fetchone()

    # Find the product scraped reviews
    cur.execute("""
    SELECT
        reviews.id,
        scraped_reviews.url AS url,
        date,
        score,
        body_text,
        review_sources.name AS source_name
    FROM
        reviews
    INNER JOIN scraped_reviews
    INNER JOIN review_sources
    ON
        reviews.id = scraped_reviews.review_id
    AND scraped_reviews.review_source_id = review_sources.id
    WHERE
        product_id = %s
    """, (product_id,))
    params['scraped_reviews'] = cur.fetchall()


    # Find the product user reviews
    cur.execute("""
    SELECT
        reviews.id,
        date,
        score,
        body_text,
        users.name AS username
    FROM
        reviews
    INNER JOIN user_reviews
    INNER JOIN users
    ON
        reviews.id = user_reviews.review_id
    AND user_reviews.user_id = users.id
    WHERE
        product_id = %s
    """, (product_id,))
    params['user_reviews'] = cur.fetchall()

    return params

@app.route("/products/<product_id>/post_review/", methods=["POST"])
def post_product_review(product_id):
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    INSERT INTO
        reviews
    VALUES (NULL, NOW(), %s, %s, %s)
    """, (request.form['score'], product_id, request.form['reviewText'])
    )
    cur.execute("""
    INSERT INTO
        user_reviews
    VALUES
        (
            NULL,
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
    """, (params['username'],)
    )

    db.commit()

    flask.flash("Posted review!", "success")
    return flask.redirect(flask.url_for('product', product_id=product_id))

@app.route('/scrape/', methods=['POST'])
def scrape():
    params = cookie_params(request)
    
    redir = flask.redirect(flask.url_for('product', product_id=request.form['product_id']))

    # Create the appropriate scraper
    scraper = ReviewScraper.from_url(request.form['url'])
    if not scraper:
        flask.flash("Couldn't create the scraper, boo", "error")
        return redir

    scraper.parse_page()
    if not scraper.score:
        flask.flash("Couldn't find the result, boo", "error")
        return redir

    # Add the scraped review to the database
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    INSERT INTO
        reviews
    VALUES (NULL, NOW(), %s, %s, %s)
    """, (scraper.score, request.form['product_id'], scraper.body)
    )
    cur.execute("""
    INSERT INTO
        scraped_reviews
    VALUES
        (
            NULL,
            LAST_INSERT_ID(),
            (
                SELECT
                    review_sources.id
                FROM
                    review_sources
                WHERE
                    review_sources.name = %s
            ),
            %s
        )
    """, (scraper.__class__.pretty_site_name, request.form['url'])
    )
    db.commit()

    flask.flash("Successfully scraped. They gave this product a %s." % scraper.score, "success")
    return redir

@app.route('/products/categories/<category_id>/')
@util.templated('category.html')
def product_category(category_id):
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor()

    # We request *all* categories so that we can display them on the right
    # sidebar, then pick out just the one we need for this page from that.
    params['categories'] = util.get_product_categories(cur)
    params['category'] = filter(
            lambda d: d['id'] == int(category_id),
            params['categories']
        )[0]['name']

    cur.execute("""
    SELECT
        products.id AS id,
        products.name AS name,
        manufacturers.name AS manufacturer,
        COUNT(DISTINCT scraped_reviews.id) AS scraped_reviews_count,
        CAST(AVG(reviews.score) AS DECIMAL(3, 1)) AS avg_score,
        CAST(STDDEV_POP(reviews.score) AS DECIMAL(3, 2)) AS stddev,
        COUNT(DISTINCT user_reviews.id) AS user_reviews_count,
        CAST(AVG(reviews_u.score) AS DECIMAL(3, 1)) AS avg_user_score
    FROM
        products
    INNER JOIN manufacturers
        ON (products.manufacturer_id = manufacturers.id)
    LEFT JOIN (reviews, scraped_reviews)
        ON (reviews.product_id = products.id AND scraped_reviews.review_id = reviews.id)
    LEFT JOIN (reviews AS reviews_u, user_reviews)
        ON (reviews_u.product_id = products.id AND user_reviews.review_id = reviews_u.id)
    WHERE
        products.category_id = %s
    GROUP BY
        products.id
    ORDER BY
        avg_score DESC,
        products.name ASC
    """, (category_id,))
    params['products'] = cur.fetchall()

    params['has_avg_scores']      = True
    params['has_avg_user_scores'] = True
    params['has_stddev']          = True

    return params
