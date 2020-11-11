# Libraries - Python (1st Party)
import subprocess
from pathlib import Path

# Libraries - 3rd Party

# Libraries - Local libraries

class PyFfmpeg():


   def __init__(self, path_to_ffmpeg):
      self.path_to_ffmpeg = path_to_ffmpeg


   def convert_videos(self, path_to_videos):

      args = ["-i", "video.avi", "output.mp4"]

      subprocess.run()


      # ffmpeg -i bbbb.avi other.mp4