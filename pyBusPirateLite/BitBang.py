# Created by Sean Nelson on 2009-10-14.
# Copyright 2009 Sean Nelson <audiohacked@gmail.com>
# 
# Overhauled and edited by Garrett Berg on 2011- 1 - 22
# Copyright 2011 Garrett Berg <cloudform511@gmail.com>
# 
# pyBusPirate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pyBusPirate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pyBusPirate.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from typing import List, Optional, Union, ClassVar

from .base import BusPirate

# Pin constants for BitBang mode
PIN_CS    = 0b00001
PIN_MISO  = 0b00010
PIN_CLK   = 0b00100
PIN_MOSI  = 0b01000
PIN_AUX   = 0b10000
PIN_POWER = 0b100000
PIN_PULLUP = 0b1000000

class BitBang(BusPirate):
    """BitBang interface for Bus Pirate.

    This class provides access to the Bus Pirate's BitBang interface. It allows
    direct control of the Bus Pirate's pins.

    Attributes:
        portname (str): Name of the serial port (e.g., '/dev/bus_pirate' or 'COM3')
        speed (int): Communication speed in baud
        timeout (float): Timeout in seconds for read operations
        ser (serial.Serial): Serial port object
        mode (str): Current mode of the Bus Pirate
        connected (bool): Whether the Bus Pirate is connected
    """

    # Pin definitions
    PIN_CS: ClassVar[int] = 0x01
    PIN_MISO: ClassVar[int] = 0x02
    PIN_CLK: ClassVar[int] = 0x04
    PIN_MOSI: ClassVar[int] = 0x08
    PIN_AUX: ClassVar[int] = 0x10
    PIN_PULLUP: ClassVar[int] = 0x20
    PIN_POWER: ClassVar[int] = 0x40

    def __init__(
        self,
        portname: str = "",
        speed: int = 115200,
        timeout: float = 0.1,
        connect: bool = True,
    ) -> None:
        """Initialize the BitBang interface.

        Args:
            portname: Name of the serial port (e.g., '/dev/bus_pirate' or 'COM3')
            speed: Communication speed in baud (default: 115200)
            timeout: Timeout in seconds for read operations (default: 0.1)
            connect: Whether to connect immediately (default: True)

        Raises:
            ValueError: If connection fails
        """
        super().__init__(portname, speed, timeout, connect)

    def enter(self) -> bool:
        """Enter BitBang mode.

        Returns:
            bool: True if successful

        Raises:
            ValueError: If entering BitBang mode fails
        """
        if self.mode == 'bb':
            return True
        if self.mode != 'bb':
            super(BitBang, self).enter()
        self.write(0x00)
        self.timeout(self.minDelay * 10)
        if self.response(4) == "BBIO1":
            self.mode = 'bb'
            self.bp_config = 0x00  # configuration bits determine action of power sources and pullups
            self.bp_port = 0x00  # out_port similar to ports in microcontrollers
            self.bp_dir = 0x1F  # direction port similar to microchip microcontrollers.  (1) is input, (0) is output
            self.port.flushInput()
            return True
        self.recurse_flush(self.enter)
        raise ValueError('Could not enter BitBang mode')

    def write(self, data: Union[bytes, List[int]]) -> None:
        """Write data to the Bus Pirate.

        Args:
            data: Data to write (bytes or list of integers)

        Raises:
            IOError: If write fails
        """
        if isinstance(data, int):
            if data > 0xFF:
                raise IOError('Illegal extended AUX command')
            self.port.write(bytes([data]))
            return

        if isinstance(data, list):
            data = bytes(data)
        self.port.write(data)

    def read(self, length: int = 1) -> bytes:
        """Read data from the Bus Pirate.

        Args:
            length: Number of bytes to read (default: 1)

        Returns:
            bytes: Read data

        Raises:
            IOError: If read fails
        """
        return self.port.read(length)

    def configure(self, power: bool = False, pullup: bool = False) -> None:
        """Configure BitBang interface.

        Args:
            power: Whether to enable power supply (default: False)
            pullup: Whether to enable pullup resistors (default: False)

        Raises:
            IOError: If configuration fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        # Send config command
        config = 0
        if power:
            config |= self.PIN_POWER
        if pullup:
            config |= self.PIN_PULLUP

        self.write([0x80 | config])

        # Read response
        response = self.read(1)
        if response[0] != 0x01:
            raise IOError('Error configuring pins')

        self.bp_config = config

    def self_test(self) -> None:
        """Run self test.

        Raises:
            IOError: If self test fails
        """
        if not self.connected:
            raise ValueError("Not connected to Bus Pirate")

        # Send self test command
        self.write(0x0F)

        # Read response
        response = self.read(1)
        if response[0] != 0x01:
            raise IOError('Self test did not return to bitbang mode')

    @property
    def outputs(self):
        """
        Returns
        -------
        byte
            Current state of the pins
            PIN_AUX, PIN_MOSI, PIN_CLK, PIN_MISO, PIN_CS

        """

        self.write(0x40 | ~ self.pins_direction & 0x1f)  # map input->1, output->0  **TODO**
        self.timeout(self.minDelay * 10)
        return ord(self.response(1, binary=True)) & 0x1f

    @outputs.setter
    def outputs(self, pinlist=0):
        """ Configure pins as input our output

        Notes
        -----
        The Bus pirate responds to each direction update with a byte showing the current state of the pins, regardless
        of direction. This is useful for open collector I/O modes. Used in every mode to configure pins.
        In bb it configures as either input or output, in the other modes it normally configures peripherals such as
        power supply and the aux pin

        Parameters
        ----------
        pinlist : byte
            List of pins to be set as outputs (default: all inputs)
            PIN_AUX, PIN_MOSI, PIN_CLK, PIN_MISO, PIN_CS

        Returns
        -------
        byte
            Current state of the pins
            PIN_AUX, PIN_MOSI, PIN_CLK, PIN_MISO, PIN_CS
        """
        self.pins_direction = pinlist & 0x1f
        self.write(0x40 | ~ self.pins_direction & 0x1f)  # map input->1, output->0
        self.timeout(self.minDelay * 10)
        self.response(1, binary=True)

    @property
    def pins(self):
        """ Get pins status

        Returns
        -------
        byte
            Current state of the pins
            PIN_POWER, PIN_PULLUP, PIN_AUX, PIN_MOSI, PIN_CLK, PIN_MISO, PIN_CS
        """
        self.write(0x80 | (self.pins_state & 0x7f))
        self.timeout(self.minDelay * 10)
        self.pins_state = ord(self.response(1, binary=True)) & 0x7f
        return self.pins_state

    @pins.setter
    def pins(self, pinlist=0):
        """ Set pins to high or low

        Notes
        -----
        The lower 7bits of the command byte control the Bus Pirate pins and peripherals.
        Bitbang works like a player piano or bitmap. The Bus Pirate pins map to the bits in the command byte as follows:
        1|POWER|PULLUP|AUX|MOSI|CLK|MISO|CS
        The Bus pirate responds to each update with a byte in the same format that shows the current state of the pins.

        Parameters
        ----------
        pinlist : byte
            List of pins to be set high
            PIN_POWER, PIN_PULLUP, PIN_AUX, PIN_MOSI, PIN_CLK, PIN_MISO, PIN_CS

        """
        self.pins_state = pinlist & 0x7f
        self.write(0x80 | self.pins_state)
        self.timeout(self.minDelay * 10)
        self.pins_state = ord(self.response(1, binary=True)) & 0x7f

    @property
    def adc(self):
        """Returns the voltage from ADC pin

        Returns
        -------
        float
            Voltage measured at ADC pin
        """
        self.write(0x14)
        self.timeout(self.minDelay)
        ret = self.response(2, binary=True)
        voltage = (ret[0] << 8) + ret[1]
        voltage = (voltage * 6.6) / 1024
        return voltage

    def start_getting_adc_voltages(self):
        """Start continuously getting adc voltages.

        Notes
        -----
        use memberfunction enter_bb to exit,
        use get_next_adc_voltage to get the next one.
        """
        self.write(0x15)

    def get_next_adc_voltage(self):
        ret = self.response(2, binary=True)
        voltage = (ret[0] << 8) + ret[1]
        voltage = (voltage * 6.6) / 1024

        if voltage < 10:
            """sometimes the input gets out of sync.  This is the best error checking
            currently available, firmware will probably be updated to expect a 101 or
            something in the top byte, which will be better error checking"""
            self.recurse_end()
            return voltage

        self.response(1, binary=True) # get an additional byte and then flush
        self.port.flushInput()
        return self.recurse(self.get_next_adc_voltage)

    def stop_getting_adc_voltages(self):
        """I was encountering problems resetting out of adc mode, so I wrote this
        little function"""
        self.port.flushInput()
        for i in range(5):
            self.write(0x00)
            #r, w, e = select.select([self.port], [], [], 0.01);
            r = self.response(1, binary=True)
            if r: break;
        self.port.flushInput()
        self.enter_bb()
        return 1

    def selftest(self, complete=False):
        """ Self test

        Parameters
        ----------
        complete: bool
            Requires jumpers between +5 and Vpu, +3.3 and ADC

        Notes
        -----
        Self-tests are access from the binary bitbang mode. There are actually two self-tests available. T
        he full test is the same as self-test in the user terminal, it requires jumpers between two sets of pins
        in order to test some features. The short test eliminates the six checks that require jumpers.

        After the test is complete, the Bus Pirate responds with the number of errors. It also echoes any input plus
        the number of errors. The MODE LED blinks if the test was successful, or remains solid if there were errors.
        Exit the self-test by sending 0xff, the Bus Pirate will respond 0x01 and return to binary bitbang mode.

        Returns
        -------
        int
            Number of errors
        """
        self.port.flushInput()
        if complete is True:
            self.write(0x11)
        else:
            self.write(0x10)
        self.timeout(1)
        errors = self.response(1, binary=True)
        self.write(0xff)
        resp = self.response(1, binary=True)
        if resp != b'\x01':
            raise ValueError('Self test did not return to bitbang mode')
        self.timeout(self.minDelay)
        return ord(errors)

    def enable_PWM(self, frequency, dutycycle=.5):
        """ Enable PWM output 

        Parameters
        ----------
        frequency: float
            PWM frequency in Hz
        dutycycle: float
            Duty cycle between 0 (0%) and 1 (100%)

        Notes
        -----
        Configure and enable pulse-width modulation output in the AUX pin. Requires a 5 byte configuration sequence.
        Responds 0x01 after a complete sequence is received. The PWM remains active after leaving binary bitbang mode!
        Equations to calculate the PWM frequency and period are in the PIC24F output compare manual.
        Bit 0 and 1 of the first configuration byte set the prescaler value. The Next two bytes set the duty cycle
        register, high 8bits first. The final two bytes set the period register, high 8bits first.
        
        Parameter calculation stolen from http://codepad.org/qtYpZmIF

        """
        if dutycycle > 1:
            raise ValueError('Duty cycle should be between 0 and 1')
        Fosc = 24e6
        Tcy = 2.0 / Fosc
        PwmPeriod = 1.0 / frequency

        # find needed prescaler
        PrescalerList = {0: 1, 1: 8, 2: 64, 3: 256}

        for n in range(4):
            Prescaler = PrescalerList[n]
            PRy = PwmPeriod * 1.0 / (Tcy * Prescaler)
            PRy = int(PRy - 1)
            OCR = int(PRy * dutycycle)

            if PRy < (2 ** 16 - 1):
                break  # valid value for PRy, keep values
        else:
            raise ValueError('frequency requested is invalid')

        prescaler = Prescaler
        dutycycle = OCR
        period = PRy

        self.write(0x12)
        self.write(prescaler)
        self.write((dutycycle >> 8) & 0xFF)
        self.write(dutycycle & 0xFF)
        self.write((period >> 8) & 0xFF)
        self.write(period & 0xFF)
        self.timeout(self.minDelay * 10)
        if self.response(1, binary=True) != b'\x01':
            raise ValueError("Could not setup PWM mode")

    def disable_PWM(self):
        """ Clear/disable PWM """
        self.write(0x13)
        self.timeout(self.minDelay * 10)
        if self.response(1, binary=True) != b'\x01':
            raise ValueError("Could not disable PWM mode")
