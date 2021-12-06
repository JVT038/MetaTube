import yt_dlp, json, os
from threading import Thread
from metatube import socketio, sockets
from metatube.database import Templates
from metatube import sponsorblock as sb
from flask import render_template
    
class YouTube:
    def is_supported(url):
        extractors = yt_dlp.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME == 'youtube':
                return True
        return False

    def fetch_url(url):
        if YouTube.is_supported(url):
            ytdl_options = {}
            with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
                try:
                    info = ytdl.extract_info(url, download=False)
                    return info
                except Exception as e:
                    return str(e)
        else:
            raise ValueError("Invalid URL!")
        
    def verifytemplate(template):
        try:
            yt_dlp.YoutubeDL.validate_outtmpl(template)
            return True
        except ValueError as e:
            return False
        
    def __download(self, url: list, ytdl_options: dict):
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            try:
                ytdl.add_postprocessor_hook(YouTube.postprocessor_hook)
                ytdl.download(url)
                
            except Exception as e:
                return e
    
    def download_hook(d):
        if d['status'] == 'finished':
            sockets.downloadprogress({'status': 'finished_ytdl'})
        elif d['status'] == 'downloading':
            if "total_bytes_estimate" in d:
                sockets.downloadprogress({
                    'status': 'downloading', 
                    'downloaded_bytes': d['downloaded_bytes'], 
                    'total_bytes': d['total_bytes_estimate']
                })
            elif 'total_bytes' in d:
                sockets.downloadprogress({
                    'status': 'downloading', 
                    'downloaded_bytes': d['downloaded_bytes'], 
                    'total_bytes': d['total_bytes']
                })
            else:
                sockets.downloadprogress({
                    'status': 'downloading',
                    'total_bytes': 'Unknown'
                })
                
    def postprocessor_hook(d):
        if d['status'] == 'processing' or d['status'] == 'started':
            sockets.downloadprogress({'status': 'processing'})
        elif d['status'] == 'finished':
            sockets.downloadprogress({'status': 'finished_ffmpeg', 'filepath': d['info_dict']['filepath'], 'info_dict': json.dumps(d["info_dict"])})

    def get_video(self, url, ytdl_options):
        Thread(target=self.__download, args=(url, ytdl_options), name="YouTube-DLP download").start()
        
    def get_options(url, ext, output_folder, type, output_format, bitrate, skipfragments, proxy_data, ffmpeg, hw_transcoding, vaapi_device, width, height):
        proxy = json.loads(proxy_data)
        filepath = os.path.join(output_folder, output_format)
        segments = json.loads(skipfragments)
        postprocessors = []
        postprocessor_args = {}
        proxy_string = ""
        format = 'ba' if type == 'Audio' else 'b/ba+bv'
        
        if "m4a" in ext:
            ext = "m4a"
        # choose whether to use the FFmpegExtractAudio post processor or the FFmpegVideoConverter one
        if type == 'Audio':
            postprocessors.append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": ext,
                "preferredquality": bitrate
            })
        elif type == 'Video':
            postprocessors.append({
                "key": "FFmpegVideoConvertor",
                "preferedformat": ext
            })
            if len(height) < 1 or len(width) < 1:
                width = 1920
                height = 1080
            postprocessor_args["VideoConvertor"] = ['-vf', "scale=" + str(width) + ":" + str(height), '-b:a', str(bitrate) + "k"]
        # If segments have been submitted by the user to exclude, add a ModifyChapters key and add ranges
        if len(segments) > 0:
            ranges = []
            for segment in segments:
                if len(segment["start"]) < 1 or len(segment["end"]) < 1:
                    sockets.searchvideo('Enter all fragment fields!')
                    exit()
                else:
                    ranges.append((int(segment["start"]), int(segment["end"])))
            postprocessors.append({
                'key': 'ModifyChapters',
                'remove_ranges': ranges
            })
        # If hardware transcoding isn't None, add a hardware transcoding thingy to the FFmpeg arguments
        if hw_transcoding != 'None':
            if hw_transcoding == 'nvenc':
                postprocessor_args["default"] = ['-c:v', 'h264_nvenc']
            elif hw_transcoding == 'qsv':
                postprocessor_args["default"] = ['-c:v', 'h264_qsv']
            elif hw_transcoding == 'videotoolbox':
                postprocessor_args["default"] = ['-c:v', 'h264_videotoolbox']
            elif 'vaapi' in hw_transcoding:
                postprocessor_args["default"] = ['-vaapi_device', vaapi_device, '-c:v', 'h264_vaapi']
            elif hw_transcoding == 'amd':
                postprocessor_args["default"] = ['-c:v', 'h264_amf']
            elif hw_transcoding == 'omx':
                postprocessor_args["default"] = ['-c:v', 'h264_omx']

        ytdl_options = {
            'format': format,
            'postprocessors': postprocessors,
            'postprocessor_args': postprocessor_args,
            'ffmpeg_location': ffmpeg,
            'progress_hooks': [YouTube.download_hook],
            'outtmpl': filepath,
            'noplaylist': True,
            'verbose': True
        }
        
        # Add proxy if proxy is enabled
        if proxy['proxy_status'] != 'None':
            proxy_string = proxy["proxy_status"].lower().strip() + "://"
            if len(proxy["proxy_username"]) > 0 and len(proxy["proxy_username"]) > 0:
                proxy_string += proxy["proxy_username"] + ":" + proxy["proxy_password"] + "@" + proxy["proxy_address"].strip() + ":" + proxy["proxy_port"].strip()
            else:
                proxy_string += proxy["proxy_address"].strip() + ":" + proxy["proxy_port"].strip()
            ytdl_options["proxy"] = proxy_string
            
        return ytdl_options
        
def fetch_video(args):
    from metatube import create_app
    app = create_app()        
    segments = sb.segments(args["video"]["id"])
    with app.app_context():
        app.config['SERVER_NAME'] = args['server_name']
        templates = Templates.fetchalltemplates()
        downloadform = render_template('downloadform.html', templates=templates, segments=segments)
        socketio.emit('ytdl_response', (args["video"], downloadform))