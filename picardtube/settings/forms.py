from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, regexp

class DownloadSettingsForm(FlaskForm):
    ffmpeg_path = StringField('Path to FFmpeg location', validators=[DataRequired('Enter a path for FFmpeg!')])
    submit = SubmitField('Update settings')

class TestffmpegForm(FlaskForm):
    submit = SubmitField('Test FFmpeg')