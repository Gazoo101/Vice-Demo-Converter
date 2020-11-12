# Libraries - Python (1st Party)
import os
from pathlib import Path
from enum import Enum
from shutil import copyfile

# Libraries - 3rd Party


# Libraries - Local
from vice_demo_to_video_converter import ViceDemoToVideoConverter
from pyffmpeg import PyFfmpeg

class ViceDemoConverter():
   ''' ViceDemoConverter converts recorded Vice Demo's into videos.

   ViceDemoConverter expects each rom to reside in its own folder, with
   said folder being named after the game, e.g.:

   <path_to_some_where>/
      bomb jack/
      blue max/
      paper boy/
      etc.

   In these folders it will look for pre-recorded vice demo files (i.e. start.vsf,
   end.vsf). If found, it will execute Vice with the demo files and export a video.avi
   for each.

   As ViceDemoConverter was created to ease the process of generating C64-related video
   content for PlanMixPlay (www.PlanMixPlay.com), it also automates converting the
   generated .avi files into .mp4 if needed, via ffmpeg. This functionality is optional.

   ViceDemoConverter uses a workspace folder to convert .avi's to .mp4's. It will
   overwrite any .avi/.mp4 files that happen to conflict with the files it needs to
   write. So do *not* use a workspace folder that has any irreplacable .avi/.mp4 files.

   Read ViceDemoToVideoConverter comments re. which Vice version(s) is/are supported.
   '''

   def __init__(self, path_to_workspace, path_to_vice_emu, path_to_ffmpeg = None):

      self.path_to_workspace = path_to_workspace
      self.vice_recorder = ViceDemoToVideoConverter(path_to_vice_emu)
      self.pyffmpeg = PyFfmpeg(path_to_ffmpeg)


   def find_and_convert_demos_to_mp4(self, path_to_roms_folder):
      paths_to_folders_with_recorded_demos = self._detect_folder_with_file_inside(path_to_roms_folder, 'start.vsf')
      self.convert_demos_to_mp4(paths_to_folders_with_recorded_demos)


   def find_and_convert_avis_to_mp4(self, path_to_roms_folder):
      paths_to_videos = self._detect_folder_with_file_inside(path_to_roms_folder, 'video.avi')

      # Copy video.avi's to <name of game>.avi
      paths_to_workspace_videos = self._copy_and_rename_converted_avis_to_workspace(paths_to_videos)

      # .avi -> .mp4
      self.pyffmpeg.convert_videos(paths_to_workspace_videos)


   def convert_demos_to_mp4(self, paths_to_demos : list):
      # .vsf -> .avi
      paths_to_videos = self.vice_recorder.convert_recorded_demos_to_video(paths_to_demos)

      # Copy video.avi's to <name of game>.avi
      paths_to_workspace_videos = self._copy_and_rename_converted_avis_to_workspace(paths_to_videos)

      # .avi -> .mp4
      self.pyffmpeg.convert_videos(paths_to_workspace_videos)
      #self._convert_demo_avis_to_mp4(paths_to_workspace_videos)


   def convert_demos_to_avi(self, paths_to_demos : list):
      return self.vice_recorder.convert_recorded_demos_to_video(paths_to_demos)


   def _copy_and_rename_converted_avis_to_workspace(self, paths_to_video_folders : list):

      paths_to_copied_and_renamed_avis = []

      for path_to_folder_with_video in paths_to_video_folders:

         # We can safely assume that 'path_to_folder_with_video' points to a path with a 'video.avi' inside
         path_to_video = path_to_folder_with_video / "video.avi"

         # We assume that the name of the folder within which the "video.avi" resides corresponds to the
         # name of game
         game_name = path_to_folder_with_video.name

         path_to_video_in_workspace = self.path_to_workspace / (game_name + ".avi")
         #path_to_video_in_workspace.with_suffix(".avi")

         # Can handle PathLib.Path?
         copyfile(path_to_video, path_to_video_in_workspace)

         paths_to_copied_and_renamed_avis.append(path_to_video_in_workspace)

      return paths_to_copied_and_renamed_avis


   def _detect_folder_with_file_inside(self, path_to_folder, file_to_find):
      folders_with_necessary_file  = []

      for entry in os.scandir(path_to_folder):
         entry_path = Path(entry.path)

         path_to_file = entry_path / file_to_find

         if path_to_file.exists() and path_to_file.is_file():
            folders_with_necessary_file.append(entry_path)

      return folders_with_necessary_file