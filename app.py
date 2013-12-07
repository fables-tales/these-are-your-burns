from flask import Flask, request
from werkzeug import secure_filename

import os
import sqlite3

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def base_path():
    return os.path.dirname(os.path.realpath(__file__))

def read_template(template_name):
    return open(base_path() + "/templates/" + template_name).read()

def database_connection():
    if not os.path.isfile('db/app.db'):
        raise "YOUR DATABASE DOESNT EXIST FOOL, RUN db/migrate.sh"

    return sqlite3.connect('db/app.db')

@app.route("/")
def hello():
    database_connection()
    return read_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files['file']
    print request.files
    print uploaded_file
    print allowed_file(uploaded_file.filename)
    if allowed_file(uploaded_file.filename):
        print "here"
        filename = secure_filename(uploaded_file.filename)
        print "------------------------"
        print filename
        print os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(base_path() + "/tmp/" + filename)
        print "saving!!!!!!!"

    return "pony swag!"


if __name__ == "__main__":
    upload_folder = base_path() + "/tmp/"
    UPLOAD_FOLDER = ''
    ALLOWED_EXTENSIONS = set(["mp3", "wav", "ogg"])
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.debug = True
    app.run()
