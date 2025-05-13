# Created by Sean Nelson on 2009-10-14.
# Copyright 2009 Sean Nelson <audiohacked@gmail.com>
# 
# Overhauled and edited by Garrett Berg on 2011- 1 - 22
# Copyright 2011 Garrett Berg <cloudform511@gmail.com>
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


class I2C(BusPirate):
    """ Provide access to the Bus Pirate I2C interface"""

    SPEEDS = {'400kHz': 0x03,
              '100kHz': 0x02,
              '50kHz' : 0x01,
              '5kHz'  : 0x00}

    pin_mapping = {'AUX': 0b10,
                    'CS': 0b01}

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
        >>> from pyBusPirateLite.I2C import I2C
        >>> i2c = I2C()
        >>> i2c.speed = '400kHz'
        """
        super().__init__(portname, speed, timeout, connect)
        self.i2c_speed = None
        
    def enter(self):
        """ Enter I2C mode

        Once in binary I2C mode, send 0×01 to get the current mode version string. The Bus Pirate responds ‘I2Cx’,
        where x is the raw I2C protocol version (currently 1). Get the version string at any time by sending 0×01 again.
        This command is the same in all binary modes, the current mode can always be determined by sending 0x01.

        Raises
        ------
        BPError
            If I2C mode could not be entered
        """
        if self.mode == 'i2c':
            return
        if self.mode != 'bb':
            super(I2C, self).enter()

        self.write(0x02)
        self.timeout(self.minDelay * 10)
        if self.response(4) == "I2C1":
            self.mode = 'i2c'
            self.bp_port = 0b00         # two bit port
            self.bp_config = 0b0000
            self.recurse_end()
            return
        raise BPError('Could not enter I2C mode')

    @property
    def check_i2c(self):
        """Test if we are still in I2C mode

        Returns
        -------
            True if in I2C mode

        Raises
        ------
            BPError if not in I2C mode

        """
        resp = self.response(20)
        self.write(0x01)
        resp = self.response(20)
        if resp == "I2C1":
            return True
        raise BPError(f'Not in I2C mode, response {resp}.')

    def start(self):
        """ Send an I2C start bit

        Raises
        ------
        ProtocolError
            Did not get expected response
        """
        self.write(0x02)
        if self.response(1) != '\x01':
            raise ProtocolError('Could not send I2C start bit')

    def stop(self):
        """ Send an I2C stop bit

        Raises
        ------
        ProtocolError
            Did not get expected response
        """
        self.write(0x03)
        if self.response(1) != '\x01':
            raise ProtocolError('Could not send I2C stop bit')

    def ack(self):
        """ Send ACK

        Send an I2C ACK bit after reading a byte. Tells a slave device that you will read another byte.

        Raises
        ------
        ProtocolError
            Did not get expected response
        """
        self.write(0x06)
        if self.response(1) != '\x01':
            raise ProtocolError('Could not send ACK')

    def nack(self):
        """ Send NACK

        Send an I2C NACK bit after reading a byte. Tells a slave device that you will stop reading,
        next bit should be an I2C stop bit.

        Raises
        ------
        ProtocolError
            Did not get expected response
        """
        self.write(0x07)
        if self.response(1) != '\x01':
            raise ProtocolError('Could not send NACK')

    def sniffer(self):
        """ Sniff traffic on an I2C bus.

        [/] - Start/stop bit
        \ - escape character precedes a data byte value
        +/- - ACK/NACK
        Sniffed traffic is encoded according to the table above. Data bytes are escaped with the '\' character.
        Send a single byte to exit, Bus Pirate responds 0x01 on exit.
        """
        self.write(0x0f)
        resp = self.response(64)
        return resp

    def transfer(self, txdata):
        """ Bulk I2C write, send 1-16 bytes

        Bulk I2C allows multi-byte writes. The Bus Pirate expects xxxx+1 data bytes. Up to 16 data bytes can be sent at
        once. Note that 0000 indicates 1 byte because there’s no reason to send 0.

        BP replies 0×01 to the bulk I2C command. After each data byte the Bus Pirate returns the ACK (0x00) or
        NACK (0x01) bit from the slave device.

        Parameters
        ----------
        txdata: List of bytes
            Data to send (1-16 bytes)

        Returns
        -------
        status: List of bools
            Returns True(ACK) or False(NACK) for each transmitted byte

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

        resp = self.response(length+1)
        if resp[0] != '\x01':
            raise ValueError("Could not transfer I2C data")

        return resp[1:]

    @property
    def speed(self):
        """ Return current I2C clock speed

        Returns
        -------
        str
            I2C clock speed (5kHz, 50kHz, 100kHz, 400kHz)
        """
        return self.i2c_speed

    @speed.setter
    def speed(self, frequency):
        """ Set I2C speed

        Parameters
        ----------
        frequency : str
            I2C clock speed (5kHz, 50kHz, 100kHz, 400kHz)

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
            raise ProtocolError('Could not set IC2 speed')
        self.i2c_speed = frequency

    def write_then_read(self, numtx, numrx, txdata):
        """ Write then read

        This command internally sends I2C start, writes from 0-4096 bytes, then reads 0-4096 bytes into the Bus Pirates
        internal buffer, ACKing each byte internally until the final byte at which point it sends an NACK stop bit.

        All data for this command can be sent at once, and it will be buffered in the Bus Pirate. The write and read
        operations happen once the completed command has been passed to the Bus Pirate. Any write data is internally
        buffered by the Bus Pirate. At the end of the operation, any read data is returned from the buffer, be aware
        that the write buffer is re-used as the read buffer, as such any write data needs to be re-loaded if the command
        is re-executed.

        Write then read command format
        ------------------------------
        command (1byte)	number of write bytes (2bytes)	number of read bytes (2bytes)	bytes to write (0-4096bytes)
        Return data format
        success/0x01 (1byte)	bytes read from I2C (0-4096bytes)
        First send the write then read command (0x08)
        The next two bytes (High8/Low8) set the number of bytes to write (0 to 4096)
        The next two bytes (h/l) set the number of bytes to read (0 to 4096)
        If the number of bytes to read or write are out of bounds, the Bus Pirate will return 0x00 now
        Next, send the bytes to write. Bytes are buffered in the Bus Pirate, there is no acknowledgment that a byte is
        received.
        The Bus Pirate sends an I2C start bit, then all write bytes are sent at once. If an I2C write is not ACKed by a
        slave device, then the operation will abort and the Bus Pirate will return 0x00 now
        Read starts immediately after the write completes. Bytes are read from I2C into a buffer at max I2C speed
        (no waiting for UART). All read bytes are ACKed, except the last byte which is NACKed, this process is handled
        internally between the Bus Pirate and the I2C device
        At the end of the read process, the Bus Pirate sends an I2C stop
        The Bus Pirate now returns 0x01 to the PC, indicating success
        Finally, the buffered read bytes are returned to the PC
        Except as described above, there is no acknowledgment that a byte is received.

        Example
        -------
        Here's an example of a read from a typical 24AA EEPROM:

        PC------>Bus Pirate

        0x08 - command
        0x00 - Write count, Hi byte
        0x01 - Write count, Lo byte (E.G one byte to write)
        0x01 - Read count, Hi byte
        0x02 - Read count, Lo byte (E.G read 257 bytes (or more, up to the maximum allowable))
        0xA1 - The actual byte stream to write, if any (In this case the I2C read address)
        now wait while the Bus Pirate does it's business

        Bus Pirate----->PC

        0x01 - OK (would be 0x00 if the EEPROM doesn't answer the write with an ACK, in this case we wrote the read address)
        0x?? - read position 0
        ...
        0x?? - read position 256 - the requested number of bytes read from the I2C bus
        """
        self.write(0x08)
        self.write(numtx >> 8 & 0xff)
        self.write(numtx & 0xff)
        self.write(numrx >> 8 & 0xff)
        self.write(numrx & 0xff)
        for data in txdata:
            self.write(data)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError('Error in transmission')

        return self.response(numrx, binary=True)

    def aux(self, cmd):
        """ Provides extended use of AUX pin. Requires one command byte. Bus Pirate acknowledges 0x01.

            +--------+------------+
            |Command | Function   |
            +========+============+
            | 0x00   | AUX/CS low |
            +--------+------------+
            | 0x01   | AUX/CS high|
            +--------+------------+
            | 0x02   | AUX/CS HiZ |
            +--------+------------+
            | 0x03   | AUX read   |
            +--------+------------+
            | 0x10   | use AUX    |
            +--------+------------+
            | 0x20   | use CS     |
            +--------+------------+

            Returns
            -------


        """
        if cmd not in (0x00, 0x01, 0x02, 0x03, 0x10, 0x20):
            raise ProtocolError('Illegal extended AUX command')
        self.write(0x09)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError('Error in extended AUX command')
        self.write(cmd)
        resp = self.response(20, binary=True)

        # firmware ~7.1 responds to the command with text followed by another
        # 0x01 confirmation. this behaivor was not well documented on the wiki
        if resp[-1] != 0x01:
            raise ProtocolError('Error in extended AUX command')
        return resp[:-1].decode('ASCII')

    def configure(self, power=False, pullup=False, aux=False, cs=False):
        """Configure peripherals w=power, x=pullups, y=AUX, z=CS

            Enable (1) and disable (0) Bus Pirate peripherals and pins. Bit w enables the power supplies, bit x toggles
            the on-board pull-up resistors, y sets the state of the auxiliary pin, and z sets the chip select pin.
            Features not present in a specific hardware version are ignored. Bus Pirate responds 0×01 on success.

            Note
            -----
            CS pin always follows the current HiZ pin configuration. AUX is always a normal pin output (0=GND, 1=3.3volts).
        """
        data = 0x40
        if power:
            data |= 0x08
        if pullup:
            data |= 0x04
        if aux:
            data |= 0x02
        if cs:
            data |= 0x01
        self.write(data)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError('Error configuring pins')
