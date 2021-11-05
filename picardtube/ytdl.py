from picardtube import app
import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

class ytdlp:
    def search(url):
        ytdl_options = {}
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            try:
                info = ytdl.extract_info(url, download=False)
                return info
            except ExtractorError:
                return ExtractorError.msg