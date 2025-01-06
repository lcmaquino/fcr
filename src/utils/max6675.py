"""
 * MIT License
 * 
 * Copyright (c) 2016 Ivan Sevcik
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
"""

import time
class MAX6675:
    MEASUREMENT_PERIOD_MS = 220

    def __init__(self, sck, cs, so):
        """
        Creates new object for controlling MAX6675
        :param sck: SCK (clock) pin, must be configured as Pin.OUT
        :param cs: CS (select) pin, must be configured as Pin.OUT
        :param so: SO (data) pin, must be configured as Pin.IN
        """
        # Thermocouple
        self._sck = sck
        self._sck.low()

        self._cs = cs
        self._cs.high()

        self._so = so
        self._so.low()

        self._last_measurement_start = 0
        self._last_read_temp = 0
        self._error = 0

    def _cycle_sck(self):
        self._sck.high()
        time.sleep_us(1)
        self._sck.low()
        time.sleep_us(1)

    def refresh(self):
        """
        Start a new measurement.
        """
        self._cs.low()
        time.sleep_us(10)
        self._cs.high()
        self._last_measurement_start = time.ticks_ms()

    def ready(self):
        """
        Signals if measurement is finished.
        :return: True if measurement is ready for reading.
        """
        return time.ticks_diff(time.ticks_ms(), self._last_measurement_start) > MAX6675.MEASUREMENT_PERIOD_MS

    def error(self):
        """
        Returns error bit of last reading. If this bit is set (=1), there's problem with the
        thermocouple - it can be damaged or loosely connected
        :return: Error bit value
        """
        return self._error

    def read(self):
        """
        Reads last measurement and starts a new one. If new measurement is not ready yet, returns last value.
        Note: The last measurement can be quite old (e.g. since last call to `read`).
        To refresh measurement, call `refresh` and wait for `ready` to become True before reading.
        :return: Measured temperature
        """
        # Check if new reading is available
        if self.ready():
            # Bring CS pin low to start protocol for reading result of
            # the conversion process. Forcing the pin down outputs
            # first (dummy) sign bit 15.
            self._cs.low()
            time.sleep_us(10)

            # Read temperature bits 14-3 from MAX6675.
            value = 0
            for i in range(12):
                # SCK should resemble clock signal and new SO value
                # is presented at falling edge
                self._cycle_sck()
                value += self._so.value() << (11 - i)

            # Read the TC Input pin to check if the input is open
            self._cycle_sck()
            self._error = self._so.value()

            # Read the last two bits to complete protocol
            for i in range(2):
                self._cycle_sck()

            # Finish protocol and start new measurement
            self._cs.high()
            self._last_measurement_start = time.ticks_ms()

            self._last_read_temp = value * 0.25

        return self._last_read_temp