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

class PID:
  """
    Implements the Proportional-integral-derivative (PID) controller.
    The PID controller automatically compares the desired setpoint variable (SV)
    with the actual value of process variable (PV). The difference between these 
    two values is called the error value, denoted as e(t). The error value is
    used to calculate the control variable (u(t)) by the function:
    
    u(t) = Kp*(u(t)) + Ki*integrate(u, 0, t) + Kp*(du(t)/dt),
    
    where Kp, Ki, and Kd are float coefficients for the proportional, integral,
    and derivative terms respectively. The integrate represents the integral
    of u over [0, t].
  """
  def __init__(self, Kp = 1.0, Ki = 1.0, Kd = 1.0):
    """
      Initialize a PID object.
    Args:
      Kp (float, optional): the proportional coefficient. Defaults to 1.0.
      Ki (float, optional): the integral coefficient. Defaults to 1.0.
      Kd (float, optional): the derivative coefficient. Defaults to 1.0.
    """    
    self._Kp = Kp
    self._Ki = Ki
    self._Kd = Kd
  
  def control(self, process, setpoint, dt = 0.0001):
    """
      Calculate the PID control variable (u(t)).

    Args:
      process (float): the process variable (PV).
      setpoint (float): the setpoint variable (SV).
      dt (float): the time increment used for discretization. Defaults to 0.0001.

    Returns:
      float: the control variable (u(t)) value.
    """
    
    up = self._Kp*(setpoint - process)
    ui = self._lastui + self._Ki*(setpoint - process)*dt
    ud = self._Kd*((setpoint - process) - (self._lastSetpoint - self._lastProcess))/dt
    u = up + ui + ud
    self._lastSetpoint = setpoint
    self._lastProcess = process
    self._lastui = ui
    return u
  
  def start(self, process):
    """
      Starts the PID controller with the first read of the process variable (PV).
    Args:
      process (float): the process variable (PV).
    """    
    self._lastui = 0.0
    self._lastSetpoint = process
    self._lastProcess = process
    
  def coefficients(self, Kp = 0.0, Ki = 0.0, Kd = 0.0):
    """
      Set the coefficients for the PID controller.
    Args:
      Kp (float, optional): the proportional coefficient. Defaults to 0.0.
      Ki (float, optional): the integral coefficient. Defaults to 0.0.
      Kd (float, optional): the derivative coefficient. Defaults to 0.0.
    """    
    self._Kp = Kp
    self._Ki = Ki
    self._Kd = Kd