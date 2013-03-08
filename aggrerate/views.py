from aggrerate import app
from flask import render_template

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')

@app.route('/login')
def login():
    return render_template('login.html')

