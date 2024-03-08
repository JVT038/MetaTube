import yt_dlp
expectedOptions = {
    'format': 'ba[ext=MP3]/ba',
    'merge_output_format': 'MP3',
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'MP3',
            'preferredquality': '192'
        },
        {
            'actions': [
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    ' Never Gonna Give You Up',
                    ' %(title)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    ' Never Gonna Give You Up',
                    ' %(track)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    'Whenever You Need Somebody',
                    '%(album)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    'Rick Astley',
                    '%(artist)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    'Rick Astley',
                    '%(creator)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    'Rick Astley',
                    '%(album_artist)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    '1',
                    '%(track_number)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    'Unknown',
                    '%(language)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    '',
                    '%(genre)s'
                ),
                (
                    yt_dlp.postprocessor.metadataparser.MetadataParserPP.interpretter,
                    '1987-11-12',
                    '%(date)s'
                )
            ],
            'key': 'MetadataParser',
            'when': 'pre_process'
        }
    ],
    'postprocessor_args': {},
    'ffmpeg_location': 'bin',
    # 'logger': <Loggerdefault(
    #     NOTSET
    # )>,
    'outtmpl': '/path/to/downloads\\%(title)s.%(ext)s',
    'noplaylist': True,
    'verbose': False
}