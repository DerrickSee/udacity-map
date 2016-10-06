from datetime import datetime
from werkzeug import url_decode

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

from yelpy import *


app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'super secret key'


# Index View. Shows Welcome page.
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/places/<yelp_id>')
def place(yelp_id):
    data = business(id=yelp_id)
    return jsonify(data)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
