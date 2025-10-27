from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound

err_bp = Blueprint("errors", __name__)


@err_bp.app_errorhandler(NotFound)
def handleNotFound(err):
    return jsonify({"msg": "Not found"}), 404


@err_bp.app_errorhandler(Exception)
def handleGenericEx(err):
    return jsonify({"msg": "Sever die =))"}), 500
