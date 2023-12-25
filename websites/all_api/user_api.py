import datetime
from flask import jsonify, make_response
from ..models import User,Album
from .. import db
from .validation import NotFoundError, BusineesValidationError, BadRequest
from werkzeug.security import generate_password_hash
import pytz
from flask_restful import Resource, fields, marshal_with, reqparse

class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime("%d-%m-%Y %H:%M:%S")

output_user_fields = {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "role":fields.String,
    "date_created": MyDateFormat
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('input_username')
user_parser.add_argument('input_email')
user_parser.add_argument('input_password')
user_parser.add_argument('input_confirm_password')
user_parser.add_argument('input_role')


class UserAPI(Resource):
    # Get user
    @marshal_with(output_user_fields)
    def get(self, user_id = None):
        if not user_id:
            users = User.query.all()
            if users:
                return users
            else:
                return NotFoundError(error_message="No user present ")
        else:
            user = User.query.filter_by(id = user_id).first()
            if user:
                return user
            else:
                raise NotFoundError(error_message="User with user id " + str(user_id) +" is not present")
            
    #post user
    @marshal_with(output_user_fields)
    def post(self):
        args = user_parser.parse_args()
        input_username = args.get("input_username", None)
        input_email = args.get("input_email", None)
        input_role = args.get("input_role", None)
        input_password = args.get("input_password", None)
        input_confirm_password = args.get("input_confirm_password", None)

        if not input_email:
            raise BusineesValidationError(error_message="Email cannot be empty")
        elif not input_username:
            raise BusineesValidationError(error_message="Username cannot be empty")
        elif not input_password:
            raise BusineesValidationError(error_message="Password cannot be empty")
        elif not input_confirm_password:
            raise BusineesValidationError(error_message="Confirm password cannot be empty")
        
        email_exists = User.query.filter(User.email==input_email).first()
        if email_exists:
            raise BadRequest(error_message=input_email + " is already registered with us. Try to use different email")
        elif input_password != input_confirm_password:
            raise BadRequest(error_message='Passwords don\'t match! ')
        elif len(input_username) < 3:
            raise BadRequest(error_message='Username length should be atleast 3')
        elif len(input_password) < 5:
            raise BadRequest(error_message='Password length should be atleast 5')
        elif len(input_email) < 4:
            raise BadRequest(error_message='Email address is invalid')
        
        else:
            new_user = User(username = input_username,email=input_email,role=input_role,password=generate_password_hash(input_password),date_created = datetime.datetime.now(pytz.timezone('Asia/Kolkata')) )
            db.session.add(new_user)
            db.session.commit()
            return new_user,201
        
    @marshal_with(output_user_fields)
    def put(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="Please enter correct user id to update")

        args = user_parser.parse_args()
        input_email = args.get("input_email")
        input_username = args.get("input_username")

        if input_email == user.email:
            raise BusineesValidationError(error_message="You are already using "+ input_email + " email. Update to another email")

        email_exists = User.query.filter(User.stored_email==input_email).first()

        if email_exists:
            raise BadRequest(error_message=input_email + " is already registered with us. Try to use different email")
        elif len(input_username) < 3 and input_username:
            raise BadRequest(error_message='Username length should be atleast 3')
        elif len(input_email) < 4 and input_email:
            raise BadRequest(error_message='Email address is invalid')
        else:
            if input_email:
                user.email = input_email
            if input_username:
                user.username = input_username
            db.session.commit()
            return user
        
    def delete(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="Please enter correct user id to delete")
        else:
            albums = Album.query.filter(Album.creator_id == user_id).all()
            for album in albums:
                db.session.delete(album)
            db.session.delete(user)
            db.session.commit()
        return make_response(jsonify({"message":"User with id " + str(user_id) + " successfully deleted"}),200)
