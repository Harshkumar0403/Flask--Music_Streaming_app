from websites import db
from datetime import datetime
from flask_login import LoginManager,UserMixin


playlist_association = db.Table(
    'playlist_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
)


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(20),unique=True)
    password=db.Column(db.String(60),nullable=True)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    playlist = db.relationship('Song', secondary=playlist_association, backref=db.backref('users', lazy='dynamic'))
    role=db.Column(db.String(10),default='user')
    def __repr__(self):
        return f'{self.username}:{self.email}:{self.date_created.strftime("%d/%m/%y,%H:%M:%S")}'

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    image=db.Column(db.String(255))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='albums')


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    lyrics = db.Column(db.Text)
    duration = db.Column(db.String(20))
    audio = db.Column(db.String(255))
    rating = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    album = db.relationship('Album', backref='songs')

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'))