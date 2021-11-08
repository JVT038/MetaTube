from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, regexp

class GeneralSettings(FlaskForm):
    ffmpeg_path = StringField('Path to FFmpeg location', validators=[DataRequired('Enter a path!')])
    submit = SubmitField('Update settings')