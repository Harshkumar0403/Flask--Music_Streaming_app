import datetime
from flask import Blueprint, Flask, jsonify, make_response, request, redirect, url_for, flash
from flask import render_template
from ..models import  User,Album,Song
from .. import db
from .validation import NotFoundError, BusineesValidationError, BadRequest
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
from flask_restful import Resource, Api, fields, marshal_with, reqparse

class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime("%d-%m-%Y %H:%M:%S")

output_song_fields = {
    "id": fields.Integer,
    "name" : fields.String,
    "duration":fields.String,
    "rating" : fields.String,
    "date_created" : fields.String,
    "album_id" : fields.Integer,
    "lyrics" : fields.String
}
song_parser = reqparse.RequestParser()
song_parser.add_argument('input_name')
song_parser.add_argument('input_duration')
song_parser.add_argument('input_rating')
song_parser.add_argument('input_date_created')
song_parser.add_argument('input_lyrics')

class SongAPI(Resource):
    # Get album
    @marshal_with(output_song_fields)
    def get(self, album_id = None, song_id = None):
        if album_id is None:
            song = Song.query.filter_by(id = song_id).first()
            if song:
                return song
            else:
                raise NotFoundError(error_message="Song with song id " + str(album_id) + " is not present")
        else:
            album = Album.query.filter_by(id = album_id).first()
            if album:
                if song_id is None:
                    songs = Song.query.filter_by(album_id = album_id).all()
                    if songs:
                        return songs
                    else:
                        raise NotFoundError(error_message=" No songs present in " + album.name)
                else:
                    song = Song.query.filter_by(id = song_id, album_id = album_id).first()
                    if song:
                        return song
                    else:
                        raise NotFoundError(error_message="song with song id " + str(song_id) + " under album with id " + str(album_id) +" is not present")
            else:
                raise NotFoundError(error_message="album with album id " + str(album_id) +" is not present")
            