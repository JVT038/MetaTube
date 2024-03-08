import yt_dlp
from youtubesearchpython import VideosSearch
from .downloadExceptions import InvalidYouTubeUrl
from metatube import sockets, logger
from metatube.sponsorblock import segments as findsegments
from jinja2 import Environment, PackageLoader, select_autoescape
    
class utils(object):
    @staticmethod
    def is_supported(url):
        exceptions = ['radioactive']
        extractors = yt_dlp.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME == 'youtube' and url not in exceptions:
                return True
        return False

    @staticmethod
    def fetch_url(url, verbose):
        if utils.is_supported(url):
            ytdl_options = {'logger': logger, 'verbose': verbose}
            with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
                try:
                    info = ytdl.extract_info(url, download=False)
                    return info
                except Exception as e:
                    return str(e)
        else:
            raise InvalidYouTubeUrl("Invalid URL!")
    
    @staticmethod
    def verifytemplate(template, info_dict, verbose):
        ytdl_options = {'logger': logger, 'verbose': verbose}
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            try:
                filename = ytdl.evaluate_outtmpl(template, info_dict)
                return filename
            except Exception as e:
                return str(e)
    
    @staticmethod
    def search(query: str):
        logger.info('Searching YouTube for \'%s\'', query)
        search = VideosSearch(query)
        result = search.result()
        sockets.youtubesearch(result)
    
    @staticmethod
    def fetch_video(video, templates, metadata_sources, defaulttemplate):
        sb = findsegments(video["webpage_url"])
        segments = sb if type(sb) == list else 'error'
        env = Environment(
            loader=PackageLoader('metatube'),
            autoescape=select_autoescape()
        )
        downloadtemplate = env.get_template('downloadform.html')
        metadatatemplate = env.get_template('metadataform.html')
        downloadform = downloadtemplate.render(templates=templates, segments=segments, default=defaulttemplate)
        metadataform = metadatatemplate.render(metadata_sources=metadata_sources)
        sockets.youtuberesults(video, downloadform, metadataform)