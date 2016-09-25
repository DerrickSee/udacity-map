from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////catalog.db'
# db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
