from aggrerate import util
from bcrypt import hashpw, gensalt


def validateUser(username, password):
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        password
    FROM
        users
    WHERE
        name = %s
    """, username)
    fetch = cur.fetchall()

    if len(fetch) != 1:
        return False

    pw_hash = fetch[0]["password"]
    return hashpw(password, pw_hash) == pw_hash



def addUser(username, password, fullname):
    db = util.get_db()
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
        pw_hash = hashpw(password, gensalt())
        cur.execute("""
        INSERT INTO users
        VALUES
            (%s, %s, %s, %s)
        """, (None, username, pw_hash, fullname))
        db.commit()
        return True
