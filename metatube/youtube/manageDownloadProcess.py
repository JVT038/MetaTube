from .downloadOptions import downloadOptions
from .download import download
from metatube.metadata.processMetadata import processMetadata
from metatube.metadata.mergeMetadata import mergeMetadata
from metatube.sockets import metadata_error, downloaderrors
from metatube.Exception import MetaTubeException
from threading import Thread
from queue import Empty, LifoQueue
from time import sleep
class manageDownloadProcess(object):
    def __init__(self, downloadOptions: downloadOptions, metadataProcessor: processMetadata, url: str, goal: 'str'):
        self.downloadOptions = downloadOptions
        self.metadataProcessor = metadataProcessor
        self.url = url
        self.goal = goal
        
    def start_download(self):
        try:
            metadata = self.metadataProcessor.getMetadata()
        except MetaTubeException as error:
            metadata_error(str(error))
            return
        try:
            yt_dlpOptions = self.downloadOptions.optionsToDictMapper(metadata) 
        except MetaTubeException as error:
            downloaderrors(str(error))
            return
        queue = LifoQueue()
        downloadProcess = Thread(target=download.start_download, args=[self.url, yt_dlpOptions, queue])
        downloadProcess.start()
        downloadProcess.join()
        try:
            lastItem = queue.get_nowait()
            filepath = lastItem['filepath']
            merge = mergeMetadata(filepath, self.goal, metadata=metadata)
            if self.downloadOptions.ext in ['MP3', 'OPUS', 'FLAC', 'OGG']:
                merge.mergeaudiodata()
            elif self.downloadOptions.ext in ['MP4', 'M4A']:
                merge.mergevideodata()
            elif self.downloadOptions.ext in ['WAV']:
                merge.mergeid3data()
        except Empty:
            pass
        except MetaTubeException as error:
            metadata_error(str(error))
        finally:
            sleep(0.1)