class MetadataObject(object):
    
    def __init__(
        self,
        title: str | None,
        artists: str | None,
        album: str | None,
        genres: str | None,
        language: str | None,
        release_date: str | None,
        songid: str | None,
        albumid: str | None,
        tracknr: int | None,
        cover: bytes,
        cover_path: str | None,
        cover_mime_type: str | None,
        isrc: str | None,
        lyrics: str | None,
        extension: str | None,
        source: str | None,
    ):
        self.title = title or ''
        self.artists = artists or ''
        self.album = album or ''
        self.genres = genres or ''
        self.language = language or ''
        self.release_date = release_date or ''
        self.albumid = albumid or ''
        self.songid = songid or ''
        self.tracknr = tracknr or 1
        self.cover = cover
        self.cover_path = cover_path or ''
        self.cover_mime_type = cover_mime_type or ''
        self.isrc = isrc or ''
        self.lyrics = lyrics or ''
        self.extension = extension or ''
        self.source = source or ''
        
    def metadataMapper(self):
        return {
            'title': self.title,
            'artists': self.artists,
            'album': self.album,
            'genres': self.genres,
            'language': self.language,
            'release_date': self.release_date,
            'songid': self.songid,
            'albumid': self.albumid,
            'tracknr': self.tracknr,
            'cover': self.cover,
            'cover_path': self.cover_path,
            'cover_mime_type': self.cover_mime_type,
            'isrc': self.isrc,
            'lyrics': self.lyrics,
            'extension': self.extension,
            'source': self.source
        }