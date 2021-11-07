import yt_dlp

def is_supported(url):
    extractors = yt_dlp.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False

def search(url):
    if is_supported(url):
        ytdl_options = {}
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            try:
                info = ytdl.extract_info(url, download=False)
                return info
            except Exception as e:
                return e
    else:
        raise ValueError("Invalid URL!")