import subprocess, os
from picardtube.database import Config
from picardtube import Config as env

class ffmpeg():
    def __init__(self):
        ffmpeg_path = Config.query.get(1).ffmpeg_directory
        self.ffmpeg_path = os.path.join(env.BASE_DIR, ffmpeg_path)
    def test(self):
        try:
            p = subprocess.Popen('ffmpeg', cwd=self.ffmpeg_path, shell=True)
            p.wait()
            return "FFmpeg application has been found"
        except Exception as e:
            return str(e)