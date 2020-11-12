import win32gui
from win32gui import IsWindowVisible, IsWindowEnabled
import win32process

import numpy as np
import cv2

# http://ramblings.timgolden.me.uk/2007/09/26/how-do-i-get-the-window-for-a-subprocesspopen-object/
def get_hwnds_for_pid (pid):

  def callback (hwnd, hwnds):
    if IsWindowVisible (hwnd) and IsWindowEnabled (hwnd):
      _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
      if found_pid == pid:
        hwnds.append (hwnd)
    return True

  hwnds = []
  win32gui.EnumWindows (callback, hwnds)
  return hwnds

def get_window_rect_from_process_id(pid):

   hwnds = get_hwnds_for_pid(pid)

   if not hwnds:
      print("Error - No hwnds")
      return 0, 0

   if len(hwnds) > 1:
      print("Warning: More than one hwnd found - using the first one.")

   rect = win32gui.GetWindowRect(hwnds[0])

   return rect

def pillow_to_opencv_image(image_pillow):

  # use numpy to convert the pil_image into a numpy array
  image_numpy = np.array(image_pillow)  

  # convert to a openCV2 image, notice the COLOR_RGB2BGR which means that 
  # the color is converted from RGB to BGR format
  image_opencv = cv2.cvtColor(image_numpy, cv2.COLOR_RGB2BGR)

  return image_opencv

