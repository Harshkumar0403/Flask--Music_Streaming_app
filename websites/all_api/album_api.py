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
    
output_album_fields = {
    "id": fields.Integer,
    "name" : fields.String,
    "genre" : fields.String,
    "artist":fields.String,
    "creator_id" : fields.Integer 
}

album_parser = reqparse.RequestParser()
album_parser.add_argument('input_name')
album_parser.add_argument('input_genre')
album_parser.add_argument('input_artist')

class AlbumAPI(Resource):
    # Get album
    @marshal_with(output_album_fields)
    def get(self, user_id = None, album_id = None):
        if user_id is None:
            album = Album.query.filter_by(id = album_id).first()
            if album:
                return album
            else:
                raise NotFoundError(error_message="Album with album id " + str(album_id) + " is not present")
        else:
            user = User.query.filter_by(id = user_id).first()
            if user:
                if album_id is None:
                    albums = Album.query.filter_by(creator_id = user_id).all()
                    if albums:
                        return albums
                    else:
                        raise NotFoundError(error_message=" No album present in " + user.username + " profile")
                else:
                    album = Album.query.filter_by(id = album_id, creator_id = user_id).first()
                    if album:
                        return album
                    else:
                        raise NotFoundError(error_message="album with album id " + str(album_id) + " under user with id " + str(user_id) +" is not present")
            else:
                raise NotFoundError(error_message="User with user id " + str(user_id) +" is not present")
            
    @marshal_with(output_album_fields)
    def post(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="There is no user with id " + str(user_id))
        args = album_parser.parse_args()
        input_name = args.get("input_name", None)
        input_genre = args.get("input_genre", None)
        input_artist=args.get("input_artist",None)

        if not input_name:
            raise BusineesValidationError(error_message="Name cannot be empty")
        elif not input_genre:
            raise BusineesValidationError(error_message="Genre cannot be empty")
        elif not input_artist:
            raise BusineesValidationError(error_message="Artist cannot be empty")

        new_album = Album(name=input_name,genre=input_genre,artist=input_artist,creator_id=user_id)
        db.session.add(new_album)
        db.session.commit()
        return new_album,201
    
    @marshal_with(output_album_fields)
    def put(self, user_id, album_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="There is no user with id " + str(user_id))
        album= Album.query.filter_by(id = album_id, creator_id = user_id).first()
        if not album:
            raise BadRequest(error_message="There is no album with id " + str(album_id) + " under user with id " + str(user_id))

        args = album_parser.parse_args()
        input_name = args.get("input_name", None)
        input_genre = args.get("input_genre", None)
        input_artist = args.get("input_artist", None)


        if not input_name:
            raise BusineesValidationError(error_message="name cannot be empty")
        elif not input_genre:
            raise BusineesValidationError(error_message="genre cannot be empty")
        elif not input_artist:
            raise BusineesValidationError(error_message="artist cannot be empty")

        if input_name ==album.name:
            raise BusineesValidationError(error_message="You are already using "+ input_name + " name. Update to another name")
        elif input_genre == album.genre:
            raise BusineesValidationError(error_message="You are already using "+ input_genre + " genre. Update to another genre")
        elif input_artist == album.artist:
            raise BusineesValidationError(error_message="You are already using "+ input_artist + "artist. Update to another artist")

        album.name = input_name
        album.genre = input_genre
        album.artist = input_artist
        
        db.session.commit()
        return album
        
    
    def delete(self, user_id, album_id):
        user = User.query.filter_by(id = user_id).first()
        album = Album.query.filter_by(id = album_id, ceator_id = user_id).first()
        song=Song.query.filter_by(album_id=album_id).all()
        if not user:
            raise BadRequest(error_message="Please enter correct user id to delete")
        elif not album:
            raise BadRequest(error_message="User with id " + str(user_id) + " doesn't contain album with id " + str(album_id))
        else:
            db.session.delete(song)
            db.session.delete(album)
            db.session.commit()
        return make_response(jsonify({"message":"Album with id " + str(album) + " successfully deleted"}),200)