# --------------------------------------------

# NAME / ROLL NUMBER
# AMOGH ANSHU N      22F1001411

# --------------------------------------------

# IIT-M BS 2023T3
# COURSE : BSCS2003P
# MODERN APPLICATION DEVELOPMENT I

# ----------------------------------------------

# MUSIC STREAMING APPLICATION


from flask import Flask, session, redirect, url_for, Response

from flask_restful import Resource, Api

from flask_sqlalchemy import SQLAlchemy

from flask import render_template
from flask import request

from flask import jsonify
from flask import flash
from models import *
import os
from flask_session import Session
from API import *

app = None
api = None


def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config['UPLOAD_DIR'] = 'uploads'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///identifier.sqlite3'
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    app.debug = True

    db.init_app(app)
    api = Api(app)
    Session(app)
    app.app_context().push()

    return app, api


app, api = create_app()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        admin_username = request.form['username']
        admin_password = request.form['password']
        if admin_username == "admin" and admin_password == "admin":
            session['user'] = "admin"
            session['user_id'] = 0000
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if session['user'] != "admin":
        return redirect(url_for('index'))
    if request.method == "POST":
        search = request.form['search']
        return redirect(url_for('admin_search', search=search))
    normal_users = AdminAPI.get_no_of_all_users()
    creators = AdminAPI.get_no_of_creators()
    tracks = AdminAPI.get_no_of_all_songs()
    albums = AdminAPI.get_no_of_all_albums()
    genre = AdminAPI.get_no_of_genre()
    path_of_song_vs_rating = AdminAPI.graph_of_popular_song()
    path_of_genre_vs_rating = AdminAPI.graph_of_popular_genre()
    path_of_user_vs_uploads = AdminAPI.graph_of_top_five_username_vs_uploads()
    path_of_user_vs_playlist = AdminAPI.graph_of_top_five_username_vs_playlist()

    return render_template('admin_dashboard.html', normal_user=normal_users,
                           creators=creators, number_of_songs=tracks, number_of_albums=albums, number_of_genre=genre,
                           path_of_song_vs_rating=path_of_song_vs_rating,
                           path_of_genre_vs_rating=path_of_genre_vs_rating,
                           path_of_user_vs_uploads=path_of_user_vs_uploads,
                           path_of_user_vs_playlist=path_of_user_vs_playlist)


@app.route('/admin/tracks', methods=['GET', 'POST'])
def admin_tracks():
    if session['user'] != "admin":
        return redirect(url_for('index'))
    if request.method == "POST":
        search = request.form['search']
        return redirect(url_for('admin_search', search=search))
    return render_template('admin_track.html', songs=MusicAPI.get_all())


@app.route('/admin/search/<search>/users/blacklist/<int:user_id>', methods=['GET', 'POST'])
def admin_search_blacklist(search, user_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    AdminAPI.blacklist_user(user_id)
    return redirect(url_for('admin_search', search=search))


@app.route('/admin/search/<search>/users/revoke/blacklist/<int:user_id>', methods=['GET', 'POST'])
def admin_search_revoke_blacklist_user(search, user_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    AdminAPI.revoke_blacklist_user(user_id)
    return redirect(url_for('admin_search', search=search))


@app.route('/admin/albums', methods=['GET', 'POST'])
def admin_albums():
    if session['user'] != "admin":
        return redirect(url_for('index'))
    return render_template('admin_albums.html', albums=AlbumAPI.get_all())


@app.route('/admin/users', methods=['GET', 'POST'])
def admin_users():
    if session['user'] != "admin":
        return redirect(url_for('index'))
    return render_template('admin_users.html', users=AdminAPI.get_all_users())


@app.route('/admin/search/<search>', methods=['GET', 'POST'])
def admin_search(search):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    if request.method == "POST":
        search = request.form['search']
        return redirect(url_for('admin_search', search=search))
    songs = SearchAPI.search_by_song_name(search)
    albums = SearchAPI.search_by_album_name(search)
    users1 = SearchAPI.search_by_username(search)
    users2 = SearchAPI.search_by_first_name_and_last_name(search)

    return render_template('admin_search.html', songs=songs, albums=albums, users1=users1, users2=users2, search=search)


@app.route('/admin/search/<search>/<int:song_id>/play', methods=['GET', 'POST'])
def admin_play_search(search, song_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    songs = SearchAPI.search_by_song_name(search)
    albums = SearchAPI.search_by_album_name(search)
    playlists = SearchAPI.search_by_playlist_name(search)
    path = MusicAPI.play(song_id)
    return render_template('search_results_play.html', path=path, songs=songs,
                           albums=albums, playlists=playlists)


@app.route('/admin/creators', methods=['GET', 'POST'])
def admin_creators():
    if session['user'] != "admin":
        return redirect(url_for('index'))
    return render_template('admin_creators.html', creators=AdminAPI.get_all_creators())


@app.route('/admin/users/blacklist/<int:user_id>', methods=['GET', 'POST'])
def admin_blacklist(user_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    AdminAPI.blacklist_user(user_id)
    return redirect(url_for('admin_users'))


@app.route('/admin/users/revoke/blacklist/<int:user_id>', methods=['GET', 'POST'])
def admin_revoke_blacklist_user(user_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    AdminAPI.revoke_blacklist_user(user_id)
    return redirect(url_for('admin_users'))


@app.route('/admin/creators/blacklist/<int:user_id>', methods=['GET', 'POST'])
def admin_blacklist_creator(user_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    AdminAPI.blacklist_creator(user_id)
    return redirect(url_for('admin_creators'))


@app.route('/admin/creators/revoke/blacklist/<int:user_id>', methods=['GET', 'POST'])
def admin_revoke_blacklist_creator(user_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    AdminAPI.revoke_blacklist_creator(user_id)
    return redirect(url_for('admin_creators'))


@app.route('/admin/song/delete/<int:song_id>', methods=['GET', 'POST'])
def delete_song_admin(song_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    MusicAPI.delete_song_admin(song_id)
    return redirect(url_for('admin_tracks'))


@app.route('/admin/album/delete/<int:album_id>', methods=['GET', 'POST'])
def delete_album_admin(album_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    AlbumAPI.delete(album_id, session['user'])
    return redirect(url_for('admin_albums'))


@app.route('/admin/user/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_user_admin(user_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    UserAPI.delete(user_id)
    return redirect(url_for('admin_users'))


@app.route('/admin/search/<search>/users/delete/<int:user_id>', methods=['GET', 'POST'])
def admin_search_delete(search, user_id):
    if session['user'] != "admin":
        return redirect(url_for('index'))
    UserAPI.delete(user_id)
    return redirect(url_for('admin_search', search=search))


@app.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
    session.pop('user', None)
    return render_template('index.html')


@app.route('/user/blacklisted', methods=['GET', 'POST'])
def user_blacklisted():
    return render_template('user_blacklisted.html')


@app.route('/creator/blacklisted', methods=['GET', 'POST'])
def creator_blacklisted():
    return render_template('creator_blacklisted.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        try:
            session['user_id'] = LoginAPI.get(request.form['username'], request.form['password'])
            session['user'] = LoginAPI.get_username(session['user_id'])
            flash("Logged in successfully.")
            return redirect(url_for('home'))
        except:
            return ("Invalid username or password")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        output = request.form.to_dict()
        result = UserAPI.post(output)
        if result:
            return redirect(url_for('post_registration'))
        else:
            return make_response('username is taken')

    return render_template('registration.html')


@app.route('/post/registration', methods=['GET', 'POST'])
def post_registration():
    return render_template('post_registration.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if request.method == "POST":
        search = request.form['search']
        # print(search)
        return redirect(url_for('search', search=search))
    recomended_tracks = MusicAPI.get_top_five_songs_by_rating()
    playlists = PlaylistAPI.get_by_user(session['user_id'])
    albums = AlbumAPI.get_first_five()

    return render_template('home.html', data=recomended_tracks, user_id=session['user_id'],
                           playlists=playlists, albums=albums, path=False)


@app.route('/home/play/<int:song_id>/', methods=['GET', 'POST'])
def play_song(song_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    path = MusicAPI.play(song_id)
    if request.method == "POST":
        search = request.form['search']
        return redirect(url_for('search', search=search))
    recomended_tracks = MusicAPI.get_top_five_songs_by_rating()
    playlists = PlaylistAPI.get_by_user(session['user_id'])
    albums = AlbumAPI.get_first_five()

    return render_template('home.html', data=recomended_tracks, user_id=session['user_id'],
                           playlists=playlists, albums=albums, path=path)


@app.route("/user", methods=['GET', 'POST'])
def user():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    user = UserAPI.get_by_id(session['user_id'])
    if request.method == "POST":
        user = {}
        user['username'] = request.form['username']
        user['first_name'] = request.form['first_name']
        user['last_name'] = request.form['last_name']
        user['password'] = request.form['password']
        UserAPI.update(user, session['user_id'])
        return redirect(url_for('user'))

    return render_template('user_account_edit.html', user=user)


@app.route("/user/delete", methods=['GET', 'POST'])
def delete_user():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    UserAPI.delete(session['user_id'])
    return redirect(url_for('index'))


@app.route('/song/<int:song_id>', methods=['GET', 'POST'])
def song(song_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    song = MusicAPI.get_by_id(song_id)
    flag = CreatorAPI.is_creator(session['user_id'], song_id)
    if request.method == "POST":
        rating = request.form['rating']
        MusicAPI.update_rating(song_id, rating)
        return redirect(url_for('song', song_id=song_id))
    return render_template('song_page.html', data=song, rating=MusicAPI.get_rating(song_id),
                           path=False, flag=not (flag), user=session['user'])


@app.route('/song/<int:song_id>/play', methods=['GET', 'POST'])
def play_song_by_id(song_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    path = MusicAPI.play(song_id)
    song = MusicAPI.get_by_id(song_id)
    flag = CreatorAPI.is_creator(session['user_id'], song_id)
    if request.method == "POST":
        rating = request.form['rating']
        MusicAPI.update_rating(song_id, rating)
        return redirect(url_for('play_song_by_id', song_id=song_id))
    return render_template('song_page.html', data=song,
                           rating=MusicAPI.get_rating(song_id), path=path, flag=not (flag), user=session['user'])


@app.route('/album/<int:album_id>', methods=['GET', 'POST'])
def album(album_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    album = AlbumAPI.get_by_id(album_id)
    return render_template('view_album.html', album_name=album.album_name,
                           songs=AlbumAPI.construct_list_of_song_dictionaries(album_id),
                           album_id=album.album_id, user=session['user'])


@app.route('/album/<int:album_id>/<int:song_id>/play', methods=['GET', 'POST'])
def play_album_by_song(song_id, album_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    path = MusicAPI.play(song_id)
    return render_template('view_album_play_by_song.html', path=path,
                           songs=AlbumAPI.construct_list_of_song_dictionaries(album_id),
                           album_id=album_id, album_name=AlbumAPI.get_by_id(album_id).album_name,
                           user=session['user'])


@app.route('/all/albums', methods=['GET', 'POST'])
def all_albums():
    albums = AlbumAPI.get_all()
    return render_template('search_results.html', albums=albums)


@app.route('/playlist/<int:playlist_id>', methods=['GET', 'POST'])
def playlist_by_id(playlist_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    print('received request')
    playlist = PlaylistAPI.get_by_id(playlist_id)
    print(playlist)
    return render_template('view_playlist.html', playlist_name=playlist.playlist_name,
                           songs=PlaylistAPI.construct_list_of_song_dictionaries(playlist_id),
                           playlist_id=playlist.playlist_id, )


@app.route('/playlist/<int:playlist_id>/<int:song_id>/play', methods=['GET', 'POST'])
def play_playlist_by_song(song_id, playlist_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    path = MusicAPI.play(song_id)
    return render_template('view_playlist_play_by_song.html', path=path,
                           songs=PlaylistAPI.construct_list_of_song_dictionaries(playlist_id),
                           playlist_id=playlist_id, playlist_name=PlaylistAPI.get_by_id(playlist_id).playlist_name)


@app.route('/create/playlist', methods=['GET', 'POST'])
def create_playlist():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if request.method == "POST":
        out = {}
        out['playlist_name'] = request.form['playlist_name']
        out['user_id'] = session['user_id']
        out_song_id_list = request.form.getlist('song_id')
        out_song_id_str = ' '.join([str(elem) for elem in out_song_id_list])
        out['song_id'] = out_song_id_str
        # return (out)
        PlaylistAPI.post(out)
        return redirect(url_for('home'))
    else:
        songs = MusicAPI.get_all()
        return render_template('create_playlist.html', songs=songs)


@app.route('/playlist/edit/<int:playlist_id>', methods=['GET', 'POST'])
def edit_playlist(playlist_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    playlist = PlaylistAPI.get_by_id(playlist_id)
    if request.method == "POST":
        out = {}
        if request.form['playlist_name']:
            out['playlist_name'] = request.form['playlist_name']
        else:
            out['playlist_name'] = playlist.playlist_name
        out_song_id_list = request.form.getlist('song_id')
        out_song_id_str = ' '.join([str(elem) for elem in out_song_id_list])
        out['song_id'] = out_song_id_str
        PlaylistAPI.update(out, playlist_id)
        return redirect(url_for('playlist_by_id', playlist_id=playlist_id))
    else:
        songs = MusicAPI.get_all()
        return render_template('edit_playlist.html', playlist=playlist,
                               playlist_songs=PlaylistAPI.construct_list_of_song_dictionaries(playlist_id),
                               non_playlist_songs=PlaylistAPI.construct_list_of_song_dictionaries_not_in_playlist(
                                   playlist_id))


@app.route('/playlist/delete/<int:playlist_id>', methods=['GET', 'POST'])
def delete_playlist(playlist_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    PlaylistAPI.delete(playlist_id, session['user_id'])
    return redirect(url_for('home'))


@app.route('/creator/', methods=['GET', 'POST'])
def creator():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    if CreatorAPI.creator_status(session['user_id']):
        return redirect(url_for('creator_dashboard'))
    return redirect(url_for('creator_register'))


@app.route('/upload/song', methods=['GET', 'POST'])
def upload_song():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    if request.method == "POST":
        out = request.form.to_dict()
        out['user_id'] = session['user_id']
        MusicAPI.post(out, request.files['song'])
        return redirect(url_for('creator_dashboard'))

    return render_template('upload-song.html')


@app.route('/creator/song/edit/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    song = MusicAPI.get_by_id(song_id)
    if request.method == "POST":
        out = request.form.to_dict()
        out['user_id'] = session['user_id']
        MusicAPI.update(out, song_id)
        return redirect(url_for('creator_dashboard', song_id=song_id))
    return render_template('edit_song.html', song=song)


@app.route('/creator/song/delete/<int:song_id>', methods=['GET', 'POST'])
def delete_song(song_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    MusicAPI.delete_song(song_id, session['user_id'])
    return redirect(url_for('creator_dashboard'))


@app.route('/creator/register/', methods=['GET', 'POST'])
def creator_register():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    if request.method == "POST":
        CreatorAPI.become_creator(session['user_id'])
        return render_template('start_creator.html')

    return render_template('creator_register.html')


@app.route('/creator/dashboard', methods=['GET', 'POST'])
def creator_dashboard():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    if CreatorAPI.get_no_of_songs(session['user_id']) == 0:
        return render_template('start_creator.html')

    return render_template('creator_dashboard.html', n=CreatorAPI.get_no_of_songs(session['user_id']),
                           songs=MusicAPI.get_by_creator(session['user_id']),
                           r=CreatorAPI.get_avg_rating(session['user_id']),
                           a=CreatorAPI.get_no_of_albums(session['user_id']),
                           albums=AlbumAPI.get_by_creator(session['user_id']))


@app.route('/creator/create_album', methods=['GET', 'POST'])
def create_album():
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    if request.method == "POST":
        out = {}
        out['album_name'] = request.form['album_name']
        out_song_id_list = request.form.getlist('song_id')
        out_song_id_str = ' '.join([str(elem) for elem in out_song_id_list])
        out['song_id'] = out_song_id_str
        AlbumAPI.post(out, session['user_id'])
        return redirect(url_for('creator_dashboard'))
    else:
        songs = MusicAPI.get_by_creator(session['user_id'])
        return render_template('create_album.html', songs=songs)


@app.route('/creator/album/edit/<int:album_id>', methods=['GET', 'POST'])
def edit_album(album_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    album = AlbumAPI.get_by_id(album_id)
    if request.method == "POST":
        out = {}
        if request.form['album_name']:
            out['album_name'] = request.form['album_name']
        else:
            out['album_name'] = album.album_name
        out_song_id_list = request.form.getlist('song_id')
        out_song_id_str = ' '.join([str(elem) for elem in out_song_id_list])
        out['song_id'] = out_song_id_str
        AlbumAPI.update(out, album_id)
        return redirect(url_for('creator_dashboard'))
    else:
        songs = MusicAPI.get_by_creator(session['user_id'])
        album_songs = AlbumAPI.construct_list_of_song_dictionaries(album_id)
        non_album_songs = AlbumAPI.construct_list_of_song_dictionaries_not_in_album(album_id)
        # print(album_songs)
        # print(non_album_songs)
        return render_template('edit_album.html', album=album,
                               album_songs=album_songs,
                               non_album_songs=non_album_songs)


@app.route('/creator/album/delete/<int:album_id>', methods=['GET', 'POST'])
def delete_album(album_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if AdminAPI.blacklist_status_creator(session['user_id']):
        return redirect(url_for('creator_blacklisted'))
    AlbumAPI.delete(album_id, session['user_id'])
    return redirect(url_for('creator_dashboard'))


@app.route('/search/<search>', methods=['GET', 'POST'])
def search(search):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if request.method == "POST":
        search = request.form['search']
        return redirect(url_for('search', search=search))
    songs = SearchAPI.search_by_song_name(search)
    albums = SearchAPI.search_by_album_name(search)
    playlists = SearchAPI.search_by_playlist_name(search)
    return render_template('search_results.html', songs=songs, albums=albums,
                           playlists=playlists, search=search)


@app.route('/search/<search>/play/<int:song_id>', methods=['GET', 'POST'])
def play_search(search, song_id):
    if AdminAPI.blacklist_status_user(session['user_id']):
        return redirect(url_for('user_blacklisted'))
    if request.method == "POST":
        search = request.form['search']
        return redirect(url_for('search', search=search))
    songs = SearchAPI.search_by_song_name(search)
    albums = SearchAPI.search_by_album_name(search)
    playlists = SearchAPI.search_by_playlist_name(search)
    path = MusicAPI.play(song_id)
    return render_template('search_results_play.html', path=path, songs=songs,
                           albums=albums, playlists=playlists, search=search)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'

    app.run(port=9000)
