import MySQLdb

def validateUser(username, password):
    db = MySQLdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='jeff',
        passwd='jeff',
        db='aggrerate')
    cur = db.cursor()
    cur.execute("""
    SELECT
        password
    FROM
        users
    WHERE
        name = %s
    """, username)
    fetch = cur.fetchall()
    return len(fetch) == 1 and fetch[0][0] == password

def addUser(username, password):
    db = MySQLdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='jeff',
        passwd='jeff',
        db='aggrerate')
    cur = db.cursor()
    cur.execute("""
    SELECT
        name
    FROM
        users
    WHERE
        name = %s
    """, username)
    if len(cur.fetchall()) != 0:
        return False
    else:
        cur.execute("""
        INSERT INTO users
        VALUES
            (%s, %s, %s)
        """, (None, username, password))
        db.commit()
        return True

