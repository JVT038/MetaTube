from picardtube.settings import bp
from picardtube.settings.forms import *
from picardtube.database import Config
from flask import render_template, flash

@bp.route('/settings')
def settings():
    general_form = GeneralSettings()
    if general_form.validate_on_submit():
        db_config = Config()
        if db_config.ffmpeg(general_form.ffmpeg_path.data):
            flash('FFmpeg path has succefully been updated!')
            return render_template('settings.html', general_form=general_form)
    return render_template('settings.html', general_form=general_form)