import os
import flask
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient

import acp_times  # Brevet time calculations

app = Flask(__name__)

# Step 1: create a client object
# The environment variable DB_PORT_27017_TCP_ADDR is the IP of a linked docker
# container (IP of the database). Generally "DB_PORT_27017_TCP_ADDR" can be set to
# "localhost" or "127.0.0.1".
#
# For windows:
# 1) Run "docker volume prune"
# 2) client = MongoClient('mongodb://mongodb:27017/')
# Now everything should work.
#
client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)

# Step 2: connect to the DB
db = client.tododb

@app.route('/')
def todo():
    _items = db.tododb.find()
    items = [item for item in _items]

    return render_template('todo.html', items=items)

# https://www.diffen.com/difference/GET-vs-POST-HTTP-Requests
@app.route("/insert", methods=["POST"])
def insert():
    data = request.get_json()
    items = data["items"]

    if not items:
        return flask.jsonify(error="Nothing to submit")

    db.times.insert_many(items)
    return flask.jsonify(status="ok")

@app.route("/fetch")
def fetch():
    docs = list(db.times.find({}, {"_id": 0}))
    if not docs:
        return flask.jsonify(error="Nothing to display")
    return flask.jsonify(result=docs)

@app.route("/display")
def display():
    return flask.render_template("display.html")


@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    
    # FIXME: These probably aren't the right open and close times
    # and brevets may be longer than 200km
    distance = request.args.get('brevet_dist_km', type=int)
    start = request.args.get('start_time', type = str)
    open_time = acp_times.open_time(km, distance, start)
    close_time = acp_times.close_time(km, distance, start)
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

#############


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
