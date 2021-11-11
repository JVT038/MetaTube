import yt_dlp, threading
    
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
                    return e
        else:
            raise ValueError("Invalid URL!")
        
    def __download(self, url, ytdl_options):
        print(url)
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            ytdl.download(url)
            
    def get_video(self, url, ytdl_options):
        threading.Thread(target=self.__download, args=(url, ytdl_options), name="YouTube-DLP download").start()
        