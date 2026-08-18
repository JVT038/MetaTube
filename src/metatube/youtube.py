import asyncio
import json
import os
from functools import partial
from queue import Empty, LifoQueue
from threading import Thread
from time import sleep
from urllib.error import URLError

import yt_dlp
from jinja2 import Environment, PackageLoader, select_autoescape
from youtubesearchpython import VideosSearch
from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessorError
from yt_dlp.postprocessor.metadataparser import MetadataParserPP
from yt_dlp.utils import DownloadError, ExtractorError, PostProcessingError

from metatube import logger, sockets
from metatube.sponsorblock import segments as findsegments


class YouTube:
    @staticmethod
    def is_supported(url):
        extractors = yt_dlp.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME == "youtube":
                return True
        return False

    @staticmethod
    def fetch_url(url, verbose):
        if YouTube.is_supported(url):
            ytdl_options = {"logger": logger, "verbose": verbose}
            with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
                try:
                    info = ytdl.extract_info(url, download=False)
                    return info
                except Exception as e:
                    return str(e)
        else:
            raise ValueError("Invalid URL!")

    @staticmethod
    def verifytemplate(template, info_dict, verbose):
        ytdl_options = {"logger": logger, "verbose": verbose}
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            try:
                filename = ytdl.evaluate_outtmpl(template, info_dict)
                return filename
            except Exception as e:
                return str(e)

    @staticmethod
    def search(query: str):
        logger.info("Searching YouTube for '%s'", query)
        search = VideosSearch(query)
        result = search.result()
        sockets.youtubesearch(result)

    @staticmethod
    async def download(url: list, queue: LifoQueue, ytdl_options: dict):
        download_hook_partial = partial(YouTube.download_hook, queue)
        ytdl_options["progress_hooks"] = [download_hook_partial]
        ytdl_options["postprocessor_hooks"] = [YouTube.postprocessor_hook]
        with yt_dlp.YoutubeDL(ytdl_options) as ytdl:
            try:
                return ytdl.download(url)
            except KeyError as e:
                logger.error("%s key did not exist", str(e))
                sockets.downloaderrors(
                    {
                        "status": "error",
                        "message": "The output template was incorrect. Check logs for more info.",
                    }
                )
                return None
            except ExtractorError as e:
                logger.error("Extractor error: %s", str(e))
                sockets.downloaderrors(
                    {
                        "status": "error",
                        "message": "An extractor error has occured. Check logs for more info.",
                    }
                )
                return None
            except FFmpegPostProcessorError as e:
                logger.error("FFmpegPostProcessor error: %s", str(e))
                sockets.downloaderrors(
                    {
                        "status": "error",
                        "message": "An processing error involving FFmpeg has occured. Check logs for more info.",
                    }
                )
                return None
            except PostProcessingError as e:
                logger.error("Postprocessor error: %s", str(e))
                sockets.downloaderrors(
                    {
                        "status": "error",
                        "message": "A processing error has occured. Check logs for more info.",
                    }
                )
                return None
            except DownloadError as e:
                logger.error("Downloading error: %s", str(e))
                sockets.downloaderrors(
                    {
                        "status": "error",
                        "message": "A downloading error has occured. Check logs for more info.",
                    }
                )
                return None
            except URLError as e:
                logger.error("Network connection error: %s", str(e))
                sockets.downloaderrors(
                    {
                        "status": "error",
                        "message": "A network error occured. Check logs for more info.",
                    }
                )
                return None
            except Exception as e:
                logger.exception("Error during downloading video: %s", str(e))
                sockets.downloaderrors(
                    {
                        "status": "error",
                        "message": "Something has gone wrong. Check logs for more info",
                    }
                )
                return None

    @staticmethod
    def download_hook(queue: LifoQueue, d):
        queue.put(d)

    @staticmethod
    def postprocessor_hook(d):
        if d["status"] == "processing":
            sockets.postprocessing(d["postprocessor"])
        elif d["status"] == "finished":
            sockets.finished_postprocessor(
                d["postprocessor"], d["info_dict"]["filepath"]
            )

    @staticmethod
    def get_options(
        ext,
        output_folder,
        type,
        output_format,
        bitrate,
        skipfragments,
        proxy_data,
        ffmpeg,
        hw_transcoding,
        vaapi_device,
        width,
        height,
        verbose,
    ):
        proxy = json.loads(proxy_data)
        filepath = os.path.join(output_folder, output_format)
        segments = json.loads(skipfragments)
        postprocessors = []
        postprocessor_args = {}
        proxy_string = ""
        ext = "m4a" if "m4a" in ext else ext
        """
        Audio:
        If an audio type has been selected, first try to look for a format with the selected extension
        If no audio format with the selected extension has been found, just look for the best audio format
        and automatically convert it to the selected extension anyway
        Video:
        Exactly the same for videos
        """
        format = (
            f"ba[ext={ext}]/ba"
            if type == "Audio"
            else f"b[ext={ext}]/ba+bv[ext={ext}]/b/ba+bv"
        )

        # choose whether to use the FFmpegExtractAudio post processor or the FFmpegVideoConverter one
        if type == "Audio":
            postprocessors.append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": ext,
                    "preferredquality": bitrate,
                }
            )
        elif type == "Video":
            postprocessors.append(
                {"key": "FFmpegVideoConvertor", "preferedformat": ext}
            )
            postprocessor_args["videoconvertor"] = []
            if bitrate != "best":
                postprocessor_args["videoconvertor"] = ["-b:a", str(bitrate) + "k"]

            if height != "best" and width != "best":
                postprocessor_args["videoconvertor"][:0] = [
                    "-vf",
                    "scale=" + str(width) + ":" + str(height),
                ]

            # If hardware transcoding isn't None, add a hardware transcoding thingy to the FFmpeg arguments
            if hw_transcoding != "None":
                if "videoconvertor" not in postprocessor_args:
                    postprocessor_args["videoconvertor"] = []
                if hw_transcoding == "nvenc":
                    postprocessor_args["videoconvertor"].extend(["-c:v", "h264_nvenc"])
                elif hw_transcoding == "qsv":
                    postprocessor_args["videoconvertor"].extend(["-c:v", "h264_qsv"])
                elif hw_transcoding == "videotoolbox":
                    postprocessor_args["videoconvertor"].extend(
                        ["-c:v", "h264_videotoolbox"]
                    )
                elif "vaapi" in hw_transcoding:
                    postprocessor_args["videoconvertor"].extend(
                        ["-vaapi_device", vaapi_device, "-c:v", "h264_vaapi"]
                    )
                elif hw_transcoding == "amd":
                    postprocessor_args["videoconvertor"].extend(["-c:v", "h264_amf"])
                elif hw_transcoding == "omx":
                    postprocessor_args["videoconvertor"].extend(["-c:v", "h264_omx"])

        # If segments have been submitted by the user to exclude, add a ModifyChapters key and add ranges
        if len(segments) > 0:
            ranges = []
            for segment in segments:
                if len(segment["start"]) < 1 or len(segment["end"]) < 1:
                    sockets.searchvideo("Enter all fragment fields!")
                    return False
                else:
                    ranges.append((int(segment["start"]), int(segment["end"])))
            postprocessors.append({"key": "ModifyChapters", "remove_ranges": ranges})

        """
        --parse-metadata example in CLI:
        yt-dlp orJSJGHjBLI -x --audio-format mp3 --add-metadata -o "%(track,title)s - %(artist)s.%(ext)s" --parse-metadata " Bad Habits: %(title)s" --parse-metadata "Ed Sheeran:%(artist)s"
        """
        # postprocessors.append({
        #     'actions': [
        #         (MetadataParserPP.interpretter, " " + metadata['title'], ' %(title)s'),
        #         (MetadataParserPP.interpretter, metadata['album'], '%(album)s'),
        #         (MetadataParserPP.interpretter, ';'.join(json.loads(metadata['album_artists'])), '%(album_artist)s'),
        #         (MetadataParserPP.interpretter, metadata['album_tracknr'], '%(track_number)s'),
        #     ],
        #     'key': 'MetadataParser',
        #     'when': 'pre_process'
        # })

        ytdl_options = {
            "format": format,
            "merge_output_format": ext,
            "postprocessors": postprocessors,
            "postprocessor_args": postprocessor_args,
            "ffmpeg_location": ffmpeg,
            "logger": logger,
            "outtmpl": filepath,
            "noplaylist": True,
            "verbose": verbose,
        }

        # Add proxy if proxy is enabled
        if proxy["proxy_type"] != "None":
            proxy_string = proxy["proxy_type"].lower().strip() + "://"
            if len(proxy["proxy_username"]) > 0 and len(proxy["proxy_username"]) > 0:
                proxy_string += (
                    proxy["proxy_username"]
                    + ":"
                    + proxy["proxy_password"]
                    + "@"
                    + proxy["proxy_address"].strip()
                    + ":"
                    + proxy["proxy_port"].strip()
                )
            else:
                proxy_string += (
                    proxy["proxy_address"].strip() + ":" + proxy["proxy_port"].strip()
                )
            ytdl_options["proxy"] = proxy_string
        return ytdl_options

    @staticmethod
    def start_download(url, ytdl_options):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue = LifoQueue()
        coros = [YouTube.download(url, queue, ytdl_options)]
        future = asyncio.gather(*coros)
        thread = Thread(target=YouTube.loop_in_thread, args=[loop, future])
        thread.start()
        # While the future isn't finished yet continue
        while not future.done():
            try:
                # Get the latest status update from the que and print it
                d = queue.get_nowait()
                if d["status"] == "downloading":
                    if "total_bytes_estimate" in d:
                        downloaded_bytes = d["downloaded_bytes"] or "Unknown"
                        total_bytes = (
                            d["total_bytes_estimate"] or d["total_bytes"] or "Unknown"
                        )
                        sockets.downloadprogress(downloaded_bytes, total_bytes)
                elif d["status"] == "processing":
                    sockets.postprocessing(d["postprocessor"])
                elif d["status"] == "finished":
                    sockets.finished_download()
            except Empty:
                pass
            finally:
                # Sleep between checking for updates
                sleep(0.1)

    @staticmethod
    def loop_in_thread(loop, future):
        loop.run_until_complete(future)

    @staticmethod
    def fetch_video(video, templates, metadata_sources, defaulttemplate):
        sb = findsegments(video["webpage_url"])
        segments = sb if type(sb) == list else "error"
        env = Environment(
            loader=PackageLoader("metatube"), autoescape=select_autoescape()
        )
        downloadtemplate = env.get_template("downloadform.html")
        metadatatemplate = env.get_template("metadataform.html")
        downloadform = downloadtemplate.render(
            templates=templates, segments=segments, default=defaulttemplate
        )
        metadataform = metadatatemplate.render(metadata_sources=metadata_sources)
        sockets.youtuberesults(video, downloadform, metadataform)
