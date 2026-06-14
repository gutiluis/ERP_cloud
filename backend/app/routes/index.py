#!/usr/bin/env python3

# file: backend/app/routes/index.py
'''
# descr: public index rest api endpoint render
flask app loads correctly
create_app() is being called
index_bp is registered
gunicorn can import app
docker networking is working
http request reach backend through api


'''
# jsonify and json are not the same
from flask import Blueprint, render_template

index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index():
    "Render home public rest api edpoint"
    return render_template('index.html')
