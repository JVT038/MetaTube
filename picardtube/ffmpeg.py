import subprocess, os
from picardtube.database import Config
from picardtube import Config as env


class ffmpeg():
    def __init__(self):
        ffmpeg_path = Config.query.get(1).ffmpeg_directory
        if ffmpeg_path.startswith('/') or (ffmpeg_path[0].isalpha() and ffmpeg_path[1].startswith(':\\')):
            self.ffmpeg_path = ffmpeg_path
        else:
            self.ffmpeg_path = os.path.join(env.BASE_DIR, ffmpeg_path)
    def test(self):
        try:
            p = subprocess.Popen('ffmpeg', cwd=self.ffmpeg_path, shell=True)
            p.wait()
            return True
        except Exception as e:
            return str(e)