from flask.ext import login
from aggrerate import util

class User(login.UserMixin):
    @classmethod
    def get(cls, userid):
        data = util.get_userdata(username = userid)
        if data:
            data = data[0]
        else:
            return None        

        return User(data, userid=="matt")

    def __init__(self, data, admin):
        self.data = data
        self.admin = admin

    def get_username(self):
        return self.data["username"]

    def is_admin(self):
        return self.data["username"] == "admin"

    def is_authenticated(self):
        if self.data["username"] == "anonymous":
            return False
        return super(User, self).is_authenticated()

    def get_id(self):
        return self.data["username"]

def getAnonymousUser():
    return User({"username":"anonymous", "user_id":0}, False)

