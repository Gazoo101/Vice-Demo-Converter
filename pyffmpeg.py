# Libraries - Python (1st Party)
import subprocess
from pathlib import Path

# Libraries - 3rd Party

# Libraries - Local libraries

class PyFfmpeg():

   def __init__(self, path_to_ffmpeg):
      self.path_to_ffmpeg = path_to_ffmpeg

      if path_to_ffmpeg == None:
         print("Warning no path to ffmpeg provided. No video conversions can take place.")

      self.ffmpeg_execution_command = [str(self.path_to_ffmpeg), "-i", "<input_path>", "<output_path>"]


   def convert_videos(self, path_to_video_avis):

      for path_to_video in path_to_video_avis:

         path_to_video_mp4 = path_to_video
         path_to_video_mp4 = path_to_video_mp4.with_suffix(".mp4")

         execution_commands = self.ffmpeg_execution_command
         execution_commands[2] = str(path_to_video)
         execution_commands[3] = str(path_to_video_mp4)

         subprocess.run(execution_commands)
