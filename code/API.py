from flask import Flask, jsonify, request, abort, make_response
from werkzeug.exceptions import HTTPException
from flask import make_response
from flask import flash
from flask_restful import Resource, Api, reqparse
import os
from app import *
import matplotlib.pyplot as plt
from models import *
import pandas as pd
import numpy as np

class LoginAPI:
    @staticmethod
    def get(username, password):
        user = User.query.filter_by(username=username).first()
        if user is None or not user.password == password:
            raise ('Invalid username or password')
            # return None
        return user.user_id

    @staticmethod
    def get_username(user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            abort(404)
        return user.username


class MusicAPI(Music):
    @staticmethod
    def play(song_id):
        song = Music.query.filter_by(song_id=song_id).first()
        # print(song.song)
        if song is None:
            # print("if")
            abort(404)
        elif song:
            # temp=os.path.join(app.config['UPLOAD_DIR'], str(song.song_id)+'.mp3')
            temp = 'static/' + str(song.song_id) + '.mp3'
            # print(temp)
            with open(temp, 'wb') as file:
                file.write(song.song)
                # print ('done writing')
            return temp
        else:
            return jsonify("fail")

    @staticmethod
    def get_top_five_songs_by_rating():
        songs = Music.query.all()
        songs.sort(key=lambda x: MusicAPI.get_rating(x.song_id), reverse=True)
        top_five=[]
        for i in range(5):
            top_five.append(songs[i])
        return top_five

    @staticmethod
    def get_all():
        song = db.session.query(Music).all()
        if song is None:
            abort(404)
        return song

    @staticmethod
    def get_first_five(num=5):
        song = db.session.query(Music).limit(num).all()
        if song is None:
            abort(404)
        return song

    @staticmethod
    def get_by_id(song_id):
        song = Music.query.filter_by(song_id=song_id).first()
        if song is None:
            abort(404)
        return song

    @staticmethod
    def get_by_creator(user_id):
        song = Music.query.filter_by(user_id=user_id).all()
        if song is None:
            abort(404)
        return song

    @staticmethod
    def get_by_genre(genre, num=5):
        song = Music.query.filter_by(genre=genre).limit(num).all()
        if song is None:
            abort(404)
        return song

    @staticmethod
    def delete_song(song_id, user_id):
        song = Music.query.filter_by(song_id=song_id, user_id=user_id).first()
        if song is None:
            abort(404)
        db.session.delete(song)
        db.session.commit()
        return jsonify("Song deleted")

    @staticmethod
    def delete_song_admin(song_id):
        song = Music.query.filter_by(song_id=song_id).first()
        if song is None:
            abort(404)
        db.session.delete(song)
        db.session.commit()
        return jsonify("Song deleted")

    def post(self, file):
        post_query = db.session.query(Music).filter(
            (Music.song_name == self['song_name']) & (Music.user_id == self['user_id'])).first()
        if post_query:
            return make_response(jsonify("Song already exists"), 409)
        else:
            song = file
            song.save(os.path.join(app.config['UPLOAD_DIR'], song.filename))
            with open(os.path.join(app.config['UPLOAD_DIR'], song.filename), 'rb') as f:
                song_blob = f.read()
            music = Music(user_id=self['user_id'], song_name=self['song_name'], song_lyrics=self['song_lyrics'],
                          genre=self['genre'], singer=self['singer'], song=song_blob, rating='0', year=self['year'])
            db.session.add(music)
            db.session.commit()
            os.remove(os.path.join(app.config['UPLOAD_DIR'], song.filename))
            return jsonify("Song added")

    def update(self, song_id):
        put_query = db.session.query(Music).filter(Music.song_id == song_id).first()
        if put_query:
            put_query.user_id = self['user_id']
            put_query.song_name = self['song_name']
            put_query.song_lyrics = self['song_lyrics']
            put_query.genre = self['genre']
            put_query.year = self['year']
            put_query.singer = self['singer']
            db.session.commit()
            return jsonify("Song updated")
        else:
            return make_response(jsonify("Song does not exist"), 404)

    @staticmethod
    def put(song_id, user_id, song_name, song_lyrics, genre, song, rating, year, singer):
        put_query = db.session.query(Music).filter(Music.song_id == song_id).first()
        if put_query:
            put_query.user_id = user_id
            put_query.song_name = song_name
            put_query.song_lyrics = song_lyrics
            put_query.genre = genre
            put_query.song = song
            put_query.rating = rating
            put_query.year = year
            put_query.singer = singer
            db.session.commit()
            return jsonify("Song updated")
        else:
            return make_response(jsonify("Song does not exist"), 404)

    @staticmethod
    def get_rating(song_id):
        query = db.session.query(Music).filter(Music.song_id == song_id).first()
        rating_list = query.rating.split(' ')
        # print(rating_list)
        int_rating_list = []
        for x in rating_list:
            int_rating_list.append(int(x))
            # print(x)
        if sum(int_rating_list) == 0:
            return 0
        else:
            rating = sum(int_rating_list) / len(int_rating_list)
            return int(rating)

    @staticmethod
    def update_rating(song_id, rating):
        query = db.session.query(Music).filter(Music.song_id == song_id).first()
        query.rating = query.rating + ' ' + str(rating)
        db.session.commit()


class UserAPI(User):
    def post(self):
        post_query = db.session.query(User).filter(User.username == self['username']).first()
        if post_query:
            return False
        else:
            user = User(username=self['username'], first_name=self['first_name'], last_name=self['last_name'],
                        password=self['password'], creator_status=0, blacklist=0)
            db.session.add(user)
            db.session.commit()
            return True

    def update(self, user_id):
        put_query = db.session.query(User).filter(User.user_id == user_id).first()
        if put_query:
            put_query.username = self['username']
            put_query.password = self['password']
            put_query.first_name = self['first_name']
            put_query.last_name = self['last_name']
            db.session.commit()
            return jsonify("User updated")
        else:
            return make_response(jsonify("User does not exist"), 404)

    @staticmethod
    def delete(user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            abort(404)
        db.session.delete(user)
        db.session.commit()
        return jsonify("User deleted")

    @staticmethod
    def get_by_id(user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            abort(404)
        return user


class CreatorAPI:

    @staticmethod
    def is_creator(user_id, song_id):
        song = Music.query.filter_by(song_id=song_id).first()
        if song.user_id == user_id:
            return True
        else:
            return False

    @staticmethod
    def become_creator(user_id):
        patch_query = db.session.query(User).filter(User.user_id == user_id).first()
        if patch_query:
            patch_query.creator_status = 1
            db.session.commit()

    @staticmethod
    def get_no_of_songs(user_id):
        song = Music.query.filter_by(user_id=user_id).count()
        return song

    @staticmethod
    def get_no_of_albums(user_id):
        album = Album.query.filter_by(user_id=user_id).count()
        return album

    @staticmethod
    def get_avg_rating(user_id):
        song = Music.query.filter_by(user_id=user_id).all()
        rating = 0
        for x in song:
            rating += MusicAPI.get_rating(x.song_id)
        rating = rating / len(song)
        return rating

    @staticmethod
    def remove_creator(user_id):
        patch_query = db.session.query(User).filter(User.user_id == user_id).first()
        if patch_query:
            patch_query.creator_status = 0
            db.session.commit()

    @staticmethod
    def creator_status(user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if user.creator_status == 1:
            return True
        else:
            return False


class PlaylistAPI(Playlist):
    def post(self):
        post_query = db.session.query(Playlist).filter(
            (Playlist.playlist_name == self['playlist_name']) & (Playlist.user_id == self['user_id'])).first()
        if post_query:
            return make_response(jsonify("Playlist already exists"), 409)
        else:
            user_id = self['user_id']
            playlist_name = self['playlist_name']
            song_id = self['song_id']
            playlist = Playlist(user_id=user_id, playlist_name=playlist_name, song_id=song_id)
            db.session.add(playlist)
            db.session.commit()
            return ("Playlist added")

    def update(self, playlist_id):
        put_query = db.session.query(Playlist).filter(Playlist.playlist_id == playlist_id).first()
        if put_query:
            put_query.playlist_name = self['playlist_name']
            put_query.song_id = self['song_id']
            db.session.commit()
            return jsonify("Playlist updated")
        else:
            return make_response(jsonify("Playlist does not exist"), 404)

    @staticmethod
    def delete(playlist_id, user_id):
        playlist = Playlist.query.filter_by(playlist_id=playlist_id, user_id=user_id).first()
        if playlist is None:
            abort(404)
        db.session.delete(playlist)
        db.session.commit()
        return jsonify("Playlist deleted")

    @staticmethod
    def get_by_user(user_id):
        playlist = Playlist.query.filter_by(user_id=user_id).all()
        if playlist is None:
            abort(404)
        return playlist

    @staticmethod
    def get_by_id(playlist_id):
        playlist = Playlist.query.filter_by(playlist_id=playlist_id).first()
        if playlist is None:
            abort(404)
        return playlist

    @staticmethod
    def construct_list_of_song_dictionaries(playlist_id):
        playlist = Playlist.query.filter_by(playlist_id=playlist_id).first()
        song_id_list = playlist.song_id.split(' ')
        list_of_song_dict = []
        for song_id in song_id_list:
            song_dict = {}
            song = MusicAPI.get_by_id(song_id)
            song_dict['song_id'] = song.song_id
            song_dict['song_name'] = song.song_name
            song_dict['song_lyrics'] = song.song_lyrics
            song_dict['genre'] = song.genre
            song_dict['song'] = song.song
            song_dict['rating'] = song.rating
            song_dict['year'] = song.year
            song_dict['singer'] = song.singer
            list_of_song_dict.append(song_dict)

        return list_of_song_dict

    @staticmethod
    def construct_list_of_song_dictionaries_not_in_playlist(playlist_id):
        playlist = Playlist.query.filter_by(playlist_id=playlist_id).first()
        list_of_songs_in_playlist = playlist.song_id.split(' ')
        list_of_all_songs = MusicAPI.get_all()
        list_of_song_dict = []
        for song in list_of_all_songs:
            if str(song.song_id) not in list_of_songs_in_playlist:
                song_dict = {}
                song_dict['song_id'] = song.song_id
                song_dict['song_name'] = song.song_name
                song_dict['song_lyrics'] = song.song_lyrics
                song_dict['genre'] = song.genre
                song_dict['song'] = song.song
                song_dict['rating'] = song.rating
                song_dict['year'] = song.year
                song_dict['singer'] = song.singer
                list_of_song_dict.append(song_dict)

        return list_of_song_dict


class AlbumAPI(Album):
    @staticmethod
    def get_all():
        album = db.session.query(Album).all()
        if album is None:
            abort(404)
        return album

    @staticmethod
    def get_first_five(num=5):
        album = db.session.query(Album).limit(num).all()
        if album is None:
            abort(404)
        return album

    def post(self, user_id):
        post_query = db.session.query(Album).filter(Album.album_name == self['album_name']).first()
        if post_query:
            return make_response(jsonify("Album already exists"), 409)
        else:
            album_name = self['album_name']
            song_id = self['song_id']
            album = Album(user_id=user_id, album_name=album_name, song_id=song_id)
            db.session.add(album)
            db.session.commit()
            return jsonify("Album added")

    def update(self, album_id):
        put_query = db.session.query(Album).filter(Album.album_id == album_id).first()
        if put_query:
            put_query.album_name = self['album_name']
            put_query.song_id = self['song_id']
            db.session.commit()
            return jsonify("Album updated")
        else:
            return make_response(jsonify("Album does not exist"), 404)

    @staticmethod
    def delete(album_id, param):
        album = Album.query.filter_by(album_id=album_id).first()
        if album is None:
            abort(404)

        if album.user_id == param or param == 'admin':
            db.session.delete(album)
            db.session.commit()
            return jsonify("Album deleted")
        else:
            return make_response(jsonify("You are not the creator of this album"), 404)

    @staticmethod
    def get_by_id(album_id):
        album = Album.query.filter_by(album_id=album_id).first()
        if album is None:
            abort(404)
        return album

    @staticmethod
    def get_by_creator(user_id):
        album = Album.query.filter_by(user_id=user_id).all()
        if album is None:
            abort(404)
        return album

    @staticmethod
    def construct_list_of_song_dictionaries(album_id):
        album = Album.query.filter_by(album_id=album_id).first()
        song_id_list = album.song_id.split(' ')
        list_of_song_dict = []
        for song_id in song_id_list:
            song_dict = {}
            song = MusicAPI.get_by_id(song_id)
            song_dict['song_id'] = song.song_id
            song_dict['song_name'] = song.song_name
            song_dict['song_lyrics'] = song.song_lyrics
            song_dict['genre'] = song.genre
            song_dict['song'] = song.song
            song_dict['rating'] = song.rating
            song_dict['year'] = song.year
            song_dict['singer'] = song.singer
            list_of_song_dict.append(song_dict)

        return list_of_song_dict

    @staticmethod
    def construct_list_of_song_dictionaries_not_in_album(album_id):
        album = Album.query.filter_by(album_id=album_id).first()
        list_of_songs_in_album = album.song_id.split(' ')
        list_of_all_songs_by_creator = MusicAPI.get_by_creator(album.user_id)
        list_of_song_dict = []
        for song in list_of_all_songs_by_creator:
            if str(song.song_id) not in list_of_songs_in_album:
                song_dict = {}
                song_dict['song_id'] = song.song_id
                song_dict['song_name'] = song.song_name
                song_dict['song_lyrics'] = song.song_lyrics
                song_dict['genre'] = song.genre
                song_dict['song'] = song.song
                song_dict['rating'] = song.rating
                song_dict['year'] = song.year
                song_dict['singer'] = song.singer
                list_of_song_dict.append(song_dict)

        return list_of_song_dict


class AdminAPI:

    @staticmethod
    def get_all_users():
        user = User.query.all()
        # print(user)
        if user is None:
            abort(404)
        return user

    @staticmethod
    def get_all_creators():
        user = User.query.filter_by(creator_status=1).all()
        if user is None:
            abort(404)
        return user

    @staticmethod
    def get_no_of_all_users():
        if User.query.all() is None:
            return ("0")
        else:
            user = User.query.all()
            # print(user)
            # print(len(user))
            return (len(user))

    @staticmethod
    def get_no_of_all_songs():
        if Music.query.all() is None:
            return ("0")
        else:
            song = Music.query.all()
            # print(len(song))
            return (len(song))

    @staticmethod
    def get_no_of_creators():
        creator_status = 1
        if User.query.filter_by(creator_status=creator_status).all() is None:
            return ("0")
        else:
            user = User.query.filter_by(creator_status=creator_status).all()
            # print(len(user))
            return (len(user))

    @staticmethod
    def get_no_of_all_albums():
        if Album.query.all() is None:
            return ("0")
        else:
            album = Album.query.all()
            # print(len(album))
            return (len(album))

    @staticmethod
    def get_no_of_genre():
        if MusicAPI.get_all() is None:
            return ("0")
        else:
            songs = MusicAPI.get_all()
            l=[]
            for song in songs:
                l.append(song.genre)
            l=np.array(l)
            x=pd.unique(l)
            return (len(x))

    @staticmethod
    def graph_of_popular_song():
        songs = MusicAPI.get_top_five_songs_by_rating()
        x = []
        y = []
        for song in songs:
            x.append(song.song_name)
            y.append(MusicAPI.get_rating(song.song_id))
        # x.reverse()
        # y.reverse()

        plt.bar(x, y)
        plt.xlabel('Song')
        plt.ylabel('Rating')
        plt.title('Top 5 songs with most ratings')
        plt.savefig('static/plot_of_song_vs_rating.png', dpi=70, bbox_inches='tight')
        plt.close()
        return ("static/plot_of_song_vs_rating.png")

    @staticmethod
    def graph_of_popular_genre():
        songs = MusicAPI.get_top_five_songs_by_rating()
        a = []
        b = []
        for song in songs:
            a.append(song.genre)
            b.append(MusicAPI.get_rating(song.song_id))
        plt.bar(a, b, color='green')
        plt.xlabel('Genre')
        plt.ylabel('Rating')
        plt.title('Top 5 genres with most ratings')
        plt.savefig('static/plot_of_genre_vs_rating.png', dpi=70, bbox_inches='tight')
        plt.close()
        return ("static/plot_of_genre_vs_rating.png")

    @staticmethod
    def graph_of_top_five_username_vs_uploads():
        users = User.query.all()
        l = []
        for user in users:
            class New():
                def __init__(self, username, song_uploads):
                    self.username = username
                    self.song_uploads = song_uploads

            songs = Music.query.filter_by(user_id=user.user_id).all()
            e = New(song_uploads=len(songs), username=user.username)
            l.append(e)
        l.sort(key=lambda x: x.song_uploads, reverse=True)

        c = []
        d = []
        for i in range(5):
            c.append(l[i].username)
            d.append(l[i].song_uploads)

        plt.bar(c, d, color='red')
        plt.xlabel('Username')
        plt.ylabel('No of songs uploaded')
        plt.title('Top 5 creators with most songs uploaded')
        plt.savefig('static/plot_of_user_vs_uploads.png', dpi=70, bbox_inches='tight')
        plt.close()
        return ("static/plot_of_user_vs_uploads.png")

    @staticmethod
    def graph_of_top_five_username_vs_playlist():
        users = User.query.all()
        m = []
        for user in users:
            playlists = Playlist.query.filter_by(user_id=user.user_id).all()

            class graph():
                def __init__(self, username, playlist_count):
                    self.username = username
                    self.playlist_count = playlist_count

            z = graph(username=user.username, playlist_count=len(playlists))
            m.append(z)
        m.sort(key=lambda y: y.playlist_count, reverse=True)

        f = []
        g = []
        for i in range(5):
            f.append(m[i].username)
            g.append(m[i].playlist_count)

        plt.bar(f, g, color='cyan')
        plt.xlabel('Username')
        plt.ylabel('No of playlists')
        plt.title('Top 5 users with most playlists')
        plt.savefig('static/plot_of_user_vs_playlist.png', dpi=70, bbox_inches='tight')
        plt.close()
        return ("static/plot_of_user_vs_playlist.png")

    @staticmethod
    def blacklist_creator(user_id):
        patch_query = db.session.query(User).filter(User.user_id == user_id).first()
        if patch_query:
            patch_query.blacklist += 1
            db.session.commit()

    @staticmethod
    def blacklist_user(user_id):
        patch_query = db.session.query(User).filter(User.user_id == user_id).first()
        if patch_query:
            patch_query.blacklist += 2
            db.session.commit()

    @staticmethod
    def blacklist_status_user(user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if session['user'] == 'admin':
            return False
        if user.blacklist >= 2:
            return True
        else:
            return False

    @staticmethod
    def blacklist_status_creator(user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if session['user'] == 'admin':
            return False
        if user.blacklist >= 1:
            return True
        else:
            return False

    @staticmethod
    def revoke_blacklist_user(user_id):
        patch_query = db.session.query(User).filter(User.user_id == user_id).first()
        if patch_query:
            patch_query.blacklist -= 2
            db.session.commit()

    @staticmethod
    def revoke_blacklist_creator(user_id):
        patch_query = db.session.query(User).filter(User.user_id == user_id).first()
        if patch_query:
            patch_query.blacklist -= 1
            db.session.commit()


class SearchAPI:
    @staticmethod
    def search_by_song_name(song_name):
        song = Music.query.filter(Music.song_name.like('%' + song_name + '%')).all()
        if song is None:
            return False
        return song

    @staticmethod
    def search_by_singer(singer):
        song = Music.query.filter(Music.singer.like('%' + singer + '%')).all()
        if song is None:
            return False
        return song

    @staticmethod
    def search_by_genre(genre):
        song = Music.query.filter(Music.genre.like('%' + genre + '%')).all()
        if song is None:
            return False
        return song

    @staticmethod
    def search_by_year(year):
        song = Music.query.filter_by(year=year).all()
        if song is None:
            return False
        return song

    @staticmethod
    def search_by_album_name(album_name):
        album = Album.query.filter(Album.album_name.like('%' + album_name + '%')).all()
        if album is None:
            return False
        return album

    @staticmethod
    def search_by_playlist_name(playlist_name):
        playlist = Playlist.query.filter(Playlist.playlist_name.like('%' + playlist_name + '%')).all()
        if playlist is None:
            return False
        return playlist

    @staticmethod
    def search_by_username(username):
        user = User.query.filter(User.username.like('%' + username + '%')).all()
        if user is None:
            return False
        return user

    @staticmethod
    def search_by_first_name_and_last_name(name):
        user = User.query.filter(User.first_name.like('%' + name + '%') | User.last_name.like('%' + name + '%')).all()
        if user is None:
            return False
        return user
