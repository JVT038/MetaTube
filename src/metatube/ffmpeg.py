import os
import subprocess

from metatube import Config as env
from metatube import logger
from metatube.database import Config


class ffmpeg:
    def __init__(self):
        ffmpeg_path = Config.get_ffmpeg()
        if len(ffmpeg_path) > 0:
            if (
                ffmpeg_path.startswith("/")
                or (ffmpeg_path[0].isalpha() and ffmpeg_path[1].startswith(":\\"))
            ) and len(ffmpeg_path) > 0:
                self.ffmpeg_path = ffmpeg_path
            else:
                self.ffmpeg_path = os.path.join(env.BASE_DIR, ffmpeg_path)
        else:
            self.ffmpeg_path = ""

    def test(self):
        try:
            p = subprocess.Popen(
                "ffmpeg",
                cwd=self.ffmpeg_path,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            p.wait()
            logger.info("FFmpeg has been found!")
            return True
        except Exception as e:
            logger.warn("FFmpeg has not been found at %s", self.ffmpeg_path)
            return str(e)

    # So I wrote this function to exclude fragments from the download, and I spent countless hours trying to figure this out.
    # Then, I grew tired of it and opened an issue on the repo of yt-dlp: https://github.com/yt-dlp/yt-dlp/issues/1669
    # Turns out, yt-dlp has an in-built functions to exclude fragments from the download.
    # So this whole function was all for nothing, and I wasted a lot of time.
    # Because I spent so much time on this, I don't want to delete it, so I'll just leave it here, unused in my project
    '''
    def segments(self, filepath: str, segments: dict, length: str):
        """[summary]

        Args:
            `filepath (Str)`: String to filepath of the input file \n
            `segments (Dict)`: Dictionary containing timestamps of the segments to be skipped. Like this:
                            {
                                {
                                    "start": "150",
                                    "end": "170",
                                }
                                {
                                    "start": "200",
                                    "end": "210"
                                },
                                {
                                    "start": "260",
                                    "end": "270"
                                }
                            }
                            Here from 2:30 (150 seconds) - 2:50 (170 seconds) will be skipped, 3:20 (200 seconds) - 3:30 (210 seconds) will be skipped and 4:20 (260 seconds) to 4:30 (270 seconds) will be skipped \n
            `length (Str)`: String of the total duration of the video / audio file in seconds
        """
        streams = []
        files = []
        # tmpfile = tempfile.NamedTemporaryFile(delete=False)
        ext = filepath.split('.')[len(filepath.split('.')) - 1]
        output_name = filepath[0:len(filepath) - (len(ext) + 1)]
        for i in range(len(segments)):
            filename = output_name + str(i) + "." + ext
            if i == 0:
                (
                ffmpeg_python
                    .input(filepath, c='copy')
                    .trim(start=0, end=segments[i]["start"])
                    .output(filename)
                    .run(cmd=self.ffmpeg_path)
                    # .run_async(pipe_stdout=True, cmd=self.ffmpeg_path)
                )
                streams.append(ffmpeg_python.input(filename))
                files.append(filename)
                print('Converted first segment')
            elif i != 0 and i != len(segments) - 1:
                start = segments[i - 1]["end"]
                (
                ffmpeg_python
                    .input(filepath, c='copy')
                    .trim(start=start, end=segments[i]["start"])
                    .output(filename)
                    .run_async(pipe_stdout=True, cmd=self.ffmpeg_path)
                )

                streams.append(ffmpeg_python.input(filename))
                files.append(filename)
                print(f'Converted segment {i + 1}')
            elif i == len(segments) - 1:
                if segments[i]["end"] != length:
                    in_file = ffmpeg_python.input(filepath, c='copy')
                    start_first = segments[i - 1]["end"]
                    end_first = segments[i]["start"]
                    start_second = segments[i]["end"]
                    end_second = length
                    (
                        ffmpeg_python
                        .concat(
                            in_file.trim(start=start_first, end=end_first),
                            in_file.trim(start=start_second, end=end_second)
                        )
                        .output(filename)
                        .run_async(pipe_stdout=True, cmd=self.ffmpeg_path)
                    )
                    
                    streams.append(ffmpeg_python.input(filename))
                    files.append(filename)
                    print('Converted last segment')
                else:
                    start = segments[i - 1]["end"]
                    try:
                        (
                        ffmpeg_python
                            .input(filepath, c='copy')
                            .trim(start=start, end=segments[i]["start"])
                            .output(filename)
                            .run_async(pipe_stdout=True, cmd=self.ffmpeg_path)
                        )
                    except Exception as e:
                        print(str(e))
                    
                    streams.append(ffmpeg_python.input(filename))
                    files.append(filename)
                    print('Converted last segment')
        (
            ffmpeg_python
            .concat(*streams)
            .output(output_name + "." + "ext")
            .run(overwrite_output=True, cmd=self.ffmpeg_path)
        )
        print('Merged all segments')
        # for file in files:
        #     os.remove(file)
        print('Done converting')
        return True
    '''
