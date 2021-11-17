from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.core import IntegerField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, NumberRange, regexp

class DownloadSettingsForm(FlaskForm):
    ffmpeg_path = StringField('Path to FFmpeg location', validators=[DataRequired('Enter a path for FFmpeg!')])
    amount = IntegerField('Max amount of items to load', validators=[DataRequired('Enter an integer!'), NumberRange(0, 100)])
    submit = SubmitField('Update settings')