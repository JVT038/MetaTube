from .downloadOptions import downloadOptions
from .download import download
from metatube.metadata.processMetadata import processMetadata
from metatube.metadata.mergeMetadata import mergeMetadata
from metatube.sockets import downloadprocesserror, inserted_song, finished_metadata
from metatube.Exception import MetaTubeException
from metatube.database import Database
from threading import Thread
from queue import Empty, LifoQueue
from time import sleep

class manageDownloadProcess(object):
    def __init__(self, downloadOptions: downloadOptions, metadataProcessor: processMetadata, goal: 'str'):
        self.downloadOptions = downloadOptions
        self.metadataProcessor = metadataProcessor
        self.goal = goal
        
    def start_download(self, app):
        try:
            metadata = self.metadataProcessor.getMetadata(app)
        except MetaTubeException as error:
            downloadprocesserror(str(error))
            return
        try:
            yt_dlpOptions = self.downloadOptions.downloadOptionsMapper(metadata) 
        except MetaTubeException as error:
            downloadprocesserror(str(error))
            return
        queue = LifoQueue()
        downloadProcess = Thread(target=download.start_download, args=[self.downloadOptions.youtube_id, yt_dlpOptions, queue])
        downloadProcess.start()
        downloadProcess.join()
        try:
            lastItem = queue.get_nowait()
            filepath = lastItem['filepath']
            merge = mergeMetadata(filepath, self.goal, metadata=metadata)
            data = None
            if self.downloadOptions.ext in ['MP3', 'OPUS', 'FLAC', 'OGG']:
                data = merge.mergeaudiodata()
            elif self.downloadOptions.ext in ['MP4', 'M4A']:
                data = merge.mergevideodata()
            elif self.downloadOptions.ext in ['WAV']:
                data = merge.mergeid3data()
            if type(data) is not dict:
                downloadprocesserror("Metadata could not be merged.")
                return
            finished_metadata(data)
            with app.app_context():
                data['youtube_id'] = self.downloadOptions.youtube_id
                id = Database.insert(data)
                data["id"] = id
                inserted_song(data)
        except Empty:
            pass
        except MetaTubeException as error:
            downloadprocesserror(str(error))
        finally:
            sleep(0.1)