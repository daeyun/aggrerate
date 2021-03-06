import re
import MySQLdb as mdb

from functools import wraps
from flask import request, render_template

# From Flask documentation:
# http://flask.pocoo.org/docs/patterns/viewdecorators/
def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator

def get_db():
    return mdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='jeff',
        passwd='jeff',
        db='aggrerate',
        charset='utf8'
    )

def get_dict_cursor(db=None):
    if not db:
        db = get_db()
    return (db, db.cursor(mdb.cursors.DictCursor))

# Database helpers
def get_product_categories(cur=None):
    if not cur:
        (_, cur) = get_dict_cursor()

    cur.execute("""
    SELECT
        id,
        name
    FROM
        product_categories
    ORDER BY
        id
    """)
    return cur.fetchall()

def get_manufacturers(cur=None):
    if not cur:
        (_, cur) = get_dict_cursor()

    cur.execute("""
    SELECT
        id,
        name
    FROM
        manufacturers
    ORDER BY
        name
    """)
    return cur.fetchall()

# Note that `cur` can't be None when we're editing the database, because this
# API would not provide the client any way to commit to the db after executing.
def add_manufacturer(cur, mfg):
    cur.execute("""
    INSERT INTO
        manufacturers
    VALUES
        (
            NULL,
            %s
        )
    """, (mfg,)
    )

# Get User details based on a username and password
def get_userdata(username, cur=None):
    if not cur:
        (_, cur) = get_dict_cursor()

    cur.execute("""
    SELECT
        id as user_id,
        name as username,
        full_name as fullname
    FROM
        users
    WHERE
        name = %s
    """, (username,))

    return cur.fetchall()


# This is not a very efficient way to strap tags, but it's easy and robust.
def strip_tags(string):
    if not string:
        return ''

    string = re.sub(r'\{[\s\S]*?\}', r'', string)
    string = re.sub(r'\<[\s\S]*?\>', r'', string)
    string = re.sub(r'//[^ ]', r' ', string)
    string = re.sub(r'[\(\)]', r'', string)
    string = re.sub(r'[^ a-zA-Z0-9\.\-\_\/]', r' ', string)
    string = string.lower()
    string = re.sub(r'\.[ \n\t\r]', r' ', string)
    string = re.sub(r'[\t\n ]+', r' ', string)
    return string

def ugly_str_to_float(s):
    try:
        return float(filter(lambda x: unicode.isdigit(x) or x == '.', s))
    except:
        return None
