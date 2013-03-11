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
        db='aggrerate'
    )

def get_dict_cursor(db=None):
    if not db:
        db = get_db()
    return (db, db.cursor(mdb.cursors.DictCursor))
