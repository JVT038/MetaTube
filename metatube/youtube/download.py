import yt_dlp, os
from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessorError
from threading import Thread
from urllib.error import URLError
from yt_dlp.utils import ExtractorError, DownloadError, PostProcessingError
from metatube import sockets, logger
from functools import partial
from queue import LifoQueue, Empty
from time import sleep
import asyncio

class download(object):
    @staticmethod
    async def download(url: list, queue: LifoQueue, ytdl_options: dict):
        download_hook_partial = partial(download.download_hook, queue)
        postprocessor_hook_partial = partial(download.postprocessor_hook, queue)
        ytdl_options['progress_hooks'] = [download_hook_partial]
        ytdl_options['postprocessor_hooks'] = [postprocessor_hook_partial]
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            try:
                return ytdl.download(url)
            except KeyError as e:
                logger.error('%s key did not exist', str(e))
                sockets.downloaderrors({'status': 'error', 'message': 'The output template was incorrect. Check logs for more info.'})
                return None
            except ExtractorError as e:
                logger.error('Extractor error: %s', str(e))
                sockets.downloaderrors({'status': 'error', 'message': 'An extractor error has occured. Check logs for more info.'})
                return None
            except FFmpegPostProcessorError as e:
                logger.error('FFmpegPostProcessor error: %s', str(e))
                sockets.downloaderrors({'status': 'error', 'message': 'An processing error involving FFmpeg has occured. Check logs for more info.'})
                return None
            except PostProcessingError as e:
                logger.error('Postprocessor error: %s', str(e))
                sockets.downloaderrors({'status': 'error', 'message': 'A processing error has occured. Check logs for more info.'})
                return None
            except DownloadError as e:
                logger.error('Downloading error: %s', str(e))
                sockets.downloaderrors({'status': 'error', 'message': 'A downloading error has occured. Check logs for more info.'})
                return None
            except URLError as e:
                logger.error('Network connection error: %s', str(e))
                sockets.downloaderrors({'status': 'error', 'message': 'A network error occured. Check logs for more info.'})
                return None
            except Exception as e:
                logger.exception('Error during downloading video: %s', str(e))
                sockets.downloaderrors({'status': 'error', 'message': 'Something has gone wrong. Check logs for more info'})
                return None
    
    @staticmethod
    def download_hook(queue: LifoQueue, d: dict):
        queue.put(d)

    @staticmethod
    def postprocessor_hook(queue: LifoQueue, d: dict):
        if d['status'] == 'processing':
            sockets.postprocessing(d['postprocessor'])
        elif d['status'] == 'finished':
            if d['postprocessor'] == 'MoveFiles':
                sockets.finished_postprocessor(d['postprocessor'], d['info_dict']['filepath'])
                queue.put({'status': 'mergedata', 'filepath': d['info_dict']['filepath']})
    
    @staticmethod
    def start_download(url, ytdl_options, queue: LifoQueue):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        coros = [download.download(url, queue, ytdl_options)]
        future = asyncio.gather(*coros)
        thread = Thread(target=download.loop_in_thread, args=[loop, future])
        thread.start()
        # While the future isn't finished yet continue
        while not future.done():
            try:
                # Get the latest status update from the queue and print it
                d = queue.get_nowait()
                if d['status'] == 'downloading':
                    if "total_bytes_estimate" in d:
                        downloaded_bytes = d['downloaded_bytes'] or 'Unknown'
                        total_bytes = d['total_bytes_estimate'] or d['total_bytes'] or 'Unknown'
                        sockets.downloadprogress(downloaded_bytes, total_bytes)
                elif d['status'] == 'processing':
                    sockets.postprocessing(d['postprocessor'])
                elif d['status'] == 'finished':
                        sockets.finished_download()
                elif d['status'] == 'mergedata':
                    break
            except Empty:
                pass
            finally:
                # Sleep between checking for updates
                sleep(0.1)
    
    @staticmethod
    def loop_in_thread(loop, future):
        loop.run_until_complete(future)