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

class Levels:
  """
    Implements the calculation of the setpoint variable (SV) from a given
    profile.
  """  
  MAX_NUMER_OF_LEVELS = 5

  def __init__(self, start = 0.0, levels = []):
    """
      Initialize a Levels object.
    Args:
        start (float, optional): the first value of the setpoint variable.
          Defaults to 0.0.
        levels (list, optional): the list of rate (r), limit (L), and delay (d)
          to calculate setpoint variable.
    """ 
    self._levels = levels
    self._numberOfLevels = len(levels)
    self._start = [0.0]*self._numberOfLevels
    self._length = [0.0]*self._numberOfLevels
    for i in range(self._numberOfLevels):
      r = self._levels[i][0]
      L = self._levels[i][1]
      d = self._levels[i][2]
      if i == 0:
        self._start[0] = start
        self._length[0] = (L - start)/r + d
      else:
        self._start[i] = self._levels[i - 1][1]
        self._length[i] = self._length[i-1] + (L - self._start[i])/r + d
    
    self._levelID = 0
    self._t = 0.0
    
  def value(self, t = 0.0):
    """
      Get the value of the setpoint variable at the time t (in seconds).
      It's suposed that the time t is always inscreasing when this method
      is called.
    Args:
      t (float, optional): the time to calculate the setpoint variable.
        Defaults to 0.0.

    Returns:
      (float, str): the value of the setpoint variable and its stage on
        the process.
    """
    if t > self._length[self._levelID]:
      if self._levelID < self._numberOfLevels - 1:
        self._levelID += 1

    r = self._levels[self._levelID][0]
    L = self._levels[self._levelID][1]
    d = self._levels[self._levelID][2]
    start = self._start[self._levelID]
    
    if self._levelID == 0:
      diff = 0.0
    else:
      diff = self._length[self._levelID - 1]

    if t <= self._length[self._levelID] - d:
      sp = start + r*(t - diff)
      stage = f"r{self._levelID + 1}"
    else:
      sp = L
      stage = f"L{self._levelID + 1}"

    return sp, stage

  def duration(self):
    """
      Get the duration of the process.

    Returns:
      float: the time (in seconds) to get from the start to the end of the
        process.
    """
    return self._length[self._numberOfLevels - 1]
  
  def limit(self):
    """
      The limit (L) of the current level.
    Returns:
      float: the limit of the setpoint variable.
    """
    return self._levels[self._levelID][1]
  
  def start(self):
    """
      The start value of the process variable at the current level.
    Returns:
      float: the start value.
    """
    return self._start[self._levelID]
