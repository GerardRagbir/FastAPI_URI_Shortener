from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.before_first_request
def initialise_tables():
    db.create_all()


class Urls(db.Model):
    id_ = db.Column('id_', db.Integer, primary_key=True)
    long = db.Column('long', db.String())
    short = db.Column('short', db.String(4))

    def __init__(self, long, short):
        self.long = long
        self.short = short


def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=4)
        rand_letters = "".join(rand_letters)
        short_url = Urls.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters


@app.route('/', methods=['POST', 'GET'])
def root():
    if request.method == "POST":
        long_url = request.form["formUrl"]
        found_url = Urls.query.filter_by(long=long_url).first()

        if found_url:
            return redirect(url_for("display_short_url", url=found_url.short))
        else:
            short_url = shorten_url()
            new_url = Urls(long_url, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))

    else:
        return render_template("urlPage.html")


@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f'<h1> URL not found. </h1>'


@app.route('/all')
def display_all():
    return render_template('allUrls.html', vals=Urls.query.all())


if __name__ == '__main__':
    app.run()
