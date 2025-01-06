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

class LinearRegression:
  """
    Implements the calculation of the linear regression for a given
    sample of values.
  """
  def __init__(self):
    self._numberOfSamples = 0
    self._dotSum = 0.0
    self._xSum = 0.0
    self._xSquaredSum = 0.0
    self._ySum = 0.0

  def sample(self, x = 0.0, y = 0.0):
    """
      Set the x and y sample.
    Args:
      x (float, optional): the value of x sample. Defaults to 0.0.
      y (float, optional): the value of y sample. Defaults to 0.0.
    """
    #Keep the values for calculating Linear Regression
    self._dotSum += x*y
    self._xSum += x
    self._ySum += y
    self._xSquaredSum += x**2
    
    #Count the number of samples  
    self._numberOfSamples += 1
 
  def regression(self):
    """
      Calculate the linear regression for the samples.
    Returns:
        float, float: the angular coefficient and the linear coefficient of the linear regression.
    """    
    a = (self._numberOfSamples*self._dotSum - self._xSum*self._ySum)/(self._numberOfSamples*self._xSquaredSum - self._xSum**2)
    b = (self._ySum*self._xSquaredSum - self._xSum*self._dotSum)/(self._numberOfSamples*self._xSquaredSum - self._xSum**2)
    return a, b

  def numberOfSamples(self):
    """
      Get the number of samples.
    Returns:
        int: the number of samples
    """
    return self._numberOfSamples