from picardtube.settings import bp
from picardtube.settings.forms import *
from picardtube.database import Config
from picardtube.ffmpeg import ffmpeg
from picardtube import db
from flask import render_template, flash, jsonify

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    download_form = DownloadSettingsForm()
    ffmpeg_form = TestffmpegForm()
    db_config = Config().query.get(1)
    ffmpeg_path = db_config.ffmpeg_directory
    output_folder = db_config.output_folder
    if download_form.is_submitted() is False:
        download_form.ffmpeg_path.data = ffmpeg_path
        download_form.output_folder.data = output_folder
    if download_form.validate_on_submit():
        if db_config.ffmpeg(download_form.ffmpeg_path.data):
            flash('FFmpeg path has succefully been updated!')
            return render_template('settings.html', download_form=download_form, current_page='settings')
        else:
            flash('FFmpeg path has succefully been updated!')
            return render_template('settings.html', download_form=download_form, current_page='settings')
    else:
        for field, error in download_form.errors.items():
            for e in error:
                print(e)

    return render_template('settings.html', download_form=download_form, current_page='settings', ffmpeg=ffmpeg_form)

@bp.route('/testffmpeg', methods=['GET'])
def testffmpeg():
    ffmpeg_instance = ffmpeg()
    test = ffmpeg_instance.test()
    return jsonify(test), 200