from flask import Flask,request, redirect,render_template,url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_restful import Resource, Api, fields, marshal_with, reqparse

db = SQLAlchemy()
DB_NAME = "database.sqlite3"
def create_app():
    app=Flask(__name__,template_folder='templates')
    app.config['SECRET_KEY']='HATTRWCVGADEWBJJUWT'
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME}'
    db.init_app(app)
    api = Api(app)

    bcrypt=Bcrypt(app)
    
    login_manager = LoginManager()
    login_manager.login_view = "views.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('views.login'))


    from .all_api.user_api  import UserAPI
    from .all_api.album_api  import AlbumAPI
    from .all_api.song_api  import SongAPI
    from .views import view
    app.register_blueprint(view, url_prefix='/')
    from .models import User

    api.add_resource(UserAPI,"/api/user", "/api/user/<int:user_id>")
    api.add_resource(AlbumAPI,"/api/album/<int:user_id>/album", "/api/album/<int:user_id>/album/<int:album_id>", "/api/album/<int:album_id>")
    api.add_resource(SongAPI,"/api/album/song/<int:album_id>", "/api/album/song/<int:album_id>/album/<int:song_id>/song", "/api/album/song/<int:song_id>/song")
    create_database(app)

    return app


def create_database(app):
    if not path.exists("websites/" + DB_NAME):
        with app.app_context():
            db.create_all()