from flask import Flask, request, redirect, session, render_template, Response
from werkzeug import secure_filename

import memeMatcher

import os
import json
import sqlite3


app = Flask(__name__)

def lookup_by_song_id(song_id):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute("SELECT * from upload WHERE id=?", (song_id, ))
    filename = cur.fetchone()[1]
    return base_path() + "/tmp/" + filename

def memes(song_file):
    print song_file
    a = memeMatcher.memeMatcher(song_file).select_and_align_memes()
    print a
    return [
                {
                    "image_url": "static/img/all_the_things.png",
                    "transition_after": 6000,
                    "top_text": "Like the legend of the pheonix",
                    "bottom_text": "All ends with beginnings",
                },
                {
                    "image_url": "static/img/doge.jpg",
                    "transition_after": 7000,
                    "top_text": "What keeps the planet spinning",
                    "bottom_text": "The force of love beginning",
                },
                {
                    "image_url": "static/img/confession_bear.jpg",
                    "transition_after": 10000,
                    "top_text": "We've come too far to give up who we are",
                    "bottom_text": "So let's raise the bar and our cups to the star",
                }
            ]

def intro_time(song_file):
    return 1000

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

def favourite_tracks():
    ids = [1]
    results = []
    for oid in ids:
        song_file = lookup_by_song_id(oid)
        a = memeMatcher.memeMatcher(song_file)
        artist = a.artist
        title = a.title
        results.append({"id": oid, "artist": artist, "title":title})

    return results

@app.route("/")
def hello():
    database_connection()
    return read_template("index.html",
            {
                "error": session.get("error", None),
                "favourites": favourite_tracks(),
            })

@app.route("/audio_files/<file_name>")
def play_song(file_name):
    #TODO: correct mime type
    return Response(open(base_path() + "/tmp/" + file_name).read(), mimetype='audio/mpeg')

@app.route("/upload", methods=["POST"])
def upload():
    print request.files
    session["error"] = None
    uploaded_file = request.files['file']
    if allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)
        song_path = base_path() + "/tmp/" + filename
        uploaded_file.save(song_path)
        session["song_path"] = song_path
        conn = database_connection()
        cur = conn.cursor()
        cur.execute("SELECT * from upload WHERE file_name=?", (filename, ))

        row = cur.fetchone()
        if not cur.fetchone():
            cur.execute("INSERT INTO upload (file_name) values(?)", (filename,))
            conn.commit()
            cur.execute("SELECT id from upload WHERE file_name=?", (filename,))
            row = cur.fetchone()
            song_id = str(row[0])
        else:
            song_id = str(row[0])

        return redirect("/player?song_id=" + str(song_id))

    session["error"] = "uploaded file of wrong type"
    return redirect("/")

@app.route("/player", methods=["GET"])
def player():
    song_path = lookup_by_song_id(request.args.get("song_id"))
    http_song_path = "/audio_files/" + os.path.split(song_path)[-1]
    return read_template("player.html", {
        "song_path": http_song_path,
        "mime_type": "audio/mpeg",
        "memes":json.dumps(memes(song_path)),
        "intro_time": intro_time(open(song_path)),
    })

if __name__ == "__main__":
    upload_folder = base_path() + "/tmp/"
    UPLOAD_FOLDER = ''
    ALLOWED_EXTENSIONS = set(["mp3", "wav", "ogg", "m4a"])
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = "adofijqweofijsdfklgjasdflidqogjwiodf:w"
    app.debug = True
    app.run()
