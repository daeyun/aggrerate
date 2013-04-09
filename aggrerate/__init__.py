from flask import Flask
from flask.ext.misaka import Misaka
from flask.ext import login
from aggrerate.loginCode import flogin

app = Flask(__name__)

# The secret key is used when creating session cookies
app.secret_key = 'aggrerate_secret_key'

Misaka(app, smartypants=True)

login_manager = login.LoginManager()

@login_manager.user_loader
def load_user(userid):
    return flogin.User.get(userid)

login_manager.setup_app(app)

@app.context_processor
def utility_processor():
    def current_user():
        if login.current_user.is_authenticated():
            return login.current_user
        else:
            return None
    return dict(current_user=current_user)

import aggrerate.views
