from .downloadOptions import downloadOptions
from .download import download
from metatube.metadata.processMetadata import processMetadata
from metatube.metadata.mergeMetadata import mergeMetadata
from metatube.metadata.readMetadata import readMetadata
from metatube.sockets import downloadprocesserror, inserted_song, finished_metadata, changed_metadata
from metatube.Exception import MetaTubeException
from metatube.database import Database
from threading import Thread
from queue import Empty, LifoQueue
from time import sleep
import os
from dateutil import parser
from datetime import datetime

class manageDownloadProcess(object):
    def __init__(self, downloadOptions: downloadOptions, metadataProcessor: processMetadata | None, goal: 'str', item: Database | None):
        self.downloadOptions = downloadOptions
        self.metadataProcessor = metadataProcessor
        self.goal = goal
        self.item = item
        
    def start_download(self, app):
        metadata = None
        if self.goal == 'add' and self.metadataProcessor is not None:
            try:
                metadata = self.metadataProcessor.getMetadata(app)
            except MetaTubeException as error:
                downloadprocesserror(str(error))
                return
        elif self.goal == 'edit':
            if self.item is not None:
                try:
                    if self.downloadOptions.ext in ['MP3', 'FLAC', 'AAC', 'OPUS', 'OGG']:
                        metadata = readMetadata.readAudioMetadata(self.item.filepath, self.item.songid, self.item.cover)
                    elif self.downloadOptions.ext in ['MP4', 'M4A']:
                        metadata = readMetadata.readVideoMetadata(self.item.filepath, self.item.songid, self.item.cover)
                except MetaTubeException as error:
                    downloadprocesserror(str(error))
                    return
            else:
                return
        if metadata is None:
            downloadprocesserror("Download process could not be started. Please check thet logs and try again.")
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
            merge = mergeMetadata(filepath, self.goal, metadata, youtube_id=self.downloadOptions.youtube_id)
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
                if self.goal == 'add':
                    id = Database.insert(data)
                    data["id"] = id
                    inserted_song(data)
                elif self.goal == 'edit':
                    changed_metadata(data)
                    id = data["itemid"]
                    head, tail = os.path.split(data["filepath"])
                    if tail.startswith('tmp_'):
                        data["filepath"] = os.path.join(head, tail[4:len(tail)])
                    try:
                        data["date"] = parser.parse(data["date"])
                    except Exception:
                        data["date"] = datetime.now().date()
                    self.item.update(data) # type: ignore
        except Empty:
            pass
        except MetaTubeException as error:
            downloadprocesserror(str(error))
        finally:
            sleep(0.1)