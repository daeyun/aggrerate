from flask import Flask
from flask.ext.misaka import Misaka

app = Flask(__name__)
Misaka(app, smartypants=True)

import aggrerate.views
