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
from machine import ADC, Pin, I2C
from utils.keyesadkey import KeyesADKey
from utils.i2c_lcd import I2cLcd
from mode.preheater import Preheater
from mode.reballing import Reballing
from mode.tuning import Tuning

# Comunicate with HD44780 LCD connected via I2C.
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
lcd.clear()

# Connect to channel 0 (GP26)
adc = ADC(0)
keyboard = KeyesADKey(adc)

models = [
  Preheater("Preheater", "/config/preheater.json"),
  Reballing("Reballing", "/config/reballing.json"),
  Tuning("Auto Tuning", "/config/tuning.json")
]

currentModel = 0
modelsCount = len(models)
lastKey = -1.0
lcd.clear()
i = 0
while True:
  key = keyboard.read()

  if models[currentModel].isLocked():
    if key == keyboard.LEFT:
      models[currentModel].previousMenu()

    if key == keyboard.RIGHT:
      models[currentModel].nextMenu()

    if key == keyboard.UP:
      models[currentModel].increaseParameter()
      
    if key == keyboard.DOWN:
      models[currentModel].decreaseParameter()

    if key == keyboard.SELECT and lastKey != keyboard.SELECT:
      label = models[currentModel].menuLabel()
      if label == "Home":
        models[currentModel].stop()
        models[currentModel].unlock()

      if label == "Run":
        if models[currentModel].isRunning():
          models[currentModel].stop()
        else:
          models[currentModel].run()

      if label != "Home" and label != "Run":
        models[currentModel].stop()
    else:
      if models[currentModel].isRunning():
        models[currentModel].run()
  else:
    if key == keyboard.LEFT:
        currentModel = (currentModel - 1)%modelsCount

    if key == keyboard.RIGHT:
        currentModel = (currentModel + 1)%modelsCount

    if key == keyboard.SELECT and lastKey != keyboard.LONG_SELECT:
      models[currentModel].lock()

  lines = models[currentModel].view()

  lastKey = key
  lcd.move_to(0, 0)
  lcd.putstr(lines[0])
  lcd.move_to(0, 1)
  lcd.putstr(lines[1])
 
  time.sleep(1.0/60)