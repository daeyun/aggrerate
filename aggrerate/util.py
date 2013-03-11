import MySQLdb as mdb

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
