from flask import Flask
app = Flask(__name__)

@app.route('/')
def main():
    return 'This is Aggrerate. Here is a <a href="/hackgrerate">link</a>.'

@app.route('/hackgrerate')
def hackgrerate():
    return 'Team Hackgrerate'
