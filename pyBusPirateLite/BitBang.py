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

from .base import BusPirate, ProtocolError


class BitBang(BusPirate):
    """ Provide access to the Bus Pirate bitbang mode"""

    def __init__(self, portname='', speed=115200, timeout=0.1, connect=True):
        """
        This constructor by default conntects to the first buspirate it can
        find. If you don't want that, set connect to False.

        Parameters
        ----------
        portname : str
            Name of comport (/dev/bus_pirate or COM3)
        speed : int
            Communication speed, use default of 115200
        timeout : int
            Timeout in s to wait for reply
 
        Examples
        --------
        >>> bb = BitBang()
        """
        super().__init__(portname, speed, timeout, connect)

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
            raise ProtocolError('Self test did not return to bitbang mode')
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
