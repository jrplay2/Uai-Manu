from flask import Blueprint, render_template, current_app, send_from_directory
import os

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/desnatadeira")
def desnatadeira():
    return render_template("desnatadeira.html")

@bp.route("/wse250")
def wse250():
    return render_template("wse250.html")

@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
