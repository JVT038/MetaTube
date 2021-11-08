from picardtube.settings import bp
from picardtube.settings.forms import *
from picardtube.database import Config
# from picardtube.init import checkdb
from flask import render_template, flash

@bp.route('/settings', methods=['GET', 'POST'])
# @checkdb
def settings():
    general_form = GeneralSettings()
    ffmpeg_path = Config.ffmpeg_directory
    if general_form.validate_on_submit():
        db_config = Config().query.get(1)
        if db_config.ffmpeg(general_form.ffmpeg_path.data):
            flash('FFmpeg path has succefully been updated!')
            return render_template('settings.html', general_form=general_form, current_page='settings', ffmpeg=ffmpeg_path)
        else:
            flash('Something went wrong. Check the logs for more info')
            return render_template('settings.html', general_form=general_form, current_page='settings', ffmpeg=ffmpeg_path)
    return render_template('settings.html', general_form=general_form, current_page='settings', ffmmpeg=ffmpeg_path)