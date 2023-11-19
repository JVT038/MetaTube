from threading import Thread
from metatube import youtube, socketio, logger
from metatube.youtube import YouTube as yt
from metatube.metadata import MetaData

def start_process(url, ytdl_options, metadataData):
    YouTubeThread = Thread(target=yt.download, args=(url, ytdl_options), name="yt-dlp download")
    mergeMetadataThread = createMetadataThread(metadataData)
    youtubeThread.start()
    logger.info('YouTube thread has started')
    youtubeThread.join()
    logger.info('YouTube thread has finished')
    logger.info('Metadata thread has started')
    mergeMetadataThread.start()
    mergeMetadataThread.join()
    logger.info('Metadata thread has finished')
    
def createMetadataThread(metadataData):
    # filepath, release_id, metadata, cover, source
    filepath = metadataData['']
    if Database.checktrackid(release_id) is None and Database.checktrackid(metadata.get('trackid', '')) is None:
        
        metadata_user = metadata
        cover_source = cover if cover != '/static/images/empty_cover.png' else os.path.join(env.BASE_DIR, 'metatube', cover)
        extension = filepath.split('.')[len(filepath.split('.')) - 1].upper()
        if extension in env.META_EXTENSIONS:
            if source == 'Spotify':
                cred = Config.get_spotify().split(';')
                spotify = Spotify(cred[1], cred[0])
                metadata_source = spotify.fetch_track(release_id)
                data = MetaData.getspotifydata(filepath, metadata_user, metadata_source)
            elif source == 'Musicbrainz':
                metadata_source = musicbrainz.search_id_release(release_id)
                data = MetaData.getmusicbrainzdata(filepath, metadata_user, metadata_source, cover_source)
            elif source == 'Deezer':
                metadata_source = Deezer.searchid(release_id)
                data = MetaData.getdeezerdata(filepath, metadata_user, metadata_source)
            elif source == 'Genius':
                token = Config.get_genius()
                genius = Genius(token)
                metadata_source = genius.fetchsong(release_id)
                lyrics = genius.fetchlyrics(metadata_source["song"]["url"])
                data = MetaData.getgeniusdata(filepath, metadata_user, metadata_source, lyrics)
            elif source == 'Unavailable':
                data = MetaData.onlyuserdata(filepath, metadata_user)
            if data is not False:
                data["goal"] = 'add'
                data["extension"] = extension
                data["source"] = source
                if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
                    Thread(target=MetaData.mergeaudiodata(data), args=(url, ytdl_options), name="Merge metadata")
                elif extension in ['MP4', 'M4A']:
                    Thread(target=MetaData.mergevideodata(data), args=(url, ytdl_options), name="Merge metadata")
                elif extension in ['WAV']:
                    Thread(target=MetaData.mergeid3data(data), args=(url, ytdl_options), name="Merge metadata")
        else:
            # The name will be the filename of the downloaded file without the extension
            filename = os.path.split(filepath)[1]
            name = filename[0:len(filename) - len(filename.split('.')[len(filename.split('.')) - 1]) - 1]
            data = {
                'filepath': filepath,
                'name': name,
                'artist': metadata_user.get('artists', 'Unknown'),
                'album': 'Unknown',
                'date': datetime.now().strftime('%d-%m-%Y'),
                'length': 'Unknown',
                'image': cover_source,
                'track_id': release_id
            }
            sockets.downloadprogress({'status': 'metadata_unavailable', 'data': data})
            logger.debug('Metadata unavailable for file %s', data["filepath"])
    else:
        sockets.searchvideo(f'{source} item has already been downloaded!')
        try:
            os.unlink(filepath)
        except Exception:
            pass