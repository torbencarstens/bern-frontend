from datetime import datetime
from typing import Optional

import flask
from flask import Flask, render_template, send_from_directory, request, abort
from flask_minify import Minify

from opendata import api
from opendata.api import get_stationboard
from opendata.models import Point, QueryType, LocationSearchResponse, Stationboard

app = Flask("bus", template_folder="flask_templates")
Minify(app=app, html=True, js=True, cssless=True)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory('public', "favicon.jpg")


@app.route("/public/<path:path>")
def public(path: str):
    if "images" in path:
        stop_number = request.args.to_dict().get("stop_number")
        extension = path.rsplit(".")[-1]
        path = f"images/{stop_number}.{extension}"

    return send_from_directory('public', path)


@app.route("/health")
def health():
    return "", 200


@app.route('/setcookie', methods=['GET', 'POST'])
def setcookie():
    if request.method == "POST":
        cookie_value = request.form.get("show-image")
    else:
        cookie_value = request.args.get("show-image")
    cookie_value = "true" if cookie_value else "false"
    stop_number = request.args.get('stop_number')

    resp = flask.redirect(f"/{stop_number}")
    resp.set_cookie('showImage', cookie_value, samesite="STRICT")

    return resp


@app.route('/search', methods=["GET"])
def search():
    query = request.args.get("query")
    x = request.args.get("x")
    y = request.args.get("y")
    _type = request.args.get("type")
    if _type:
        _type = QueryType(_type)
    try:
        point = Point(x, y)
    except ValueError:
        point = None

    data: Optional[LocationSearchResponse] = api.search_location(query, point, _type)
    if not data:
        abort(500)

    response = flask.Response(data.to_json())
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/", defaults={"station_id": "8590010"}, methods=["GET"])
@app.route("/station_id", methods=["GET"])
def index(station_id: str):
    limit = request.args.get("limit", 10)
    stationboard: Stationboard = get_stationboard(station_id=station_id, limit=limit)
    # handle error appropriately
    if not stationboard:
        abort(404)

    kwargs = {
        "stationboard": stationboard.stationboard,
        "station": stationboard.station,
        "time": datetime.now().strftime("%H:%M")
    }

    # pycharm doesn't recognize the changed templates folder (flask_templates)
    # noinspection PyUnresolvedReferences
    return render_template("index.html", **kwargs)
