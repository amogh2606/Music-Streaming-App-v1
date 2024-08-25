from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    creator_status = db.Column(db.Integer, nullable=False)
    blacklist = db.Column(db.Integer, nullable=False)


class Music(db.Model):
    song_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    song_name = db.Column(db.String, nullable=False)
    song_lyrics = db.Column(db.String)
    genre = db.Column(db.String)
    song = db.Column(db.BLOB, nullable=False)
    rating = db.Column(db.String)
    year = db.Column(db.Integer, nullable=False)
    singer = db.Column(db.String)


class Album(db.Model):
    album_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    song_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    album_name = db.Column(db.String, nullable=False)


class Playlist(db.Model):
    playlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    song_id = db.Column(db.String, nullable=False)
    playlist_name = db.Column(db.String, nullable=False)
