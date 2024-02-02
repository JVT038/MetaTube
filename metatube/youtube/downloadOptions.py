import os
from metatube import logger
from .downloadExceptions import *
from metatube.metadata.metadataObject import MetadataObject
from yt_dlp.postprocessor.metadataparser import MetadataParserPP
class downloadOptions(object):
    def __init__(
        self,
        ext: str,
        output_folder: str,
        output_type: str,
        output_format: str,
        bitrate: int | str,
    	skipfragments: dict,
    	proxy_data: dict,
    	ffmpeg: str,
    	hw_transcoding: str,
    	vaapi_device: str,
    	width: int | str,
    	height: int | str,
    	verbose: bool,
    	
     ):
        self.ext = ext
        self.output_folder = output_folder
        self.output_type = output_type
        self.output_format = output_format
        self.bitrate = bitrate
        self.skipfragments = skipfragments
        self.proxy_data = proxy_data
        self.ffmpeg = ffmpeg
        self.hw_transcoding = hw_transcoding
        self.vaapi_device = vaapi_device
        self.width = width
        self.height = height
        self.verbose = verbose
        
    def optionsToDictMapper(self, metadata: MetadataObject) -> dict:
        filepath = os.path.join(self.output_folder, self.output_format)
        postprocessors = []
        postprocessor_args = {}
        proxy_string = ""
        ext = "m4a" if "m4a" in self.ext else self.ext
        '''
        Audio:
        If an audio type has been selected, first try to look for a format with the selected extension
        If no audio format with the selected extension has been found, just look for the best audio format
        and automatically convert it to the selected extension anyway
        Video:
        Exactly the same for videos
        '''
        format = f'ba[ext={ext}]/ba' if self.output_type == 'Audio' else f'b[ext={ext}]/ba+bv[ext={ext}]/b/ba+bv'
        
        # choose whether to use the FFmpegExtractAudio post processor or the FFmpegVideoConverter one
        if self.output_type == 'Audio':
            postprocessors.append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": ext,
                "preferredquality": self.bitrate
            })
        elif self.output_type == 'Video':
            postprocessors.append({
                "key": "FFmpegVideoConvertor",
                "preferedformat": ext
            })
            postprocessor_args['videoconvertor'] = []
            if self.bitrate != 'best':
                postprocessor_args["videoconvertor"] = ['-b:a', str(self.bitrate) + "k"]
                
            if self.height != 'best' and self.width != 'best':
                postprocessor_args["videoconvertor"][:0] = ['-vf', 'scale=' + str(self.width) + ':' + str(self.height)]
            
            # If hardware transcoding isn't None, add a hardware transcoding thingy to the FFmpeg arguments
            if self.hw_transcoding != 'None':
                if "videoconvertor" not in postprocessor_args:
                    postprocessor_args["videoconvertor"] = []
                if self.hw_transcoding == 'nvenc':
                    postprocessor_args["videoconvertor"].extend(['-c:v', 'h264_nvenc'])
                elif self.hw_transcoding == 'qsv':
                    postprocessor_args["videoconvertor"].extend(['-c:v', 'h264_qsv'])
                elif self.hw_transcoding == 'videotoolbox':
                    postprocessor_args["videoconvertor"].extend(['-c:v', 'h264_videotoolbox'])
                elif 'vaapi' in self.hw_transcoding:
                    postprocessor_args["videoconvertor"].extend(['-vaapi_device', self.vaapi_device, '-c:v', 'h264_vaapi'])
                elif self.hw_transcoding == 'amd':
                    postprocessor_args["videoconvertor"].extend(['-c:v', 'h264_amf'])
                elif self.hw_transcoding == 'omx':
                    postprocessor_args["videoconvertor"].extend(['-c:v', 'h264_omx'])
                else:
                    raise InvalidHardwareTranscoding("An invalid type has been selected for hardware transcoding.")
        else:
            raise NoOutputType("No output type has been selected. Video or audio must be chosen for download.")
                    
        # If segments have been submitted by the user to exclude, add a ModifyChapters key and add ranges
        if len(self.skipfragments) > 0:
            ranges = []
            for segment in self.skipfragments:
                if len(segment["start"]) < 1 or len(segment["end"]) < 1:
                    raise EmptyFragments("One or more segment fields was left empty.")
                else:
                    ranges.append((int(segment["start"]), int(segment["end"])))
            postprocessors.append({
                'key': 'ModifyChapters',
                'remove_ranges': ranges
            })
        
        '''
        --parse-metadata example in CLI:
        yt-dlp orJSJGHjBLI -x --audio-format mp3 --add-metadata -o "%(track,title)s - %(artist)s.%(ext)s" --parse-metadata " Bad Habits: %(title)s" --parse-metadata "Ed Sheeran:%(artist)s"
        '''
        postprocessors.append({
            'actions': [
                (MetadataParserPP.interpretter, " " + metadata.title, ' %(title)s'),
                (MetadataParserPP.interpretter, metadata.album, '%(album)s'),
                (MetadataParserPP.interpretter, metadata.album_artists, '%(artist)s'),
                (MetadataParserPP.interpretter, metadata.album_artists, '%(album_artist)s'),
                (MetadataParserPP.interpretter, str(metadata.tracknr), '%(track_number)s'),
                (MetadataParserPP.interpretter, metadata.language, '%(language)s'),
                (MetadataParserPP.interpretter, metadata.genres, '%(genre)s'),
                (MetadataParserPP.interpretter, metadata.release_date, '%(date)s'),
            ],
            'key': 'MetadataParser',
            'when': 'pre_process'
        })
            
        ytdl_options = {
            'format': format,
            'merge_output_format': ext,
            'postprocessors': postprocessors,
            'postprocessor_args': postprocessor_args,
            'ffmpeg_location': self.ffmpeg,
            'logger': logger,
            'outtmpl': filepath,
            'noplaylist': True,
            'verbose': self.verbose
        }
        
        # Add proxy if proxy is enabled
        if self.proxy_data['proxy_type'] != 'None':
            proxy_string = self.proxy_data["proxy_type"].lower().strip() + "://"
            if len(self.proxy_data["proxy_username"]) > 0 and len(self.proxy_data["proxy_username"]) > 0:
                proxy_string += self.proxy_data["proxy_username"] + ":" + self.proxy_data["proxy_password"] + "@" + self.proxy_data["proxy_address"].strip() + ":" + self.proxy_data["proxy_port"].strip()
            else:
                proxy_string += self.proxy_data["proxy_address"].strip() + ":" + self.proxy_data["proxy_port"].strip()
            ytdl_options["proxy"] = proxy_string
        return ytdl_options