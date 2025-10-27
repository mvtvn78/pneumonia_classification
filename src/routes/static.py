from flask import Blueprint, send_from_directory

static_bp = Blueprint("static", __name__)


@static_bp.route("/static/<path:fileName>")
def staticHandler(fileName):
    return send_from_directory("../store", fileName)
