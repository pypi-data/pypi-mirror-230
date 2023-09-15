from flask import Blueprint, render_template, request, g
from datetime import datetime
from utah.arches.web_blueprints import render_content

app = Blueprint('myapp', __name__)

counter = 0

@app.route("/")
def hello_world():
    return render_content._getDocument("main/default.html", g.locale)

@app.route("/favicon.ico")
def favicon():
    return render_content._getDocument("main/images/tool-icon.png", g.locale)
