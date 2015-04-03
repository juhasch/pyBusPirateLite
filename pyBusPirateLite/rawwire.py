"""
Created by Sean Nelson on 2009-10-14.
Copyright 2009 Sean Nelson <audiohacked@gmail.com>

Overhauled and edited by Garrett Berg on 2011- 1 - 22
Copyright 2011 Garrett Berg <cloudform511@gmail.com>

This file is part of pyBusPirate.

pyBusPirate is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyBusPirate is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyBusPirate.  If not, see <http://www.gnu.org/licenses/>.
"""

try:
   from .BitBang import BBIO
except ValueError:
   from BitBang import BBIO

class RawWireCfg:
	NA = 0x01
	LSB = 0x02
	_3WIRE = 0x04
	OUTPUT = 0x08

class RawWire(BBIO):
	def start_bit(self):
		'''is kept in because it was in for legacy code,
		I recommend you use send_start_bit'''
		self.check_mode('raw')
		self.port.write("\x02")
		self.timeout(0.1)
		return self.response(1)

	def stop_bit(self):
		'''is kept in because it was in for legacy code,
		I recommend you use send_stop_bit'''
		self.check_mode('raw')
		self.port.write("\x03")
		self.timeout(0.1)
		return self.response(1)

	def read_bit(self):
		self.check_mode('raw')
		self.port.write("\x07")
		self.timeout(0.1)
		return self.response(1)

	def peek(self):
		self.check_mode('raw')
		self.port.write("\x08")
		self.timeout(0.1)
		return self.response(1)

	def clock_tick(self):
		self.check_mode('raw')
		self.port.write("\x09")
		self.timeout(0.1)
		return self.response(1)

	def clock_low(self):
		self.check_mode('raw')
		self.port.write("\x0A")
		self.timeout(0.1)
		return self.response(1)

	def clock_high(self):
		self.check_mode('raw')
		self.port.write("\x0B")
		self.timeout(0.1)
		return self.response(1)

	def data_low(self):
		self.check_mode('raw')
		self.port.write("\x0C")
		self.timeout(0.1)
		return self.response(1)

	def data_high(self):
		self.check_mode('raw')
		self.port.write("\x0D")
		self.timeout(0.1)
		return self.response(1)

	def wire_cfg(self, pins = 0):
		self.check_mode('raw')
		self.port.write(0x80 | pins)
		self.timeout(0.1)
		return self.response(1)

	#if someone who cares could write a more user-friendly wire_cfg that would be cool
	# (make it similar to my configure_peripherals)

	def bulk_clock_ticks(self, ticks = 1):
		self.check_mode('raw')
		self.port.write(0x20 | (ticks - 1))
		self.timeout(0.1)
		return self.response(1)
