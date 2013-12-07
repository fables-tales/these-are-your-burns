from flask import Flask, request, redirect, session, render_template, Response
from werkzeug import secure_filename

import os
import json
import sqlite3


app = Flask(__name__)

def memes(song_path):
    return [
                {
                    "image_url": "static/img/all_the_things.png",
                    "transition_after": 5000,
                    "top_text": "Music",
                    "bottom_text": "All the things",
                },
                {
                    "image_url": "static/img/all_the_things.png",
                    "transition_after": 3000,
                    "top_text": "mus",
                    "bottom_text": "sux",
                }
            ]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def base_path():
    return os.path.dirname(os.path.realpath(__file__))

def read_template(template_name, params={}):
    return render_template(template_name, **params)

def database_connection():
    if not os.path.isfile('db/app.db'):
        raise "YOUR DATABASE DOESNT EXIST FOOL, RUN db/migrate.sh"

    return sqlite3.connect('db/app.db')

@app.route("/")
def hello():
    database_connection()
    return read_template("index.html", {"error": session.get("error", None)})

@app.route("/audio_files/<file_name>")
def play_song(file_name):
    #TODO: correct mime type
    return Response(open(base_path() + "/tmp/" + file_name).read(), mimetype='audio/mpeg')

@app.route("/upload", methods=["POST"])
def upload():
    session["error"] = None
    uploaded_file = request.files['file']
    if allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        song_path = base_path() + "/tmp/" + filename
        uploaded_file.save(song_path)
        session["song_path"] = song_path
        return redirect("/player")

    session["error"] = "uploaded file of wrong type"
    return redirect("/")

@app.route("/player", methods=["GET"])
def player():
    song_path = session["song_path"]
    http_song_path = "/audio_files/" + os.path.split(session["song_path"])[-1]
    return read_template("player.html", {
        "song_path": http_song_path,
        "mime_type": "audio/mpeg",
        "memes":json.dumps(memes(open(song_path)))
    })

if __name__ == "__main__":
    upload_folder = base_path() + "/tmp/"
    UPLOAD_FOLDER = ''
    ALLOWED_EXTENSIONS = set(["mp3", "wav", "ogg", "m4a"])
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = "adofijqweofijsdfklgjasdflidqogjwiodf:w"
    app.debug = True
    app.run()
