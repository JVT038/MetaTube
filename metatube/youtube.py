import yt_dlp
from threading import Thread
from metatube import sockets
from metatube import ffmpeg
    
class YouTube:
    def is_supported(url):
        extractors = yt_dlp.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME != 'generic':
                return True
        return False

    def search(url):
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
            sockets.overview({'status': 'Finished download'})
        elif d['status'] == 'downloading':
            if "total_bytes_estimate" in d:
                sockets.overview({
                    'status': 'downloading', 
                    'downloaded_bytes': d['downloaded_bytes'], 
                    'total_bytes': d['total_bytes_estimate']
                })
            else:
                sockets.overview({
                    'status': 'downloading',
                    'total_bytes': 'Unknown'
                })
    def postprocessor_hook(d):
        if d['status'] == 'processing' or d['status'] == 'started':
            sockets.overview({'status': 'processing'})
        elif d['status'] == 'finished':
            sockets.overview({'status': 'finished_ffmpeg', 'filepath': d['info_dict']['filepath']})

    def get_video(self, url, ytdl_options):
        Thread(target=self.__download, args=(url, ytdl_options), name="YouTube-DLP download").start()