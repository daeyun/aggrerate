from flask import Flask
from flask.ext.misaka import Misaka

app = Flask(__name__)

# The secret key is used when creating session cookies
app.secret_key = 'aggrerate_secret_key'

Misaka(app, smartypants=True)

import aggrerate.views
