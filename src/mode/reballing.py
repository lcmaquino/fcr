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
from utils.pid import PID
from utils.levels import Levels

class Reballing(Mode):
  """
    Implements the Reballing Mode to control the temperature of two heater 
    elements. Those heaters must be connected to a mechanical relay or to a 
    State Solid Relay (SSR).
  """
  def __init__(self, name = "", filename = ""):
    super().__init__(name, filename)
    self._ptnID = 1

    self.bottomHeaterTemperature = MAX6675(
      Pin(10, Pin.OUT),
      Pin(11, Pin.OUT),
      Pin(12, Pin.IN)
    )
    
    self.topHeaterRelay = Pin(14, Pin.OUT)
    self.topHeaterRelay.low()

    self.bottomHeaterRelay = Pin(15, Pin.OUT)
    self.bottomHeaterRelay.low()
  
    self.Kp = self.getValue("Kp")
    self.heaterPID = PID(
      Kp = self.Kp,
      Ki = self.getValue("Ki"),
      Kd = self.getValue("Kd"),
    )
    
    self.stopAt = 0
    self.PV = 0.0
    self.SV = 0.0
    self._levels = Levels()
    self.stage = ""
    self.samplePeriod = 1000.0*self.getValue("ap")
    # self.DEBUG = True

  def view(self):
    if self.isLocked():
      label = self.menuLabel()
      
      if label == "Run" or label == "Home":
        line1 = label

      if label == "PTN":
        line1 = f"PTN{self._ptnID}"
        unit = ""

      if label not in ["PTN", "Run", "Home"]:
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

      if label[0] == 'r':
        value = self._mainMenu[f"PTN{self._ptnID}"][label]
        line1 = label + " " + f"{value:5.2f}{unit}"
      
      if label[0] in ['L', 'd']:
        value = self._mainMenu[f"PTN{self._ptnID}"][label]
        line1 = label + " " + f"{value:5.1f}{unit}"
      
      if self.isRunning():
        line0 = self.fill(f"PV {self.PV:5.1f}\xDFC", f"{self.display(round(self._levels.duration() - self._duration))}")
        if label == "PTN":
          line1 = self.fill(f"SV {self.SV:5.1f}\xDFC", "[*]")
        else:
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
    self.PV = self.bottomHeaterTemperature.read()

    if not self._isRunning:
      levels = []
      for i in range(1, 6):
        r = self.getValue(f"r{i}")

        if r == 0.0:
          break

        L =  self.getValue(f"L{i}")
        d = self.getValue(f"d{i}") 
         
        levels.append([r, L, d])

      self._startRunning = time.ticks_ms()
      self._lastTime = self._startRunning
      self._duration = 0.0
      self._levels = Levels(self.PV, levels)
      self.heaterPID.start(self.PV)
      self.Kp = self.getValue("Kp")
      self.heaterPID.coefficients(
        self.Kp,
        self.getValue("Ki"),
        self.getValue("Kd")
      )
      self.samplePeriod = 1000.0*self.getValue("ap")
      self.stopAt = time.ticks_add(self._startRunning, round(self.samplePeriod))
      self.save()
      self._menuID = 0   
      self.u = 0
      self._isRunning = True
      factor = 1.0
      if self.DEBUG:
        print(f"t;PV;SV;FACTOR;u")
        print(f"{0.0};{self.PV};{self.PV};{factor};0.0")

    now = time.ticks_ms()
    dt = time.ticks_diff(now, self._lastTime)/1000.0
    self._duration = time.ticks_diff(now, self._startRunning)/1000.0

    self.SV, self.stage = self._levels.value(self._duration)

    if time.ticks_diff(now, self._lastTime) > self.samplePeriod:
      self.u = self.heaterPID.control(self.PV, self.SV, dt)
      self._lastTime = now

      #Calculate actuation period
      factor = 1 - (0.05)**(-self.u/(self.Kp*(-self._levels.limit() + self._levels.start())))
      if factor < 0.0:
        factor = 0.0

      self._actuationPeriod = factor*self.samplePeriod
     
      if self._actuationPeriod > self.samplePeriod:
        self._actuationPeriod = self.samplePeriod

      self.stopAt = time.ticks_add(now, round(self._actuationPeriod))

      if self.DEBUG:
        print(f"{self._duration};{self.PV};{self.SV};{factor};{self.u}")

    if time.ticks_diff(self.stopAt, now) > 0:
      self.bottomHeaterRelay.high()
      self.topHeaterRelay.high()
    else:
      self.bottomHeaterRelay.low()
      self.topHeaterRelay.low()

    if self._duration > self._levels.duration():
      self.stop()

  def stop(self):
    self._isRunning = False
    self.save()
    self.bottomHeaterRelay.low()
    self.topHeaterRelay.low()

  def menuInfo(self, label = ""):
    if label in ["Kp", "Ki", "Kd", "ap"]:
      return self._menuPID["info"][label]
    else:
      if label[0] in ["r", "L", "d"]:
        return self._mainMenu["info"][label[0]]
      else:
        return self._mainMenu["info"][label]

  def getValue(self, label = ""):
    if label in ["Kp", "Ki", "Kd", "ap"]:
      return self._menuPID[label]
    else:
      if label[0] in ["r", "L", "d"]:
        return self._mainMenu[f"PTN{self._ptnID}"][label]
      else:
        return self._mainMenu[label]

  def setValue(self, label = "", value = None):
    if label not in ["Run", "Home"]:
      if label in ["Kp", "Ki", "Kd", "ap"]:
        self._menuPID[label] = value
      else:
        if label[0] in ["r", "L", "d"]:
          self._mainMenu[f"PTN{self._ptnID}"][label] = value
        else:
          self._mainMenu[label] = value
  
  def increaseParameter(self):
    label = self.menuLabel()     
    if label not in ["Run", "Home"]:
      if label in ["Kp", "Ki", "Kd", "ap"]:
        info = self._menuPID["info"][label]
        max = info["max"]
        step = info["step"]
        if self._menuPID[label] + step <= max:
          self._menuPID[label] += step
      else:
        if label[0] in ['r', 'L', 'd']:       
          info = self._mainMenu["info"][label[0]]
          max = info["max"]
          step = info["step"]
          
          if self._mainMenu[f"PTN{self._ptnID}"][label] + step <= max:
            self._mainMenu[f"PTN{self._ptnID}"][label] += step
        else:
          info = self._mainMenu["info"][label]
          max = info["max"]
          step = info["step"]
          
          if self._ptnID + step <= max:
            self._ptnID += step
            
  def decreaseParameter(self):
    label = self.menuLabel()  
    if label not in ["Run", "Home"]:
      if label in ["Kp", "Ki", "Kd", "ap"]:
        info = self._menuPID["info"][label]
        min = info["min"]
        step = info["step"]
        if self._menuPID[label] - step >= min:
          self._menuPID[label] -= step
      else:
        if label[0] in ['r', 'L', 'd']:       
          info = self._mainMenu["info"][label[0]]
          min = info["min"]
          step = info["step"]
          
          if self._mainMenu[f"PTN{self._ptnID}"][label] - step >= min:
            self._mainMenu[f"PTN{self._ptnID}"][label] -= step
        else:
          info = self._mainMenu["info"][label]
          min = info["min"]
          step = info["step"]
          
          if self._ptnID - step >= min:
            self._ptnID -= step