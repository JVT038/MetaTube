from flask.templating import render_template_string
from metatube.settings import bp
from metatube.database import *
from metatube.ffmpeg import ffmpeg
from metatube import Config as env
from metatube import socketio, sockets
from flask import render_template, request, jsonify
import os, json

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    db_config = Config().query.get(1)
    ffmpeg_path = db_config.ffmpeg_directory
    amount = db_config.amount
    hw_transcoding = db_config.hardware_transcoding
    metadata_sources = db_config.metadata_sources.split(';')
    spotify = db_config.spotify_api.split(';') if db_config.spotify_api is not None else ['', '']
    genius = db_config.genius_api if db_config.genius_api is not None else ''
    templates = Templates.query.all()
    
    return render_template('settings.html', 
                           ffmpeg=ffmpeg_path, 
                           amount=amount, 
                           current_page='settings', 
                           templates=templates, 
                           hw_transcoding=hw_transcoding,
                           metadata_sources=metadata_sources,
                           spotify=spotify,
                           genius=genius)
    
@socketio.on('updatetemplate')
def template(name, output_folder, output_ext, output_name, id, goal, bitrate = 'best', width = 'best', height = 'best', proxy_json = {'status': False,'type': '','address': '','port': '','username': '','password': ''}):
    data = {
        'name': name,
        'output_folder': output_folder, 
        'ext': output_ext,
        'output_name': output_name,
        'bitrate': str(bitrate),
        'width': width,
        'height': height,
        'resolution': str(width) + ";" + str(height)
    }
    proxy = json.loads(proxy_json)
    data["proxy"] = {
        'status': True if str(proxy['status']) == 'true' else False,
        'type': proxy['type'],
        'address': proxy['address'],
        'port': proxy['port'],
        'username': proxy['username'],
        'password': proxy['password']
    }
    print(data["proxy"]["status"])
    if len(data["name"]) < 1 or len(data["output_folder"]) < 1 or len(data["ext"]) < 1 or len(goal) < 1 or len(id) < 1 or data["name"] == 'Default' or len(data["output_name"]) < 1:
        sockets.changetemplate('Enter all fields!')
    elif data["proxy"]["status"] is True and (len(data["proxy"]["address"]) < 1 or len(data["proxy"]["type"]) < 1 or len(data["proxy"]["port"]) < 1):
        sockets.changetemplate('Enter all proxy fields!')
    else:
        # check if output folder is absolute or relative
        if data["output_folder"].startswith('/') or (data["output_folder"][0].isalpha() and data["output_folder"][1].startswith(':\\')):
            # check if output folder actually exists and if it's a directory
            if os.path.exists(data["output_folder"]) is False or os.path.isdir(data["output_folder"]) is False:
                sockets.changetemplate('Output directory doesn\'t exist')
        else:
            data["output_folder"] = os.path.join(env.BASE_DIR, data["output_folder"])
            if os.path.exists(data["output_folder"]) is False or os.path.isdir(data["output_folder"]) is False:
                sockets.changetemplate('Output directory doesn\'t exist')
        
        if data["ext"] not in ["mp4", "flv", "webm", "ogg", "mkv", "avi", "aac", "flac", "mp3", "m4a_audio", "m4a_video", "opus", "vorbis", "wav"]:
            sockets.changetemplate('Incorrect extension')
        
        if data["ext"] in ["aac", "flac", "mp3", "m4a_audio", "opus", "vorbis", "wav"]:
            data["type"] = 'Audio'
        
        elif data["ext"] in ["mp4", "m4a_video", "flv", "webm", "ogg", "mkv", "avi"]:
            data["type"] = 'Video'
        
        if goal == 'add':
            if Templates.check_existing(data["name"]):
                sockets.changetemplate('Name is already in use')
                return False
            data['id'] = Templates.add(data)
            sockets.templatesettings({'status': 'newtemplate', 'msg': 'Template successfully added', 'data': data})
        
        elif goal == 'edit':
            template = Templates.fetchtemplate(id)
            template.edit(data)
            sockets.templatesettings({'status': 'changedtemplate', 'msg': 'Template successfully changed', 'data': data})
    
@socketio.on('deletetemplate')
def deltemplate(id):
    if len(id) < 1:
        sockets.templatesettings({'status': 'error', 'msg': 'Select a valid template'})
        return False
    if Templates.counttemplates() < 2:
        sockets.templatesettings({'status': 'error', 'msg': 'You must have one existing template!'})
        return False
    template = Templates.fetchtemplate(input_id=id)
    if template.default is True:
        sockets.templatesettings({'status': 'error', 'msg': 'You can\'t  delete the default template!'})
        return False
    template.delete()
    sockets.templatesettings({'status': 'delete', 'msg': 'Template successfully removed', 'templateid': id})
    
@socketio.on('setdefaulttemplate')
def defaulttemplate(id):
    if len(id) < 1:
        sockets.templatesettings({'status': 'error', 'msg': 'Select a valid template'})
        return False
    template = Templates.fetchtemplate(input_id=id)
    default = Templates.searchdefault()
    template.setdefault(default)

@socketio.on('updatesettings')
def updatesettings(ffmpeg_path, amount, hardware_transcoding, metadata_sources, extradata):
    db_config = Config.query.get(1)
    response = ""
    
    if db_config.ffmpeg_directory != ffmpeg_path:
        ffmpeg_path = os.path.join(env.BASE_DIR, ffmpeg_path)
        if os.path.exists(ffmpeg_path):
            if os.path.isfile(ffmpeg_path):
                ffmpeg_path = os.path.dirname(ffmpeg_path)
            if db_config.ffmpeg_directory != ffmpeg_path:
                db_config.ffmpeg(ffmpeg_path)
                ffmpeg_instance = ffmpeg()
                if ffmpeg_instance.test():
                    response += 'FFmpeg path has succefully been updated and found! <br />'
                else:
                    response += 'FFmpeg path has succefully been updated, but the application hasn\'t been found <br />'
        else:
            response += 'FFmpeg path doesn\'t exist <br/>'
            
    if str(db_config.amount) != str(amount):
        db_config.set_amount(amount)
        response += 'Max amount has succesfully been updated <br />'
        
    if str(db_config.hardware_transcoding) != str(hardware_transcoding):
        if "vaapi" in hardware_transcoding:
            if len(hardware_transcoding.split(';')[1]) < 1:
                response += 'Enter a VAAPI device path! <br />'
                exit()
        db_config.set_hwtranscoding(hardware_transcoding)
        response += 'Hardware Transcoding setting has succesfully been updated! <br />'
        
    if ';'.join(sorted(metadata_sources)) != ';'.join(sorted(db_config.metadata_sources.split(';'))):
        if (len(metadata_sources) == 1 and 'genius' not in metadata_sources) or (len(metadata_sources) > 1):
            db_config.set_metadata(';'.join(sorted(metadata_sources)))
            response += 'Metadata setting has succesfully been updated! <br />'
        else:
            response += 'At least one metadata source excluding Genius must be selected! <br />'
    
    if 'spotify' in metadata_sources and 'spotifyapi' in extradata:
        spotifydata =  extradata["spotifyapi"]["secret"] + ";" +  extradata["spotifyapi"]["id"]
        if str(db_config.spotify_api) != spotifydata:
            db_config.set_spotify(spotifydata)
            response += 'Spotify API settings have succesfully been updated! <br />'
            
    if 'genius' in metadata_sources and 'geniusapi' in extradata:
        geniusdata = extradata['geniusapi']['token']
        if str(db_config.genius_api) != geniusdata:
            db_config.set_genius(geniusdata)
            response += 'Genius API settings have succesfully been updated! <br/>'
            
    sockets.downloadsettings(response)