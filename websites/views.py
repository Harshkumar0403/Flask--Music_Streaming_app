import os
import io
import base64
import matplotlib.pyplot as plt
from flask import Blueprint, Flask, request, redirect, flash, url_for
from flask import render_template
from flask_login import login_required, current_user,login_user,logout_user
from websites.auth import signinForm,loginForm,AdminloginForm,PlaylistForm
from websites import db
from sqlalchemy.sql import func
from websites.models import User,Album,Song,Playlist,playlist_association
import bcrypt
from . import create_app
from werkzeug.utils import secure_filename
from flask import current_app

view=Blueprint('views',__name__)

@view.route('/')
def index():
    return render_template('base.html',title='Home Page')

@view.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    form=loginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'),user.password.encode('utf-8')):
            login_user(user)
            flash (f'Login successful for {form.email.data}',category='success')
            return redirect(url_for('views.dashboard'))
        else:
            flash(f'please enter correct email or password',category='danger')
            return redirect(url_for('views.index'))
    return render_template('login.html',title='login',form=form)

@view.route('/signin',methods=['GET','POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    form=signinForm()
    if form.validate_on_submit():
        encrypted_password=bcrypt.hashpw(form.password.data.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=encrypted_password)
        db.session.add(user)
        db.session.commit()
        flash (f'Account created successfully for {form.username.data}',category='success')
        return redirect(url_for('views.dashboard'))
    return render_template('signin.html',title='signin',form=form)

@view.route('/admin',methods=['GET','POST'])
def admin():
    form=AdminloginForm()
    if form.validate_on_submit():
        if form.email.data=='harshkumar202018@gmail.com' and form.password.data=='Harshkumar1$':
            flash (f'Login successful for {form.email.data}',category='success')
            return redirect(url_for('views.adminpage'))
        else:
            flash(f'please enter correct email or password',category='danger')
            return redirect(url_for('views.index'))

    return render_template('admin.html',title='admin',form=form)

@view.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    albums = Album.query.all()
    songs = Song.query.all()
    top_songs = db.session.query(Song).order_by(Song.rating.desc()).limit(7).all()
    return render_template('dashboard.html',title='dashbaord',albums=albums,songs=songs,top_songs=top_songs,user=current_user)

@view.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.index'))

@view.route('/adminpage')
def adminpage():
    users = User.query.filter_by(role='user').all()
    creators = User.query.filter_by(role='creator').all()
    albums = Album.query.all()
    num_songs = Song.query.count()
    genres = [genre[0] for genre in db.session.query(Album.genre).distinct()]
    avg_ratings = [
        db.session.query(func.round(func.avg(Song.rating),2)).join(Album).filter(Album.genre == genre).scalar()
        for genre in genres
    ]
    genre_data = [{'genre': genre, 'avg_rating': avg} for genre, avg in zip(genres, avg_ratings)]


    return render_template('adminpage.html',users=users, creators=creators,albums=albums,num_songs=num_songs, genre_data=genre_data)

@view.route('/creator',methods=['GET','POST'])
def creator():
    if current_user.role != 'creator':
        # Update the user's role to 'creator'
        current_user.role = 'creator'
        db.session.commit()
    albums = Album.query.all()
    songs = Song.query.all()
    top_songs = db.session.query(Song).order_by(Song.rating.desc()).limit(7).all()
    return render_template('creator.html', user=current_user,albums=albums,songs=songs,top_songs=top_songs)

@view.route('/profile')
@login_required
def profile():
    creator_albums = current_user.albums
    return render_template('profile.html', user=current_user,creator_albums=creator_albums)

@view.route('/remove_user/<int:user_id>', methods=['POST'])
def remove_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User removed successfully', 'success')
    return redirect(url_for('views.adminpage'))

@view.route('/remove_album/<int:album_id>', methods=['POST'])
def remove_album(album_id):
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    flash('Album removed successfully', 'success')
    return redirect(url_for('views.adminpage'))
@view.route('/remove_song/<int:song_id>', methods=['POST'])
def remove_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    flash('song removed successfully', 'success')
    return redirect(url_for('views.adminpage'))

@view.route('/remove_creator/<int:creator_id>', methods=['POST'])
def remove_creator(creator_id):
    creator = User.query.get_or_404(creator_id)
    db.session.delete(creator)
    db.session.commit()
    flash('Creator removed successfully', 'success')
    return redirect(url_for('views.adminpage'))


@view.route('/create_page',methods=['GET','POST'])
@login_required
def create_page():
    if request.method == 'POST':
        album_name = request.form.get('album_name')
        genre = request.form.get('genre')
        artist = request.form.get('artist')
        image=request.files.get('image')
        if image:
           filename=str(album_name)+ secure_filename(image.filename)
           image.save(os.path.join(
                    view.root_path, 'static/album_images/', filename))
           input_url = "/static/album_images/" + filename

        # Create a new album
        new_album = Album(name=album_name, genre=genre, artist=artist, image=input_url,creator=current_user)
        db.session.add(new_album)
        db.session.commit()
        flash('Album Created successfully', 'success')
        creator_albums = current_user.albums
        return redirect(url_for('views.create_song',album_id=new_album.id))
    
    return render_template('create_page.html',user=current_user)
@view.route('/create_song/<int:album_id>',methods=['GET','POST'])
@login_required
def create_song(album_id):
    album = Album.query.get_or_404(album_id)
    if request.method == 'POST':
        song_name = request.form.get('song_name')
        lyrics = request.form.get('lyrics')
        duration = request.form.get('duration')
        rating = request.form.get('rating')
        audio = request.files.get('audio')
        if audio:
           filename=str(song_name)+ secure_filename(audio.filename)
           audio.save(os.path.join(
                    view.root_path, 'static/audio/', filename))
           input_url = "/static/audio/" + filename
        else:
            input_url=None

        # Create a new song
        new_song = Song(name=song_name, lyrics=lyrics, duration=duration,rating=rating,audio=input_url,album=album)
        db.session.add(new_song)
        db.session.commit()
        flash('Album Created successfully', 'success')
        

    return render_template('create_song.html', album=album,user=current_user)

@view.route('/view_lyrics/<int:song_id>')
@login_required
def view_lyrics(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template('view_lyrics.html', song=song,user=current_user)

@view.route('/rate_song/<int:song_id>', methods=['POST'])
@login_required
def rate_song(song_id):
    song = Song.query.get_or_404(song_id)
    new_rating = int(request.form.get('rating'))

    # Update the song's rating
    song.rating = new_rating
    db.session.commit()

    return redirect(url_for('views.view_lyrics', song_id=song.id,user=current_user))

@view.route('/update_album/<int:album_id>', methods=['GET', 'POST'])
@login_required
def update_album(album_id):
    album = Album.query.get_or_404(album_id)

    if request.method == 'POST':
        album.name = request.form.get('name')
        album.genre = request.form.get('genre')
        album.artist = request.form.get('artist')
        
        db.session.commit()
        flash(f'Song "{album.name}" has been updated successfully!', 'success')
        return redirect(url_for('views.creator'))

    return render_template('update_album.html', album=album,user=current_user)

@view.route('/delete_album/<int:album_id>')
@login_required
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    
    # Delete associated songs before deleting the album
    songs = Song.query.filter_by(album_id=album.id).all()
    for song in songs:
        db.session.delete(song)

    db.session.delete(album)
    db.session.commit()
    flash(f'Album "{album.name}" has been deleted successfully!', 'success')

    return redirect(url_for('views.creator'))

@view.route('/select_songs/<int:album_id>')
@login_required
def select_songs(album_id):
    album = Album.query.get_or_404(album_id)
    return render_template('select_songs.html', album=album,user=current_user)

@view.route('/delete_song/<int:song_id>')
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    album_id = song.album_id

    db.session.delete(song)
    db.session.commit()
    flash(f'Song "{song.name}" has been deleted successfully!', 'success')

    return redirect(url_for('views.select_songs', album_id=album_id))

@view.route('/update_song/<int:song_id>', methods=['GET', 'POST'])
@login_required
def update_song(song_id):
    song = Song.query.get_or_404(song_id)

    if request.method == 'POST':
        song.name = request.form.get('name')
        song.lyrics = request.form.get('lyrics')
        song.duration = request.form.get('duration')
        # Update other song details as needed
        db.session.commit()
        flash(f'Song "{song.name}" has been updated successfully!', 'success')
        return redirect(url_for('views.creator', album_id=song.album_id))

    return render_template('update_song.html', song=song,user=current_user)

@view.route('/search_results', methods=['GET'])
def search_results():
    query = request.args.get('query')

    # Perform a search in albums based on the query
    albums = Album.query.filter(Album.name.ilike(f'%{query}%') | Album.genre.ilike(f'%{query}%') | Album.artist.ilike(f'%{query}%')).all()

    # Perform a search in songs based on the query
    songs = []

    # Check if the query is a valid float before attempting the conversion
    if query:
        try:
            query_float = float(query)
            songs = Song.query.filter(Song.name.ilike(f'%{query}%') | (Song.rating == query_float)).all()
        except ValueError:
            songs = Song.query.filter(Song.name.ilike(f'%{query}%')).all()

    return render_template('search_results.html', query=query, albums=albums, songs=songs,user=current_user)

@view.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    song_id = request.form.get('song_id')

    # Check if the song is not already in the user's playlist
    if song_id and Song.query.get(song_id) not in current_user.playlist:
        current_user.playlist.append(Song.query.get(song_id))
        db.session.commit()
        flash('Song added to your playlist!', 'success')
    else:
        flash('Song is already in your playlist!', 'warning')

    if current_user.role == 'user':
        return redirect(url_for('views.dashboard'))
    elif current_user.role == 'creator':
        return redirect(url_for('views.creator'))
    

@view.route('/remove_from_playlist', methods=['POST'])
def remove_from_playlist():
    song_id = request.form.get('song_id')

    # Check if the song is in the user's playlist
    if song_id and Song.query.get(song_id) in current_user.playlist:
        current_user.playlist.remove(Song.query.get(song_id))
        db.session.commit()
        flash('Song removed from your playlist!', 'success')
    else:
        flash('Song not found in your playlist!', 'warning')

    if current_user.role == 'user':
        return redirect(url_for('views.dashboard'))
    elif current_user.role == 'creator':
        return redirect(url_for('views.creator'))
   