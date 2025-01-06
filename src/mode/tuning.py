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
from machine import Pin
from mode.mode import Mode
from utils.max6675 import MAX6675
from utils.extreme import Extreme
from utils.linear_regression import LinearRegression

class Tuning(Mode):
  """
    Implements the Tuning Mode to control the temperature of two heater
    elements. Those heaters must be connected to a mechanical relay or to a
    State Solid Relay (SSR). The Tuning Mode reads the temperature of
    the two heater elements and use that data to calculate the parameters
    for a PID controller. 
  """
  def __init__(self, name = "", filename = ""):
    super().__init__(name, filename)
 
    self._bottomHeaterTemperature = MAX6675(
      Pin(10, Pin.OUT),
      Pin(11, Pin.OUT),
      Pin(12, Pin.IN)
    )
    self._bottomHeaterSSR = Pin(15, Pin.OUT)
    self._bottomHeaterSSR.low()

    self._topHeaterTemperature = MAX6675(
      Pin(7, Pin.OUT),
      Pin(8, Pin.OUT),
      Pin(9, Pin.IN)
    )
    self._topHeaterSSR = Pin(14, Pin.OUT)
    self._topHeaterSSR.low()
    
    self.PV = 0.0
    self.firstPV = 0.0
    self.SV = self.getValue("SV")
    self.runPeriod = 1000.0*self.getValue("d")
    self.samplePeriod = 1000.0*self.getValue("ap")
    self.stopAt = 0
    # self.DEBUG = True

  def view(self):
    if self.isLocked():
      label = self.menuLabel()
      
      if label == "Run" or label == "Home":
        line1 = label
      else:
        value = self.getValue(label)
        info = self.menuInfo(label)
        unit = info["unit"]
        if len(unit) > 0 and unit[0] == "C":
          unit = "\xDF" + unit

      if label == "SV" or label == "Kp":
        line1 = label + " " + f"{value:5.1f}{unit}"

      if label == "Ki" or label == "Kd":
        line1 = label + " " + f"{value:6.3f}{unit}"

      if label == "ap":
        line1 = label + " " + f"{value:4.1f}{unit}"
        
      if label == "d":
        line1 = label + " " + f"{value:03d}{unit}"

      if self.isRunning():
        line0 = self.fill(f"PV {self.PV:5.1f}\xDFC", f"{self.display(self.getValue('d') - round(self._duration/1000.0))}")
        line1 = self.fill(line1, "[*]")
      else:
        line0 = self.fill(self.name(), "")
        line1 = self.fill(line1, "[>]")
    else:
      line0 = self.fill("Mode", "")
      line1 = self.fill(self.name(), "")
      
    self._lines = [
      line0,
      line1
    ]

    return self._lines

  def run(self):
    self.PV = self._bottomHeaterTemperature.read()

    if not self._isRunning:
      self._startRunning = time.ticks_ms()
      self._lastTime = self._startRunning
      self._duration = 0.0
      
      self.e = Extreme()
      self.lr = LinearRegression()
      
      self._integral = 0.0

      self.stopAt = time.ticks_add(self._startRunning, round(self.samplePeriod))
      self._Min = 1.0e+20
      self._Max = 1.0e-20
      self._firstCross = False
      self.SV = self.getValue("SV")
      self.runPeriod = 1000.0*self.getValue("d")
      self.samplePeriod = 1000.0*self.getValue("ap")
      self.firstPV = self.PV
      self.lastPV = self.PV
      self._menuID = 0
      self._isRunning = True
      self.save()
      factor = 1.0
      if self.DEBUG:
        print(f"t;PV;SV;FACTOR")
        print(f"{0.0};{self.PV};{self.PV};{factor}")

    now = time.ticks_ms()
    self._duration = time.ticks_diff(now, self._startRunning)
    deltat = time.ticks_diff(now, self._lastTime)
   
    if deltat > self.samplePeriod:
      duration = self._duration/1000.0
      deltat /= 1000.0
     
      if self.PV < self.SV:
        factor = 1.0
      else:
        factor = 0.0
        if not self._firstCross:
          self._firstCross = True
          self._firstCrossTime = self._duration
          self._zeroCrosses = 0

      self.stopAt = time.ticks_add(now, round(self.samplePeriod*factor))

      #Save current values as past values
      self._lastTime = now

      if self.DEBUG:
        print(f"{duration};{self.PV};{self.SV};{factor}")

    if self._firstCross:
      #Keep track of the minimum, maximum, and zeros for PV
      self.e.sample(self.PV)
      
      if (self.SV - self.lastPV)*(self.SV - self.PV) < 0.0:
        self._zeroCrosses += 1
      
      self._integral += self.PV - self.SV
    else:
      #Keep track of PV for calculate the linear regression
      self.lr.sample(self._duration/1000.0, self.PV)

    self.lastPV = self.PV

    if time.ticks_diff(self.stopAt, now) > 0:
      self._bottomHeaterSSR.high()
      self._topHeaterSSR.high()
    else:
      self._bottomHeaterSSR.low()
      self._topHeaterSSR.low()

    if self._duration > 1000.0*self._mainMenu["d"]:
      self._regression = self.lr.regression()
      self.setValue("Kp", round(self.e.xMax() - self.e.xMin(), 1))
      self.setValue("Ki", round(0.025*(self._integral*(self._mainMenu['d'] - self._firstCrossTime/1000.0)/(self.e.numberOfSamples()*(self.SV - self.firstPV))), 3))
      self.setValue("Kd", round(0.05*self._regression[0], 3))
      self.stop()

  def stop(self):
    self._isRunning = False
    self.save()
    self._bottomHeaterSSR.low()
    self._topHeaterSSR.low()