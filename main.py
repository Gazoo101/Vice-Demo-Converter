# Libraries - Python (1st Party)
from pathlib import Path


# Libraries - 3rd Party


# Libraries - Local libraries
from vice_demo_converter import ViceDemoConverter


def append_path_all_entries(path_to_append : Path, entries : list):
   entries_appended = []

   for entry in entries:
      entries_appended.append(path_to_append / entry)

   return entries_appended


if __name__ == "__main__":

   path_to_vice = Path(r"D:\<path>\<to>\<vice>\x64sc.exe")
   path_to_ffmpeg = Path(r"D:\<path>\<to>\<ffmpeg>\ffmpeg\bin\ffmpeg.exe")
   path_to_workspace_folder = Path(r"D:\<path>\<to>\<workspace>")
   path_to_games = Path(r"D:\<path>\<to>\Roms")

   vice_converter = ViceDemoConverter(path_to_workspace_folder, path_to_vice, path_to_ffmpeg)

   # Convert explicit game demos
   game_recordings_to_convert = []
   game_recordings_to_convert += ["Bop'n Rumble (979)"]
   game_recordings_to_convert += ["KRAKOUT_04191_01"]
   game_recordings_to_convert += ["Ghosts'n Goblins (3136)"]

   # Overwrite for debugging
   game_recordings_to_convert = ["Ghosts'n Goblins (3136)"]

   ###
   # Example 1 -- Hand-picked start.vsf -> video.avi
   abs_path_game_recordings_to_convert = append_path_all_entries(path_to_games, game_recordings_to_convert)
   #vice_converter.convert_demos_to_avi(abs_path_game_recordings_to_convert)

   ###
   # Example 2 -- All video.avi -> <game name>.mp4
   vice_converter.find_and_convert_avis_to_mp4(path_to_games)

   ###
   # Example 3 -- All start.vsf -> <game name>.mp4
   #vice_converter.find_and_convert_demos_to_mp4(path_to_games)
