# Created by Sean Nelson on 2009-10-14.
# Copyright 2009 Sean Nelson <audiohacked@gmail.com>
# 
# Overhauled and edited by Garrett Berg on 2011- 1 - 22
# Copyright 2011 Garrett Berg <cloudform511@gmail.com>
# 
# Updated and made Python3 compatible by Juergen Hasch, 20160501
# Copyright 2016 Juergen Hasch <python@elbonia.de>
# 
# This file is part of pyBusPirate.
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

from .base import BPError, BusPirate, ProtocolError


class SPI(BusPirate):
    SPEEDS = {'30kHz' : 0b000,
             '125kHz': 0b001,
             '250kHz': 0b010,
             '1MHz'  : 0b011,
             '2MHz'  : 0b100,
             '2.6MHz': 0b101,
             '4MHz'  : 0b110,
             '8MHz'  : 0b111}

    CFG_SAMPLE = 0x01
    CFG_CLK_EDGE = 0x02
    CFG_IDLE = 0x04
    CFG_PUSH_PULL = 0x08

    PIN_CS = 1
    PIN_AUX = 2
    PIN_PULLUP = 4
    PIN_POWER = 8

    def __init__(self, portname='', speed=115200, timeout=0.1, connect=True):
        """ Provide high-speed access to the Bus Pirate SPI hardware

        Parameters
        ----------
        portname : str
            Name of comport (/dev/bus_pirate or COM3)
        speed : int
            Communication speed, use default of 115200
        timeout : int
            Timeout in s to wait for reply
        connect : bool
            Automatically connect to BusPirate (default) 

        Example
        -------
        >>> from pyBusPirateLite.SPI import SPI
        >>> spi = SPI()
        >>> spi.pins = SPI.PIN_POWER | SPI.PIN_CS
        >>> spi.config = SPI.CFG_PUSH_PULL | SPI.CFG_IDLE
        >>> spi.speed = '1MHz'
        >>> spi.cs = True
        >>> data = spi.transfer( [0x82, 0x00])
        >>> spi.cs = False
        """
        self._config = None
        self._speed = None
        self._cs = None
        self._pins = None
        super().__init__(portname, speed, timeout, connect)

    def enter(self):
        """ Enter raw SPI mode

        Once in raw bitbang mode, send 0x01 to enter raw SPI mode. The Bus Pirate responds 'SPIx',
        where x is the raw SPI protocol version (currently 1). Get the version string at any time by sending 0x01 again.

        Raises
        ------
        BPError
            Could not enter SPI mode

        """
        if self.mode == 'spi':
            return
        if self.mode != 'bb':
           super(SPI, self).enter()

        self.write(0x01)
        if self.response(4) == "SPI1":
            self.mode = 'spi'
            return
        raise BPError('Could not enter SPI mode')

    @property
    def modestring(self):
        """ Return mode version string """
        self.write(0x01)
        self.timeout(self.minDelay * 10)
        return self.response(4)

    @property
    def pins(self):
        return self._pins

    @pins.setter
    def pins(self, cfg):
        """ Configure peripherals

        Parameters
        ----------
        cfg: int
            Pin configuration 0000wxyz
            w=power, x=pull-ups, y=AUX, z=CS

        Notes
        -----
        Enable (1) and disable (0) Bus Pirate peripherals and pins. Bit w enables the power supplies, bit x toggles
        the on-board pull-up resistors, y sets the state of the auxiliary pin, and z sets the chip select pin.
        Features not present in a specific hardware version are ignored. Bus Pirate responds 0x01 on success.

        * CS pin always follows the current HiZ pin configuration.
        * AUX is always a normal pin output (0=GND, 1=3.3volts).
        """
        self.write(0x40 | (cfg & 0x0f))
        if self.response(1, binary=True) != b'\x01':
            raise ValueError("Could not set SPI pins")
        self._pins = cfg

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, cfg):
        """ Set SPI configuration

        This command configures the SPI settings. Options and start-up defaults are the same as the user terminal
        SPI mode. w= pin output HiZ(0)/3.3v(1), x=CKP clock idle phase (low=0), y=CKE clock edge (active to idle=1),
        z=SMP sample time (middle=0). The Bus Pirate responds 0x01 on success.

        Default raw SPI startup condition is 0010. HiZ mode configuration applies to the SPI pins and the CS pin,
        but not the AUX pin. See the PIC24FJ64GA002 datasheet and the SPI section[PDF] of the PIC24 family manual
        for more about the SPI configuration settings.

        Parameters
        ----------
        cfg : byte
                CFG_SAMPLE: sample time (0 = middle)
                CFG_CLK_EDGE: clock edge (1 = active to idle)
                CFG_IDLE: clock idle phase (0 = low)
                CFG_PUSH_PULL: pin output (0 = HiZ, 1 = push-pull)

        Examples
        -------
        >>> spi.config = CFG_PUSH_PULL | CFG_IDLE

        Raises
        ------
        ProtocolError
            If configuration could not be set
        """
        self.write(0x80 | cfg)
        self.timeout(self.minDelay)
        if self.response(1, binary=True) != b'\x01':
            raise ValueError("Could not set SPI configuration")
        self._config = cfg

    def transfer(self, txdata):
        """ Bulk SPI transfer, send/read 1-16 bytes

        Bulk SPI allows direct byte reads and writes. The Bus Pirate expects xxxx+1 data bytes. Up to 16 data bytes
        can be sent at once, each returns a byte read from the SPI bus during the write.

        Note that 0000 indicates 1 byte because there's no reason to send 0. BP replies 0x01 to the bulk SPI command,
        and returns the value read from SPI after each data byte write.

        The way it goes together:

        The upper 4 bit of the command byte are the bulk read command (0001xxxx)
        xxxx = the number of bytes to read. 0000=1, 0001=2, etc, up to 1111=16
        If we want to read (0001) four bytes (0011=3=read 4) the full command is 00010011 (0001 + 0011 ).
        Convert from binary to hex and it is 0x13


        Parameters
        ----------
        txdata: List of bytes
            Data to send (1-16 bytes)

        Returns
        -------
            List containing received data

        Raises
        ------
        ValueError
            If more than 16 bytes are requested to be sent
        """
        length = len(txdata)
        if length > 16:
            ValueError('A maximum of 16 bytes can be sent')
        self.write(0x10 + length-1)
        for data in txdata:
            self.write(data)
        if self.response(1, binary=True) != b'\x01':
            raise ValueError("Could not transfer SPI data")
        rxdata = self.response(length, binary=True)
        return rxdata

    def write_then_read(self, numtx, numrx, txdata, cs=True):
        """ Write then read

        This command was developed to help speed ROM programming with Flashrom. It might be helpful for a lot of common
        SPI operations. It enables chip select, writes 0-4096 bytes, reads 0-4096 bytes, then disables chip select.

        All data for this command can be sent at once, and it will be buffered in the Bus Pirate. The write and read
        operations happen all at once, and the read data is buffered. At the end of the operation, the read data is
        returned from the buffer. The goal is to meet the stringent timing requirements of some ROM chips by buffering
        everything instead of letting the serial port delay things.

        Write then read command format:
        +---------------|--------------------------------|-------------------------------|-----------------------------+
        |command (1byte)| number of write bytes (2bytes) | number of read bytes (2bytes) | bytes to write (0-4096bytes)|
        +---------------|--------------------------------|-------------------------------|-----------------------------+

        Return data format:
        +----------------------|-----------------------------------+
        | success/0x01 (1byte) | bytes read from SPI (0-4096bytes) |
        +----------------------|-----------------------------------+

        1. First send the write then read command (00000100)
        2. The next two bytes (High8/Low8) set the number of bytes to write (0 to 4096)
        3. The next two bytes (h/l) set the number of bytes to read (0 to 4096)
        4. If the number of bytes to read or write are out of bounds, the Bus Pirate will return 0x00 now
        5. Now send the bytes to write. Bytes are buffered in the Bus Pirate, there is no acknowledgment that a byte is received.
        6. Now the Bus Pirate will write the bytes to SPI and read/return the requsted number of read bytes
        7. CS goes low, all write bytes are sent at once
        8. Read starts immediately, all bytes are put into a buffer at max SPI speed (no waiting for UART)
        9. At the end of the read, CS goes high
        10. The Bus Pirate now returns 0x01, success
        11. Finally, the buffered read bytes are returned via the serial port

        Except as described above, there is no acknowledgment that a byte is received.

        Parameters
        ----------
        numtx : int
            Number of bytes to write
        numrx : int
            Number of bytes to read
        txdata : list
            Data to send
        cs : bool
            Generate CS transitions (default=True)

        Raises
        ------
        ProtocolError
            If data could not be sent
        """
        if cs:
            self.write(0x04)
        else:
            self.write(0x05)
        self.write(numtx >> 8 & 0xff)
        self.write(numtx & 0xff)
        self.write(numrx >> 8 & 0xff)
        self.write(numrx & 0xff)
        for data in txdata:
            self.write(data)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError("Error transmitting data")

        return self.response(numrx, binary=True)

    @property
    def cs(self):
        """ Return chip select pin status """
        return self._cs

    @cs.setter
    def cs(self, value):
        """ Set chip select pin
        Parameters
        ----------
        value: bool
            Set CS high(False) or low(True) (i.e. active low CS)

        Raises
        ------
        ProtocolError
            If CS could not be set
        """
        if value:
            self.write(0x02)
        else:
            self.write(0x03)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError("CS could not be set")
        self._cs = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, frequency):
        """ Set SPI bus speed

        Parameters
        ----------
        frequency : str
            SPI clock speed (30kHz, 125kHz, 250kHz, 1MHz, 2MHz, 2.6MHz, 4MHz, 8MHz)

        Raises
        ------
        ProtocolError
            If I2C speed could not be set
        """
        try:
            clock = self.SPEEDS[frequency]
        except KeyError:
            raise ValueError('Clock speed not supported')
        self.write(0x60 | clock)

        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError('Could not set SPI speed')
        self._speed = frequency

    def sniffer(self, cs):
        """ Sniff SPI traffic when CS low(10)/all(01) TODO

        Parameters
        ----------
        cs : Bool
            True: Capture when CS is low
            False: Capture all

        Notes
        -----
        0000 11XX
        The SPI sniffer is implemented in hardware and should work up to 10MHz. It follows the configuration settings
        you entered for SPI mode. The sniffer can read all traffic, or filter by the state of the CS pin.

            [/] - CS enable/disable
            xy - escape character (\\) precedes two byte values X (MOSI pin) and Y (MISO pin) (updated in v5.1)

        Sniffed traffic is encoded according to the table above. The two data bytes are escaped with the '\' character
        to help locate data in the stream.

        Send the SPI sniffer command to start the sniffer, the Bus Pirate responds 0x01 then sniffed data starts to
        flow. Send any byte to exit. Bus Pirate responds 0x01 on exit. (0x01 reply location was changed in v5.8)

        If the sniffer can't keep with the SPI data, the MODE LED turns off and the sniff is aborted. (new in v5.1)

        The sniffer follows the output clock edge and output polarity settings of the SPI mode, but not the input
        sample phase.

        More detailed notes on the SPI sniffer in the SPI user terminal documentation.
        """
        if cs is True:
            cmd = 0x0e
        else:
            cmd = 0x0d
        self.write(cmd)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError('Could not set SPI sniff mode')
