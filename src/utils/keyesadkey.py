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

import time
from math import fabs

class KeyesADKey:
  """
    Implements the API for talking with Keyes_AD_Key compatible keypads.
  """
  MEASUREMENT_PERIOD_MS = 10
  LONG_PUSH_COUNT = 10
  STBY = -1.0
  LEFT = 0.01
  UP = 0.14
  DOWN = 0.32
  RIGHT = 0.48
  SELECT = 0.70
  LONG_SELECT = 1.4
  TOLERANCE = 0.01

  def __init__(self, adc):
    """
      Initialize a KeyesADKey object.
    Args:
        adc (ADC): a machine.ADC object.
    """    
    self._adc = adc
    self.lastMeasurementStart = time.ticks_ms()
    self._lastReadValue = KeyesADKey.STBY
    self._error = 0
    self._clickCount = 0

  def ready(self):
    """
      Get if the keypad is ready for read.
    Returns:
      bool: It's True if the keypad is ready for read. Otherwise False.
    """
    return time.ticks_diff(time.ticks_ms(), self.lastMeasurementStart) > KeyesADKey.MEASUREMENT_PERIOD_MS

  def read(self):
    """
      Read the keypad voltage output.
    Returns:
        float: the voltage associated with the switch clicked on the keypad.
          It returns -1.0 if no swtich was clicked on the keypad.
    """
    if self.ready():
      v = self._adc.read_u16()*(1.0/65535)
      if fabs(v - self._lastReadValue) < KeyesADKey.TOLERANCE:
        self._clickCount += 1
      else:
        self._clickCount = 0

      self._lastReadValue = v
      self.lastMeasurementStart = time.ticks_ms()
      
      if fabs(v - KeyesADKey.LEFT) < KeyesADKey.TOLERANCE:
        return KeyesADKey.LEFT

      if fabs(v - KeyesADKey.UP) < KeyesADKey.TOLERANCE:
        return KeyesADKey.UP
      
      if fabs(v - KeyesADKey.DOWN) < KeyesADKey.TOLERANCE:
        return KeyesADKey.DOWN

      if fabs(v - KeyesADKey.RIGHT) < KeyesADKey.TOLERANCE:
        return KeyesADKey.RIGHT

      if (fabs(v - KeyesADKey.SELECT) < KeyesADKey.TOLERANCE) and (self._clickCount >= KeyesADKey.LONG_PUSH_COUNT):
        self._clickCount = 0
        return KeyesADKey.LONG_SELECT

      if fabs(v - KeyesADKey.SELECT) < KeyesADKey.TOLERANCE:
        return KeyesADKey.SELECT

    return KeyesADKey.STBY