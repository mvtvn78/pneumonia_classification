from flask import request
from util import generateUnique as gn

from werkzeug.utils import secure_filename


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def uploadHanler():
    if "file" not in request.files:
        return -1
    f = request.files["file"]
    if f.filename == "":
        return -2
    if f and allowed_file(f.filename):
        ext = f.filename.split(".")[-1]
        filename = "store\\" + secure_filename(f"{gn.generateUniqueTimestamp()}.{ext}")
        f.save(filename)
        return filename
