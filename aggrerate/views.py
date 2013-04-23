from flask import render_template, request
import flask, time
import json

from aggrerate import app, util
from aggrerate.loginCode import loginCode, flogin
from aggrerate.scraper import ReviewScraper
from aggrerate.scraper.specifications import SpecificationScraper
from flask.ext import login

def cookie_params(request):
    params = {}
    if login.current_user.is_authenticated():
        params["username"] = login.current_user.data["username"]
    else:
        params["username"] = "anonymous"
    return params

@app.route('/')
@util.templated("main.html")
def main():
    params = cookie_params(request)
    # params = {'username': request.cookies.get['username']}
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        users.name          AS user_name,
        users.full_name     AS full_name,
        reviews.date        AS review_date,
        reviews.score       AS review_score,
        reviews.body_text   AS text,
        products.name       AS product_name,
        manufacturers.name  AS manufacturer_name,
        products.id         AS product_id
    FROM
        reviews
    INNER JOIN users
    INNER JOIN user_reviews
    INNER JOIN products
    INNER JOIN manufacturers
    ON
        (user_reviews.user_id = users.id)
    AND (user_reviews.review_id = reviews.id)
    AND (reviews.product_id = products.id)
    AND (products.manufacturer_id = manufacturers.id)
    ORDER BY
        reviews.date DESC,
        products.name ASC
    LIMIT 5
    """)
    params['reviews'] = cur.fetchall()

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
    if username == login.current_user.data['username']:
        params['active_user'] = True

    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        *
    FROM
        users
    WHERE
        users.name = %s
    """, username)
    user_profile = cur.fetchone()
    if user_profile:
        params['user'] = user_profile
    else:
        flask.abort(404)

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

    cur.execute("""
    SELECT
        user_preferences.id AS user_preference_id,
        review_sources_id AS source_id,
        review_sources.name AS source_name,
        priority
    FROM
        user_preferences
    INNER JOIN users
        ON users.id = user_preferences.user_id
    INNER JOIN review_sources
        ON review_sources_id = review_sources.id
    WHERE
        users.name = %s
    ORDER BY
        review_sources.name ASC
    """, username)
    preferences = cur.fetchall()

    params['reviews'] = []
    for product in products:
        params['reviews'].append(product)
    params['dispUsername'] = username

    params['preferences'] = preferences

    return params

@app.route('/user/set_preferences/', methods=['POST'])
def update_user_preference():
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor(None)
    deleted = cur.execute("""
    REPLACE INTO
        user_preferences (user_id, review_sources_id, priority)
    VALUES
        (
            %s,
            %s,
            %s
        )
    """, (login.current_user.data['user_id'], request.form['source_id'], request.form['priority']))
    db.commit()

    return flask.jsonify({'resp': True})

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

@app.route("/loginPage/")
@util.templated("login.html")
def loginPage():
    params = cookie_params(request)
    return params

@app.route("/attemptLogin/")
def attemptLogin():
    params = cookie_params(request)
    if 'username' in flask.request.args.keys() and 'password' in request.args.keys():
        if loginCode.validateUser(request.args['username'], request.args['password']):
            if login.login_user(flogin.User.get(request.args['username']), remember=True):
                flask.flash("You logged in!", "info")
                return flask.redirect(flask.url_for('main'))
    return flask.redirect(flask.url_for('loginPage'))

@app.route("/logout/")
def logout():
    resp = flask.make_response(render_template('main.html'))
    resp.set_cookie('username', '', expires=0)
    login.logout_user()
    flask.flash("You logged out", "info")
    return flask.redirect(flask.url_for('main'))

@app.route("/signup/")
@util.templated("signup.html")
def signup():
    return {}

@app.route('/attemptSignup', methods=["POST"])
def attemptSignup():
    if not ('username' in request.form.keys() and
            'password' in request.form.keys() and
            'fullname' in request.form.keys() and
            request.form['username'] and request.form['password'] and request.form['fullname']):
        return flask.redirect(flask.url_for('signup', retry=True))
    # It's time to add the user's new username and password to the table
    if loginCode.addUser(request.form['username'], request.form['password'], request.form['fullname']):
        flask.flash("Welcome %s. You can log in now." % request.form['fullname'], "info")
        return flask.redirect(flask.url_for('loginPage'))
    else:
        flask.flash("%s already exists in our database" % request.form['username'], "error")
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
        metascore_with_date(%s,products.id,NOW()) AS avg_score,
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
    """, (login.current_user.data["user_id"],))
    params['products'] = cur.fetchall()

    params['categories'] = util.get_product_categories()
    params['manufacturers'] = util.get_manufacturers()

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
    specs_url    = request.form['specs_url']

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

    # Scrape specifications
    specs_scraper = SpecificationScraper(specs_url)
    specs_scraper.parse_page()
    if not specs_scraper.specs:
        flask.flash('Unable to scrape specs', 'error')
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

    product_id = cur.lastrowid

    cur.executemany("""
    INSERT INTO
        specifications
    VALUES
        (
            NULL,
            %s,
            %s,
            %s,
            %s
        )
    """, [(product_id, k, v, util.ugly_str_to_float(v)) for k, v in specs_scraper.specs.iteritems()]
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
        if not params['product']:
            flask.abort(404)

        params['manufacturers'] = util.get_manufacturers(cur)
        params['categories'] = util.get_product_categories(cur)
        return render_template('product_edit.html', **params)

    # Otherwise we're a POST. Did they click cancel?
    if request.form.has_key('cancel'):
        flask.flash('Changes canceled', 'info')
        return flask.redirect(flask.url_for('product', product_id=product_id))

    if request.form.has_key('delete'):
        deleted = cur.execute("""
        DELETE FROM
            products
        WHERE
            id = %s
        """, (product_id,))
        db.commit()

        if deleted:
            flask.flash('Product deleted', 'success')
            return flask.redirect(flask.url_for('products_list'))
        else:
            flask.flash('Failed to delete product', 'error')
            return flask.redirect(flask.url_for('edit_product', product_id=product_id))

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
        product_categories.name AS category,
        metascore_with_date(%s,products.id,NOW()) AS avg_score
    FROM
        products
    INNER JOIN product_categories
    INNER JOIN manufacturers
    ON
        products.category_id = product_categories.id
    AND products.manufacturer_id = manufacturers.id
    WHERE
        products.id = %s
    """, (login.current_user.data["user_id"], product_id,))
    params['product'] = cur.fetchone()

    cur.execute("""
    SELECT
        name,
        value,
        value_decimal
    FROM
        specifications
    WHERE
        product_id = %s
    """, (product_id,)
    )
    params['specs'] = cur.fetchall()

    # Find the product scraped reviews
    cur.execute("""
    SELECT
        reviews.id,
        scraped_reviews.url AS url,
        date,
        score,
        blurb,
        review_sources.id AS review_source_id,
        review_sources.name AS source_name,
        COALESCE(SUM(votes.value), 0) AS sum
    FROM
        reviews
    INNER JOIN scraped_reviews
    ON
        reviews.id = scraped_reviews.review_id
    INNER JOIN review_sources
    ON
        scraped_reviews.review_source_id = review_sources.id
    LEFT JOIN votes
    ON
        reviews.id = votes.review_id
    AND scraped_reviews.review_source_id = review_sources.id
    WHERE
        product_id = %s
    GROUP BY
        reviews.id
    ORDER BY
        sum DESC,
        reviews.score DESC
    """, (product_id,))
    params['scraped_reviews'] = cur.fetchall()

    # Find the product user reviews
    cur.execute("""
    SELECT
        reviews.id,
        date,
        score,
        body_text,
        users.id AS user_id,
        users.name AS username,
        users.full_name AS full_name,
        COALESCE(SUM(votes.value), 0) AS sum
    FROM
        reviews
    INNER JOIN user_reviews
    ON
        reviews.id = user_reviews.review_id
    INNER JOIN users
    ON
        user_reviews.user_id = users.id
    LEFT JOIN votes
    ON
        reviews.id = votes.review_id
    WHERE
        product_id = %s
    GROUP BY
        reviews.id
    ORDER BY
        sum DESC,
        reviews.score DESC
    """, (product_id,))
    params['user_reviews'] = cur.fetchall()

    # Find tags
    cur.execute("""
    SELECT
        tags
    FROM
        product_tags
    WHERE
        product_id = %s
    """, (product_id,))
    product_tags = cur.fetchall()
    if len(product_tags) > 0:
        params['tags'] = product_tags[0]['tags']

    # Modify the behavior of inc/review.html linking
    params['product_page'] = True
    params['source_page'] = False

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
    if not scraper.score or not scraper.timestamp:
        flask.flash("Couldn't find the result, boo", "error")
        return redir

    # Add the scraped review to the database
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    INSERT INTO
        reviews (date, score, product_id, body_text)
    VALUES (%s, %s, %s, %s)
    """, (scraper.timestamp, scraper.score, request.form['product_id'], scraper.body)
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
            %s,
            %s
        )
    """, (scraper.__class__.pretty_site_name, request.form['url'], scraper.blurb or '')
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
        metascore_with_date(%s,products.id,NOW()) AS avg_score,
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
    """, (login.current_user.data["user_id"], category_id,))
    params['products'] = cur.fetchall()

    params['has_avg_scores']      = True
    params['has_avg_user_scores'] = True
    params['has_stddev']          = True

    return params

@app.route('/recommendations/')
@util.templated('recommendations.html')
def recommendations():
    return

@app.route('/recommendations/get_specification_names/')
def get_specification_names():
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor(None)
    cur.execute("""
    SELECT DISTINCT
        name
    FROM
        specifications
    """)
    spec_names = map(lambda d: d['name'], cur.fetchall())
    return flask.jsonify({'spec_names': spec_names})

def get_num(s):
    retStr = ""
    if s[:1] in '-+':
        retStr += s[:1]
        s = s[1:]
    p_good = True
    for c in s:
        if c.isdigit():
            retStr += c
        elif c == '.' and p_good:
            retStr += c
            p_good = False
        else:
            break
    if retStr:
        return float(retStr)
    else:
        return 0

def modify_score(baseScore, baseState, specification, requirement):
    if specification:
        print "BBBBB", baseScore, baseState, specification, requirement
        if requirement[1].lower() in ["<", "less than"]:
            if (specification["value_decimal"] and specification["value_decimal"] < get_num(requirement[2])):
                return (baseScore + 2, (baseState[0], 0))
            else:
                return (baseScore - 2, (0, baseState[1]))
        elif requirement[1].lower() in [">", "greater than"]:
            if (specification["value_decimal"] and specification["value_decimal"] > get_num(requirement[2])):
                return (baseScore + 2, (baseState[0], 0))
            else:
                return (baseScore - 2, (0, baseState[1]))
        elif requirement[1].lower() in ["is", "="]:
            if (specification["value_decimal"] and abs(get_num(requirement[2]) - float(specification["value_decimal"])) < 0.01) or str(requirement[2]).lower() == specification["value"].lower():
                return (baseScore + 2, (baseState[0], 0))
            else:
                return (baseScore - 2, (0, baseState[1]))
    else:
        return (baseScore-1, (0, baseState[1]))

@app.route('/execute_search/')
@util.templated('ajax/query_response.html')
def execute_search():
    params = cookie_params(request)

    query = request.args.get("query","")

    query_words = query.split()
    query_sql = """
    SELECT
        products.id AS id,
        products.name AS name,
        manufacturers.name AS manufacturer,
        product_categories.id AS category_id,
        product_categories.name AS category,
        COUNT(DISTINCT scraped_reviews.id) AS scraped_reviews_count,
        metascore_with_date(%s,products.id,NOW()) AS avg_score,
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
    """
    if query_words:
        query_sql += "WHERE\n "
        query_sql += ' AND '.join(
            ["(CONCAT_WS(' ', manufacturers.name, products.name, product_categories.name) REGEXP %s)"]*len(query_words)
        )
    query_sql += """
    GROUP BY
        products.id
    ORDER BY
        avg_score DESC,
        products.name ASC
    """

    sql_elements = [login.current_user.data["user_id"]]
    sql_elements.extend(query_words)

    (db, cur) = util.get_dict_cursor()
    cur.execute(query_sql, sql_elements)

    params['products'] = []
    params['products'].extend(cur.fetchall())
    for i in params['products']:
        if i["avg_score"]: i["avg_score"] = float(i["avg_score"])
        if i["avg_user_score"]: i["avg_user_score"] = float(i["avg_user_score"])

    # Unscored products start at an even 5
    for product in params['products']:
        product["rec_score"] = product["avg_score"] or 5
        product["rec_state"] = (1, 1) # (All recs pass, all recs fail)

    # Rebuild requirements list
    requirements = []
    for i in range(int(request.args.get('num_requirements'))):
        requirements.append(request.args.getlist('requirements[%s][]' % i))

    for requirement in requirements:
        print "REQUIREMENT: ", requirement
        cur.execute("""
            SELECT
                product_id,
                name,
                value,
                value_decimal
            FROM
                specifications
            WHERE
                name = %s""", (requirement[0],))
        raw_specs = cur.fetchall()
        specs = {}

        for s in raw_specs:
            specs[s["product_id"]] = s

        for product in params['products']:
            (product["rec_score"], product["rec_state"]) = \
                modify_score(product["rec_score"], product["rec_state"], specs.get(int(product["id"])), requirement)
            print "SCORE:", product["rec_score"], "STATE:", product["rec_state"]

    params['products'] = sorted(params['products'], key=lambda x: -x.get("rec_score"))
    for product in params['products']:
        if product['rec_state'] == (1, 0):
            # All the requirements passed
            product['rec_class'] = 'success'
        elif product['rec_state'] == (0, 1):
            # All the requirements failed
            product['rec_class'] = 'error'
        elif product['rec_state'] == (0, 0):
            pass
        elif product['rec_state'] == (1, 1):
            pass

    params['has_categories'] = True
    params['has_avg_scores'] = True
    params['has_rec_scores'] = True

    return params

# Takes in the name of a source, and shows the
# source's information
@app.route('/source/<review_source_id>/')
@util.templated('source.html')
def source(review_source_id):

    params = cookie_params(request)

    # Returns a relation whose attributes have
    # 1. Name of the source (ex: The Verge)
    # 2. The URL of the source (ex: www.theverge.com)
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        name,
        url
    FROM
        review_sources
    WHERE
        review_sources.id = %s
    """, review_source_id)
    source_data = cur.fetchall()
    params['source_data'] = source_data

    # Returns a relation that contains
    # 1. A product name
    # 2. The source's review for the product
    # 3. URL to the review
    cur.execute("""
    SELECT
        products.name           AS product_name,
        manufacturers.name      AS manufacturer,
        scraped_reviews.blurb   AS blurb,
        scraped_reviews.url     AS url
    FROM
        scraped_reviews INNER JOIN reviews
            ON scraped_reviews.review_id = reviews.id
        INNER JOIN products
            ON reviews.product_id = products.id
        INNER JOIN manufacturers
            ON products.manufacturer_id = manufacturers.id
    WHERE
        scraped_reviews.review_source_id = %s
    """, review_source_id)
    reviews = cur.fetchall()    # contains all of the reviews
    params['reviews'] = reviews

    return params

@app.route('/attemptSource', methods=["POST"])
def attemptSource():
    # Put more lines of code down here
    return

@app.route('/history/')
@util.templated('history.html')
def history():
    params = cookie_params(request)
    params['categories'] = util.get_product_categories()
    return params

@app.route('/history/get_results/<ts>/')
@util.templated('ajax/history_results.html')
def get_history_results(ts):
    params = cookie_params(request)

    query = """
    SELECT
        products.id AS id,
        products.name AS name,
        manufacturers.name AS manufacturer,
        product_categories.id AS category_id,
        product_categories.name AS category,
        COUNT(DISTINCT scraped_reviews.id) AS scraped_reviews_count,
        metascore_with_date(%s,products.id,%s) AS avg_score,
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
    """
    
    if request.args.get('c') != 'all':
        query += """
        WHERE
            products.category_id = %s
        """

    query += """
    GROUP BY
        products.id
    HAVING
        avg_score > 0
    ORDER BY
        avg_score DESC,
        products.name ASC
    """

    sql_args = (login.current_user.data["user_id"], ts)
    if request.args.get('c') != 'all':
        sql_args += (request.args.get('c'),)

    (db, cur) = util.get_dict_cursor(None)
    cur.execute(query, sql_args)
    params['products'] = cur.fetchall()
    params['categories'] = util.get_product_categories()

    params['has_categories'] = True
    params['has_avg_scores'] = True

    # Uncomment this to include average user scores in the products table
    return params

@app.route('/review/get_votes/<review_id>/')
def get_review_votes(review_id):
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor(None)
    cur.execute("""
    SELECT
        COALESCE(SUM(value), 0) AS sum
    FROM
        votes
    WHERE
        review_id = %s
    """, (review_id,))
    score = int(cur.fetchall()[0]['sum'])

    return flask.jsonify({'score': score})

@app.route('/review/submit_vote/', methods=['POST'])
def submit_review_vote():
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor(None)
    cur.execute("""
    REPLACE INTO
        votes (review_id, user_id, value)
    VALUES
        (%s, %s, %s)
    """, (
            request.form['review_id'],
            login.current_user.data['user_id'],
            request.form['value']
        )
    )
    db.commit()

    # Now return the new value
    cur.execute("""
    SELECT
        COALESCE(SUM(value), 0) AS sum
    FROM
        votes
    WHERE
        review_id = %s
    """, (request.form['review_id'],))
    score = int(cur.fetchall()[0]['sum'])

    return flask.jsonify({'score': score})

@app.route('/review/get_comments/<review_id>/')
@util.templated('ajax/comments.html')
def get_review_comments(review_id):
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor(None)
    cur.execute("""
    SELECT
        comments.id,
        comments.body_text,
        users.id AS user_id,
        users.name,
        users.full_name
    FROM
        comments
    INNER JOIN users
        ON comments.user_id = users.id
    WHERE
        review_id = %s
    ORDER BY
        comments.id ASC
    """, (review_id,))
    comments = cur.fetchall()

    return {'comments': comments}

@app.route('/review/post_comment/', methods=['POST'])
@util.templated('ajax/comments.html')
def post_review_comment():
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor(None)
    cur.execute("""
    INSERT INTO
        comments (user_id, review_id, body_text)
    VALUES
        (%s, %s, %s)
    """, (
            login.current_user.data['user_id'],
            request.form['review_id'],
            request.form['body_text']
        )
    )
    db.commit()

    cur.execute("""
    SELECT
        comments.id,
        comments.body_text,
        users.id AS user_id,
        users.name,
        users.full_name
    FROM
        comments
    INNER JOIN users
        ON comments.user_id = users.id
    WHERE
        review_id = %s
    ORDER BY
        comments.id ASC
    """, (request.form['review_id'],))
    comments = cur.fetchall()

    return {'comments': comments}

@app.route('/review/delete_comment/', methods=['POST'])
def delete_review_comment():
    params = cookie_params(request)

    (db, cur) = util.get_dict_cursor(None)
    deleted = cur.execute("""
    DELETE FROM
        comments
    WHERE
        id = %s
    AND user_id = %s
    """, (request.form['comment_id'], login.current_user.data['user_id']))
    db.commit()

    return flask.jsonify({'deleted': deleted})

# Takes in the name of a source, and shows the
# source's information
@app.route('/source/<review_source_id>/')
@util.templated('source.html')
def source(review_source_id):
    params = cookie_params(request)

    if params["username"] != "anonymous":
        params['active_user'] = True
    else:
        params['active_user'] = False

    # Returns a relation whose attributes have
    # 1. Name of the source (ex: The Verge)
    # 2. The URL of the source (ex: www.theverge.com)
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        id,
        name,
        url
    FROM
        review_sources
    WHERE
        review_sources.id = %s
    """, review_source_id)
    source_data = cur.fetchone()
    if not source_data:
        flask.abort(404)
    params['source_data'] = source_data

    # Returns a relation that contains
    # 1. A product name
    # 2. The source's review for the product
    # 3. URL to the review
    cur.execute("""
    SELECT
        reviews.id              AS id,
        reviews.date            AS date,
        reviews.score           AS score,
        scraped_reviews.blurb   AS blurb,
        scraped_reviews.url     AS url,
        review_sources.name     AS source_name,
        products.id             AS product_id,
        products.name           AS product_name,
        manufacturers.name      AS manufacturer
    FROM
        scraped_reviews
    INNER JOIN reviews
        ON scraped_reviews.review_id = reviews.id
    INNER JOIN review_sources
        ON scraped_reviews.review_source_id = review_sources.id
    INNER JOIN products
        ON reviews.product_id = products.id
    INNER JOIN manufacturers
        ON products.manufacturer_id = manufacturers.id
    WHERE
        scraped_reviews.review_source_id = %s
    """, review_source_id)
    reviews = cur.fetchall()    # contains all of the reviews
    params['reviews'] = reviews

    cur.execute("""
    SELECT
        priority
    FROM
        user_preferences
    WHERE
        user_id = %s
    AND review_sources_id = %s
    """, (login.current_user.data["user_id"], source_data['id']))
    preferences = cur.fetchone()
    if preferences:
        params['original_priority'] = (preferences['priority'])
    else:
        params['original_priority'] = 1.0

    # Modify the behavior of inc/review.html linking
    params['product_page'] = False
    params['source_page'] = True

    return params
