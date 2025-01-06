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

class Preheater(Mode):
  """
    Implements the Preheater Mode to control the temperature of one heater element.
    That heater must be connected to a mechanical relay or to a 
    State Solid Relay (SSR).
  """
  def __init__(self, name = "", filename = ""):
    super().__init__(name, filename)

    self._bottomHeaterTemperature = MAX6675(
      Pin(10, Pin.OUT), 
      Pin(11, Pin.OUT), 
      Pin(12, Pin.IN)
    )
    
    self.bottomHeaterRelay= Pin(15, Pin.OUT)
    self.bottomHeaterRelay.low()
    self._heaterPID = PID(
      Kp = self.getValue("Kp"),
      Ki = self.getValue("Ki"),
      Kd = self.getValue("Kd"),
    )
    self.stopAt = 0
    self.PV = 0.0
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
      self.startRunning = time.ticks_ms()
      self.firstPV = self.PV
      self.SV = self.getValue("SV")
      self.samplePeriod = 1000.0*self.getValue("ap")
      self.runningPeriod = self.getValue("d")
      self.stopAt = time.ticks_add(self.startRunning, round(self.samplePeriod))
      self.Kp = self.getValue("Kp")
      self._heaterPID.start(self.PV)
      self._heaterPID.coefficients(
        self.Kp,
        self.getValue("Ki"),
        self.getValue("Kd")
      )
      self.lastTime = self.startRunning
      self._duration = 0.0
      self.save()
      self._menuID = 0
      self._isRunning = True
      factor = 1.0

      if self.DEBUG:
        print(f"t;PV;SV;FACTOR;u")
        print(f"{0.0};{self.PV};{self.PV};{factor};0.0")

    now = time.ticks_ms()
    dt = time.ticks_diff(now, self.lastTime)/1000.0
    self._duration = time.ticks_diff(now, self.startRunning)

    if time.ticks_diff(now, self.lastTime) > self.samplePeriod:
      self.u = self._heaterPID.control(self.PV, self.SV, dt)
      self.lastTime = now

      #Calculate actuation period
      factor = 1 - (0.05)**(-self.u/(self.Kp*(-self.SV + self.firstPV)))
      if factor < 0.0:
        factor = 0.0

      self.stopAt = time.ticks_add(now, round(factor*self.samplePeriod))

      if self.DEBUG:
        print(f"{self._duration/1000.0};{self.PV};{self.SV};{factor};{self.u}")

    if time.ticks_diff(self.stopAt, now) > 0:
      self.bottomHeaterRelay.high()
    else:
      self.bottomHeaterRelay.low()

    if self._duration > 1000.0*self.runningPeriod:
      self.stop()

  def stop(self):
    self._isRunning = False
    self.save()
    self.bottomHeaterRelay.low()