# Python (1st Party)
import time
import subprocess

from pathlib import Path
#from collections import namedtuple

# 3rd Party libraries
import pyautogui
from sympy import Point2D
import numpy as np
import cv2
from PIL import ImageGrab

# PMP - Local libraries
#from utilities import get_hwnds_for_pid
from utilities import get_window_rect_from_process_id
from utilities import pillow_to_opencv_image

class ViceDemoToVideoConverter():
   """ ViceDemoToVideoConverter converts recorder Vice demo's to video.

   For the functionality Vice does *not* expose via command-line or hotkeys,
   ViceDemoToVideoConverter uses pyautogui to interact with Vice. Unfortunately,
   this ties the interaction strongly to the exact GUI Vice offers. This
   class was developed for the SDL2-based (*not* newer GTK3-based) GUI.

   You can download this version of Vice here:
   https://sourceforge.net/projects/vice-emu/files/releases/binaries/windows/WinVICE-3.2-x86.7z/download

   """

   def __init__(self, path_to_vice_emu):
      self.vice_playback_polling_interval = 3   # Seconds
      self.path_to_vice_emu = path_to_vice_emu

      path_to_vice_playback_graphic = Path("./playback-tile.png").absolute()

      if path_to_vice_playback_graphic.exists():
         self.image_vice_playback_template = cv2.imread(str(path_to_vice_playback_graphic))

         print("Warning: Without a template tile for Vice playback, playback cannot be detected.")
      
      self.window_vice_rect = None
      self.size_vice_playback_area = Point2D(120, 60)

      self.detection_threshold_playback_tile = 0.9

      self.vice_command_line_arguments = []
      #self.vice_command_line_arguments += ["-VICIIfilter", "0"]      # Disable CRT filter

      self.vice_command_line_arguments += ["-playback"]

      self.pos_offset_menu_snapshot = Point2D(90, 40)
      self.pos_offset_menu_snapshot_start_stop_playback_history = Point2D(90, 180)

      # Appears to work, and then immediately not work.
      #self.vice_command_line_arguments += ["+VICIIdsize"]
      #self.vice_command_line_arguments += ["+VICIIdscan"]

   def _update_vice_window_properties(self, vice_window_rect):

      self.window_vice_rect = vice_window_rect

      self.window_vice_top_left = Point2D( self.window_vice_rect[0], self.window_vice_rect[1] )
      self.window_vice_bottom_right = Point2D( self.window_vice_rect[2], self.window_vice_rect[3] )
      self.window_vice_size = self.window_vice_bottom_right - self.window_vice_top_left


   def convert_recorded_demos_to_video(self, paths_to_rom_folders):

      paths_to_recorded_videos = []

      for path_to_rom_folder in paths_to_rom_folders:

         if (path_to_rom_folder.exists() == False):
            print(f"Couldn't find path: {path_to_rom_folder} - Skipping")
            continue

         path_to_rom_recording_start = path_to_rom_folder / "start.vsf"

         if path_to_rom_recording_start == False:
            print(f"Couldn't find rom recording start: {path_to_rom_recording_start} - Skipping")
            continue

         print(f"Now processing: {path_to_rom_folder}")
         path_to_recorded_video = self._convert_recorded_demo_to_video(path_to_rom_recording_start, self.vice_command_line_arguments)

         paths_to_recorded_videos.append(path_to_recorded_video)

         print("done one")

      print("done all")

      return paths_to_recorded_videos


   def _is_vice_playback_occurring(self):
      """ _is_vice_playback_occurring() detects if Vice is still engaged in playing back a recorded demo.
      
      The function uses a small image template of a screenshot of Vice displaying some playback related
      text. If this image template is detected within a small region of the lower-right of Vice's GUI
      it is assumed that demo playback is occurring.

      Approaches using pyautogui .pixel() or .locate() functionality did not work.
      """

      point_to_grab = self.window_vice_bottom_right - self.size_vice_playback_area

      lower_bottom_rect = (point_to_grab.x, point_to_grab.y, self.window_vice_bottom_right.x, self.window_vice_bottom_right.y)

      # The argument 'all_screens=True' is required in order for PIL to
      # properly perform a .grab() outside of the primary monitor.
      image_pillow = ImageGrab.grab(lower_bottom_rect, all_screens=True)
      #image.show()

      image_opencv = pillow_to_opencv_image(image_pillow)

      result = cv2.matchTemplate(image_opencv, self.image_vice_playback_template, cv2.TM_CCOEFF_NORMED)
      min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

      if max_val > self.detection_threshold_playback_tile:
         #print("playback detected")
         return True
      else:
         #print("NO playback detected")
         return False


      


   def _wait_until_vice_demo_playback_completes(self):
      # Simple polling approach to

      vice_playback_active = True

      while vice_playback_active:
         time.sleep(self.vice_playback_polling_interval)
         vice_playback_active = self._is_vice_playback_occurring()


   def _debug_draw_pixels(self, pos_start : Point2D, size : Point2D):
      import numpy as np
      #import scipy.misc as smp # Deprecated
      from PIL import Image

      data = np.zeros( (size.y, size.x, 3), dtype=np.uint8 )

      for y in range(size.y):
         for x in range(size.x):

            pixel_x = int(pos_start.x + x)
            pixel_y = int(pos_start.y + y)

            color1 = pyautogui.pixel(pixel_x, pixel_y)

            data[y,x] = color1

            print(f"x {x}, y {y}")

      img = Image.fromarray( data )
      img.show()


   def _trigger_vice_start_stop_playback(self):
      """ _trigger_vice_start_stop_playback() starts/stops Vice recorded playback via pyautogui
      by simulating mouse moves/clicks.

      Has since been superceded by simply passing '-playback' to Vice.
      """

      pos_menu_snapshot = self.window_vice_top_left + self.pos_offset_menu_snapshot
      pos_menu_snapshot_start_stop_playback = self.window_vice_top_left + self.pos_offset_menu_snapshot_start_stop_playback_history

      pyautogui.moveTo(pos_menu_snapshot.x, pos_menu_snapshot.y)
      pyautogui.click()
      time.sleep(1.0)

      pyautogui.moveTo(pos_menu_snapshot_start_stop_playback.x, pos_menu_snapshot_start_stop_playback.y)
      pyautogui.click()
      time.sleep(1.0)


   def _trigger_vice_save_stop_media_file(self, media_filename : Path):
      
      pyautogui.hotkey('alt', 'c')
      time.sleep(1.5) # This menu doesn't pop 'immediately'

      print(f"Exporting recording to: {media_filename}")

      # Vice will be in whatever folder the recent rom opening was in - so we must set the current
      # folder/file to be where we're currently recording / running the demo.
      pos_filename = self.window_vice_top_left + Point2D(100, 260)
      pos_select_driver = self.window_vice_top_left + Point2D(100, 330)
      pos_select_driver_ffmpeg = self.window_vice_top_left + Point2D(100, 490)
      
      pyautogui.moveTo(pos_filename.x, pos_filename.y)
      time.sleep(1.0)

      # We don't click as we expect this field to already be highlighted
      pyautogui.typewrite(str(media_filename))

      pyautogui.moveTo(pos_select_driver.x, pos_select_driver.y)
      time.sleep(1.0)
      pyautogui.click()

      pyautogui.moveTo(pos_select_driver_ffmpeg.x, pos_select_driver_ffmpeg.y)
      time.sleep(1.0)
      pyautogui.click()

      time.sleep(3.0)

      pyautogui.press('enter')


   def _convert_recorded_demo_to_video(self, path_to_rom_recording_start: Path, additional_arguments):
      
      # Vice expects both a 'start.vsf' and a 'end.vsf' file to be present when
      # replaying a recorded demo. We set the CWD to where the 'start.vsf' file is
      # located in order to help Vice find the 'end.vsf' file.
      
      path_to_vsfs = path_to_rom_recording_start.parent

      # Vice.exe + graphics/recording settings + path_to_vsf_start
      # path_to_vsf_start *must* be placed at the end
      vice_and_arguments = [str(self.path_to_vice_emu)] + additional_arguments + [str(path_to_rom_recording_start)]

      # No starting demo for now
      #vice_and_arguments = [str(self.path_to_vice_emu)] + additional_arguments


      # Developers Note:
      # We used trigger Vice as an external process using 'with', i.e.:
      #     with subprocess.Popen(vice_and_arguments, cwd=str(path_to_vsfs)) as proc:
      #
      # Although this appears to automatically contain code-execution within the 'with'
      # scope until the process is killed, it also seems to suppress a number of errors
      # from properly stopping execution and highlighting errors. Therefore, we've
      # opted to do without the 'with' scope approach.
      proc = subprocess.Popen(vice_and_arguments, cwd=str(path_to_vsfs))

      # Give Vice time to boot
      time.sleep(5.0)

      window_vice_rect = get_window_rect_from_process_id(proc.pid)
      self._update_vice_window_properties(window_vice_rect)

      # Wait for Vice to load up the 'start.vsf' state
      # time.sleep(3.0)

      #self._trigger_vice_start_stop_playback()

      video_filename = path_to_vsfs / "video.avi"

      # video file to make
      #testy = path_to_rom_recording_start.stem()

      # Trigger recording of media
      self._trigger_vice_save_stop_media_file(video_filename)

      self._wait_until_vice_demo_playback_completes()

      # Once playback has finished - we auto-stop media recording
      pyautogui.hotkey('alt', 'c')

      time.sleep(3.0)

      proc.kill()

      return video_filename



   