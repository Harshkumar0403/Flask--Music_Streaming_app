from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import Length,DataRequired,EqualTo,Email
from wtforms import SelectField

class signinForm(FlaskForm):
    username=StringField(label='Username',validators=[DataRequired(),Length(min=3,max=20)])
    email=StringField(label='Email adress',validators=[DataRequired(),Email()])
    password=PasswordField(label='Password',validators=[DataRequired(),Length(min=5,max=13)])
    confirm_password=PasswordField(label='confirm_Password',validators=[DataRequired(),Length(min=5,max=13),EqualTo('password')])
    submit=SubmitField(label='Sign up')

class loginForm(FlaskForm):
    email=StringField(label='Email adress',validators=[DataRequired(),Email()])
    password=PasswordField(label='Password',validators=[DataRequired(),Length(min=5,max=13)])
    submit=SubmitField(label='Log in')

class AdminloginForm(FlaskForm):
    email=StringField(label='Email adress',validators=[DataRequired(),Email()])
    password=PasswordField(label='Password',validators=[DataRequired(),Length(min=5,max=13)])
    submit=SubmitField(label='Log in')


class PlaylistForm(FlaskForm):
    song_id = SelectField('Select a Song', validators=[DataRequired()],choices=[])

    def set_song_choices(self, song_choices):
        self.song_id.choices = song_choices