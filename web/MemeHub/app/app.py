import os
from flask import Flask, request, redirect, render_template, render_template_string, send_file, session, Blueprint, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import secrets
from db_handler import ImageHandler
from dotenv import load_dotenv
import uuid
import datetime

load_dotenv()

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_TYPES = {"image/jpeg", "image/png"}
BLACKLIST = ['[', ']', '.']

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
app.secret_key = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH_MB")) * 1024 * 1024
app.config["DEBUG"] = os.getenv("FLASK_ENV") == "development"

# Heplers

# checks if file's mime type is in allowed types
def allowed_file(file):
    return file.mimetype in ALLOWED_TYPES

def static_file_hash(filename):
    return int(os.stat(filename).st_mtime)

def getimages():
    # images of current session
    path = os.path.join(APP_ROOT, UPLOAD_FOLDER, session["uid"])
    handler = ImageHandler(path)
    images = handler.getall()

    # static images
    path = os.path.join(APP_ROOT, UPLOAD_FOLDER, "static")
    handler = ImageHandler(path)
    images += handler.getall()

    return sorted(images, key=lambda img: img["created_at"], reverse=True)

# Before requests

@app.before_first_request
def permanent_session():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(days=365)

# register session
@app.before_request
def register():
    if not session.get("uid"):
        session["uid"] = uuid.uuid4().hex
    path = os.path.join(APP_ROOT, UPLOAD_FOLDER, session["uid"])
    if not os.path.isdir(path):
        os.mkdir(path)

# Routes

@app.route("/")
def index():
    images = getimages()
    if not images:
        return render_template("index.html", images=None)

    title_error = False
    current = images[0]
    image_url = render_template_string(url_for("send_image", path=current["path"]))
    try:
        image_title = render_template_string(current["title"])
    except Exception as e:
        print(e)
        image_title = ""
        title_error = True

    return render_template("index.html", images=images, image_url=image_url, image_title=image_title, title_error=title_error)

@app.route("/upload", methods=["GET","POST"])
def upload_file():
    if request.method == "GET":
        return render_template("upload.html", error=None)

    title = request.form.get("title") or ""
    if any( char in title for char in BLACKLIST ):
        return render_template("upload.html", error="Character not allowed")

    target = os.path.join(APP_ROOT, UPLOAD_FOLDER)

    file = request.files["file"]
    if file and allowed_file(file):
        ext = file.mimetype.split('/', 1)[1]
        filename = secrets.token_urlsafe(12) + '.' + ext
        path = os.path.join(session["uid"], filename)
        destination = os.path.join(target, path)

        # save data to database
        handler = ImageHandler(os.path.join(APP_ROOT, UPLOAD_FOLDER, session["uid"]))
        handler.add(path, title)

        # save file
        file.save(destination)

        return render_template("uploaded.html")
    else:
        return render_template("upload.html", error="File type not allowed")

@app.route("/uploads")
def send_image():
    path = request.args.get("path")
    if not path or '/' not in path:
        return None

    folder, filename = path.split('/', 1)
    filename = secure_filename(filename)
    if folder != "static" and folder != session["uid"]:
        return None

    target = os.path.join(APP_ROOT, UPLOAD_FOLDER, folder, filename)
    try:
        return send_file(target)
    except:
        return render_template("404.html"), 404

# URL defaults

@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    if endpoint == "static" or endpoint.endswith(".static"):
        filename = values.get("filename")
        if filename:
            if '.' in endpoint:  # has higher priority
                blueprint = endpoint.rsplit('.', 1)[0]
            else:
                blueprint = request.blueprint  # can be None too
            if blueprint:
                static_folder = app.blueprints[blueprint].static_folder
            else:
                static_folder = app.static_folder
            param_name = 'h'
            while param_name in values:
                param_name = '_' + param_name
            values[param_name] = static_file_hash(os.path.join(static_folder, filename))

# Error handling

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def file_size_limit(e):
    return render_template("413.html"), 413

if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT)
