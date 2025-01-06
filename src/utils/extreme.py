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

class Extreme:
  """
    Implements the calculation of the minimum and maximum for a given
    sample of values.
  """
  def __init__(self):
    self._numberOfSamples = 0
    self._xMin = 1.0e20
    self._xMax = -1.0e20
    self._yMin = 1.0e20
    self._yMax = -1.0e20

  def sample(self, x = 0.0, y = 0.0):
    """
      Set the x and y sample.
    Args:
      x (float, optional): the value of x sample. Defaults to 0.0.
      y (float, optional): the value of y sample. Defaults to 0.0.
    """    
    #Keep track of min and max.
    if x < self._xMin:
      self._xMin = x
      
    if x > self._xMax:
      self._xMax = x
      
    if y < self._yMin:
      self._yMin = y
      
    if y > self._yMax:
      self._yMax = y

    #Count the number of samples  
    self._numberOfSamples += 1

  def xMin(self):
    """
      Get the minimum x value from the given samples.
    Returns:
      float: the minimum x value.
    """
    return self._xMin
  
  def xMax(self):
    """
      Get the maximum x value from the given samples.
    Returns:
      float: the maximum x value.
    """
    return self._xMax
  
  def yMin(self):
    """
      Get the minimum y value from the given samples.
    Returns:
      float: the minimum y value.
    """
    return self._yMin
  
  def yMax(self):
    """
      Get the maximum y value from the given samples.
    Returns:
      float: the maximum y value.
    """
    return self._yMax
  
  def numberOfSamples(self):
    """
      Get the number of samples.
    Returns:
        int: the number of samples
    """
    return self._numberOfSamples