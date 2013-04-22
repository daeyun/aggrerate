from aggrerate import util
from bcrypt import hashpw, gensalt


# Hashes all plaintext passwords in the users table.
def hash_plaintext():
    (db, cur) = util.get_dict_cursor()
    cur.execute("""
    SELECT
        name, password
    FROM
        users
    """)
    fetch = cur.fetchall()

    for account in fetch:

        password = account["password"]
        user = account["name"]
        print user
        print password
        try:
            hashpw("password", password)
        except:
            pw_hash = hashpw(password, gensalt())
            print pw_hash
            cur.execute("""
            UPDATE
                users
            SET
                name = %s, password = %s
            WHERE
                name = %s
            """, (user, pw_hash, user))
            fetch = cur.fetchall()
            db.commit()

hash_plaintext()
