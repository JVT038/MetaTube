from metatube.settings import bp
from metatube.settings.forms import *
from metatube.database import *
from metatube.ffmpeg import ffmpeg
from metatube import Config as env
from metatube.youtube import YouTube as youtube
from flask import render_template, flash, request, jsonify
from mock import Mock
import os, json

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    download_form = DownloadSettingsForm()
    ffmpeg_form = TestffmpegForm()
    db_config = Config().query.get(1)
    ffmpeg_path = db_config.ffmpeg_directory
    templates = Templates.query.all()
    if download_form.is_submitted() is False:
        download_form.ffmpeg_path.data = ffmpeg_path
    if download_form.validate_on_submit():
        if db_config.ffmpeg(download_form.ffmpeg_path.data):
            ffmpeg_instance = ffmpeg()
            if ffmpeg_instance.test():
                flash('FFmpeg path has succefully been updated and found!')
                return render_template('settings.html', download_form=download_form, current_page='settings', templates=templates)
            else:
                flash('FFmpeg path has succefully been updated, but the application hasn\'t been found')
                return render_template('settings.html', download_form=download_form, current_page='settings', templates=templates)
        else:
            flash('Something went wrong while updating the path. Check the logs for more info.')
            return render_template('settings.html', download_form=download_form, current_page='settings', templates=templates)
    else:
        for field, error in download_form.errors.items():
            for e in error:
                print(e)

    return render_template('settings.html', download_form=download_form, current_page='settings', ffmpeg=ffmpeg_form, templates=templates)

@bp.route('/ajax/template', methods=['POST'])
def template():
    data = Mock()
    goal = request.form.get('goal')
    data.name = request.form.get('name')
    data.output_folder = request.form.get('output_folder')
    data.ext = request.form.get('output_ext')
    data.output_name = request.form.get('output_name')
    data.bitrate = request.form.get('bitrate')
    id = request.form.get('id', "0")
    
    default_proxy = {
        'status': False,
        'type': '',
        'address': '',
        'port': '',
        'username': '',
        'password': ''
    }
    proxy = json.loads(request.form.get('proxy', default_proxy))
    data.proxy = {
        'status': True if proxy['status'] == 'true' else False,
        'type': proxy['type'],
        'address': proxy['address'],
        'port': proxy['port'],
        'username': proxy['username'],
        'password': proxy['password']
    }
    
    if len(data.name) < 1 or len(data.output_folder) < 1 or len(data.ext) < 1 or len(goal) < 1 or len(id) < 1 or data.name == 'Default' or len(data.bitrate) < 1 or len(data.output_name) < 1:
        response = jsonify('Enter all fields!')
        return response, 400
    elif data.proxy["status"] is True and (len(data.proxy["address"]) < 1 or len(data.proxy["type"]) < 1 or len(data.proxy["port"]) < 1):
        response = jsonify('Enter all proxy fields!')
        return response, 400
    else:
        # check if output folder is absolute or relative
        if data.output_folder.startswith('/') or (data.output_folder[0].isalpha() and data.output_folder[1].startswith(':\\')):
            # check if output folder actually exists and if it's a directory
            if os.path.exists(data.output_folder) is False or os.path.isdir(data.output_folder) is False:
                response = jsonify('Output directory doesn\'t exist')
                return response, 400
        else:
            if os.path.exists(os.path.join(env.BASE_DIR, data.output_folder)) is False or os.path.isdir(os.path.join(env.BASE_DIR, data.output_folder)) is False:
                response = jsonify('Output directory doesn\'t exist')
                return response, 400
        
        if data.ext not in ["mp4", "flv", "webm", "ogg", "mkv", "avi", "aac", "flac", "mp3", "m4a", "opus", "vorbis", "wav"]:
            response = jsonify('Incorrect extension')
            return response, 400
        
        if data.ext in ["aac", "flac", "mp3", "m4a", "opus", "vorbis", "wav"]:
            data.type = 'Audio'
        
        elif data.ext in ["mp4", "flv", "webm", "ogg", "mkv", "avi"]:
            data.type = 'Video'
        
        if goal == 'add':
            if Templates.check_existing(data.name):
                response = jsonify('Name is already in use')
                return response, 400
            Templates.add(data)
            response = jsonify('Template successfully added')
            return response, 200
        
        elif goal == 'edit':
            template = Templates.fetchtemplate(id)
            template.edit(data)
            response = jsonify('Template successfully changed')
            return response, 200
    
@bp.route('/ajax/deltemplate', methods=['POST'])
def deltemplate():
    id = request.form.get('id')
    if len(id) < 1 or int(id) == 0:
        response = jsonify('Select a valid template')
        return response, 400
    template = Templates.fetchtemplate(input_id=id)
    if template.delete():    
        response = jsonify('Template successfully removed')
        return response, 200
    else:
        response = jsonify('Something went wrong. Please check the logs for more info.')
        return response, 400