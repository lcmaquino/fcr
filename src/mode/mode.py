"""
 * Copyright (c) 2025 Luiz C. M. de Aquino <aquino.luizclaudio@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU General Public License,
 * version 2, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json

class Mode():
  """
    Implements a Mode that will be avaliable on the reworking station.
  """
  _menuID = 0
  _menuCount = 0
  _filename = ""
  _isLocked = False
  _isRunning = False
  _lines = ["", ""]
  _name = ""
  DEBUG = False
  
  def __init__(self, name = "", filename = ""):
    """
    Initialize a Mode object.

    Args:
        name (str, optional): the name for the Mode. Defaults to "".
        filename (str, optional): the JSON file with informations used
          by this object. Defaults to "".
    """
    self._name = name
    
    self._filename = filename
    with open(filename) as f:
      self._mainMenu = json.load(f)

    self._mainMenuCount = len(self._mainMenu["order"])

    self._pidFilename = "/config/pid.json"
    with open(self._pidFilename) as f:
      self._menuPID = json.load(f)
    
    self._menuPIDCount = len(self._menuPID["order"])
    
    self._menuCount = self._mainMenuCount + self._menuPIDCount + 2
    
  def run(self):
    """
      Run the code for the Mode to work properly.
    """    
    pass
  
  def isRunning(self):
    """
      It's represents the Mode state.

    Returns:
      bool: It's True if the Mode is running. False otherwise.
    """    
    return self._isRunning

  def stop(self):
    """
      It stops the working Mode.
    """    
    pass
  
  def view(self):
    """
      It should return the text to be displayed on the LCD.
    """
    pass

  def nextMenu(self):
    """
      Set the next menu available.
    """
    if self._menuID < self._menuCount - 1:
      self._menuID += 1
    else:
      self._menuID = 0

  def previousMenu(self):
    """
      Set the previous menu available.
    """
    if self._menuID > 0:
      self._menuID -= 1
    else:
      self._menuID = self._menuCount - 1

  def menuID(self):
    """
      Get the current menu ID.
    
    Returns:
      integer: the index of the current menu.
    """
    return self._menuID

  def menuCount(self):
    """
      Get the number of available menus.
    
    Returns:
      integer: the number of available menus.
    """
    return self._menuCount
  
  def menuLabel(self):
    """
      Get the label of the current menu.
    
    Returns:
      str: the label of the current menu.
    """
    if self._menuID < self._mainMenuCount:
      label = self._mainMenu["order"][self._menuID]

    if self._menuID >= self._mainMenuCount and self._menuID < self._mainMenuCount + self._menuPIDCount:
      label = self._menuPID["order"][self._menuID - self._mainMenuCount]

    if self._menuID == self._menuCount - 2:
      label = "Run"

    if self._menuID == self._menuCount - 1:
      label = "Home"

    return str(label)
  
  def menuInfo(self, label = ""):
    """
      Get informations about the menu item.

    Args:
      label (str, optional): the menu label. Defaults to "".

    Returns:
      dictionary: the dictionary with keys "min", "max", "step", and "unit".
    """
    if label in ["Kp", "Ki", "Kd", "ap"]:
      return self._menuPID["info"][label]
    else:
      return self._mainMenu["info"][label]

  def getValue(self, label = ""):
    """
      Get the value of the menu.

    Args:
      label (str, optional): the menu label. Defaults to "".

    Returns:
      mixed: the value of the menu.
    """
    if label in ["Kp", "Ki", "Kd", "ap"]:
      return self._menuPID[label]
    else:
      return self._mainMenu[label]

  def setValue(self, label = "", value = None):
    """
      Set the value of the menu.

    Args:
      label (str, optional): the menu label. Defaults to "".
    """
    if label in ["Kp", "Ki", "Kd", "ap"]:
      self._menuPID[label] = value
    else:
      self._mainMenu[label] = value

  def increaseParameter(self):
    """
      Increase the value of the current menu.
    """
    label = self.menuLabel()
    if label not in ["Run", "Home"]:
      if label in ["Kp", "Ki", "Kd", "ap"]:
        info = self._menuPID["info"][label]
        max = info["max"]
        step = info["step"]
        if self._menuPID[label] + step <= max:
          self._menuPID[label] += step
      else:
        info = self._mainMenu["info"][label]
        max = info["max"]
        step = info["step"]
        if self._mainMenu[label] + step <= max:
          self._mainMenu[label] += step
  
  def decreaseParameter(self):
    """
      Decrease the value of the current menu.
    """
    label = self.menuLabel()
    if label not in ["Run", "Home"]:
      if label in ["Kp", "Ki", "Kd", "ap"]:
        info = self._menuPID["info"][label]
        min = info["min"]
        step = info["step"]
        if self._menuPID[label] - step >= min:
          self._menuPID[label] -= step
      else:
        info = self._mainMenu["info"][label]
        min = info["min"]
        step = info["step"]
        if self._mainMenu[label] - step >= min:
          self._mainMenu[label] -= step
  
  def save(self):
    """
      Save the JSON files used by the Mode for persistence of its data.
    """
    with open(self._filename, "w") as f:
      json.dump(self._mainMenu, f)

    with open(self._pidFilename, "w") as f:
      json.dump(self._menuPID, f)
  
  def lock(self):
    """
      Lock the Mode to indicate that its being used.
    """
    self._isLocked = True

    with open(self._pidFilename) as f:
      self._menuPID = json.load(f)

  def unlock(self):
    """
      Unlock the Mode so other ones could be used.
    """
    self._menuID = 0
    self._isLocked = False

  def isLocked(self):
    """
      Unlock the Mode so other ones could be used.

    Returns:
      bool: It's True if the Mode is lock. Otherwise is False.
    """
    return self._isLocked
  
  def fill(self, start = "", end = ""):
    """
    It concatenate start and end with spaces beteween them.

    Args:
      start (str, optional): The start of the text. Defaults to "".
      end (str, optional): The end of the text. Defaults to "".

    Returns:
      str: the concatenated text with 16 characteres.
    """
    n = 16 - (len(start) + len(end))

    if n <= 0:
      spaces = " "
    else:
      spaces = " "*n
    
    line = start + spaces + end
    line = line[0:16]

    return line

  def name(self):
    """
    Get the name of the Mode.

    Returns:
      str: the name of the Mode.
    """
    return self._name
  
  def setName(self, name = ""):
    """
    Set the name of the Mode.
    Args:
      name (str): the mode name.
        Defaults to ""
    """
    self._name = name

  def display(self, seconds = 0):
    """
    Get the given seconds and convert to the format mm:ss.

    Args:
      seconds (int, optional): The number of seconds to be displayed as mm:ss.
        Defaults to 0.

    Returns:
      str: the given seconds in the format mm:ss.
    """    
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"