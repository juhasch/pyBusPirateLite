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

from time import sleep
from typing import Optional, Union, List, Tuple # Added for type hints

import serial
import serial.tools.list_ports as list_ports # Moved import


class BPError(IOError):
    pass


class ProtocolError(IOError):
    pass


class BusPirate:
    """Base class for all modes. This contains low-level functions for direct
    hardware access.

    Note: This class also contains some of the older functions that are now
    probably outdated
    """

    """
    PICSPEED = 24MHZ / 16MIPS
    """
    # 0x01 CS
    # 0x08 - +3.3V

    PIN_CS: int = 0x01
    PIN_MISO: int = 0x02
    PIN_CLK: int = 0x04
    PIN_MOSI: int = 0x08
    PIN_AUX: int = 0x10
    PIN_PULLUP: int = 0x20
    PIN_POWER: int = 0x40

    def __init__(self, portname: str = '', speed: int = 115200, timeout: float = 0.1, connect: bool = True):
        """
        This constructor by default connects to the first buspirate it can
        find. If you don't want that, set connect to False.

        Parameters
        ----------
        portname : str
            Name of comport (e.g., /dev/bus_pirate or COM3).
            If empty, will attempt to autodetect.
        speed : int
            Communication speed, default is 115200.
        timeout : float
            Timeout in seconds to wait for reply.
        connect : bool
            If True, automatically connect and enter bitbang mode.
        """

        self.minDelay: float = 1 / 115200
        self.mode: Optional[str] = None
        self.port: Optional[serial.Serial] = None
        self.connected: bool = False
        self.t: bool = True  # TODO: What is self.t for? Consider a more descriptive name.
        self.bp_config: Optional[int] = None
        self.bp_port: Optional[int] = None
        self.bp_dir: Optional[int] = None
        self.portname: str = ''
        self.pins_state: Optional[int] = None # Assuming int, based on PIN_ constants
        self.pins_direction: Optional[int] = None # Assuming int

        if connect:
            self.connect(portname, speed, timeout)
            self.enter()

    _attempts_: int = 0  # global stored for use in enter # TODO: Consider if this class attribute is appropriate, or if it should be an instance attribute or handled differently.

    @property
    def adc_value(self) -> float:
        """ Read and return the voltage on the analog input pin. """
        # raise error to prevent tab-completion having side-effects
        if self.mode != 'bb':
            raise TypeError("Action only valid in bitbang mode")
        if self.port is None:
            raise BPError("Serial port not initialized.")
        self.write(0x14)
        val = int.from_bytes(self.response(2, binary=True), 'big')
        # see
        # http://dangerousprototypes.com/blog/2009/10/09/bus-pirate-raw-bitbang-mode/
        # for conversion formula.
        return (val / 1024.0) * 3.3 * 2

    def set_power_on(self, val: bool) -> None:
        if self.port is None:
            raise BPError("Serial port not initialized.")
        self.write(0x80 | (self.PIN_POWER if val else 0))
        self.response(1, binary=True)

    power_on = property(fset=set_power_on, doc="""
        Enable or disable the built-in power supplies.
        Note that the power supplies reset every time you change modes.
        This is a write-only property. The Bus Pirate firmware does not
        provide a command to read the current power supply state.
        """)

    def enter_bb(self) -> bool:
        """Enter bitbang mode.

        This is the primary restart function. It attempts to get the Bus Pirate
        into bitbang mode, even if it's in an unknown state. Call this
        to ensure the Bus Pirate is in a known state (bitbang mode).

        This command resets the Bus Pirate into raw bitbang mode from the user
        terminal, raw SPI mode, or any other protocol mode. It expects a five
        byte bitbang version string "BBIOx" in response, where x is the
        protocol version (currently 1 for "BBIO1").

        Some terminals send a NULL character (0x00) on start-up. To ensure entry
        into raw bitbang mode, this method sends 0x00 multiple times.

        Raises
        ------
        IOError
            If the device is not connected.
        BPError
            If bitbang mode could not be entered.
        """
        if not self.connected or self.port is None:
            raise IOError('Device not connected')

        # Ensure port timeout is appropriate. self._original_timeout (e.g. 0.1s) is used for reads.
        self.port.timeout = self._original_timeout 
        self.port.flushInput()

        # Send a burst of null bytes to enter bitbang mode
        for _ in range(25): 
            self.write(0x00) 
            sleep(0.0001) # 100µs delay between bytes

        # After sending nulls, give a moment for BP to switch state and send "BBIO1"
        sleep(0.05) # 50ms delay

        resp = self.port.read(5) # Attempt to read "BBIO1"

        if resp == b"BBIO1":
            self.mode = 'bb'
            self.bp_config = 0x00  # configuration bits
            self.bp_port = 0x00    # output port state
            self.bp_dir = 0x1F     # port direction (1=input, 0=output)
            self.port.flushInput() # Clear any lingering data after successful entry
            return True
        
        # If first attempt failed, try one more robust clear and read sequence.
        self.port.flushInput()
        for _ in range(5): # Send a few more nulls
            self.write(0x00)
            sleep(0.0001)
        sleep(0.05) # Another 50ms delay
        resp = self.port.read(5)

        if resp == b"BBIO1":
            self.mode = 'bb'
            self.bp_config = 0x00
            self.bp_port = 0x00
            self.bp_dir = 0x1F
            self.port.flushInput()
            return True

        raise BPError(f'Could not enter bitbang mode. Expected "BBIO1", got "{resp!r}"')

    def enter(self) -> None:
        """Enter bitbang mode.
           This method is intended to be overridden by subclasses for specific
           protocol modes. The base implementation ensures bitbang mode.
        """
        if self.mode == 'bb':
            return
        self.enter_bb()

    def hw_reset(self) -> None:
        """Reset Bus Pirate hardware.

        Sends the hardware reset command (0x0F). The Bus Pirate responds 0x01,
        performs a complete hardware reset, prints its hardware and firmware
        version (like the 'i' command), and returns to the user terminal interface.
        After this, send 0x00 multiple times to re-enter binary (bitbang) mode.
        """
        if self.mode != 'bb':
            self.enter_bb() # Ensure we are in bitbang to send command
        if self.port is None:
            raise BPError("Serial port not initialized.")

        self.write(0x0f)
        # BP responds 0x01 then resets. No need to read the 0x01.
        self.port.flushInput() # Flush input as BP will spew version info
        sleep(0.1) # Give BP time to reset
        self.mode = None # BP is no longer in a known binary mode
        self.connected = False # Effectively disconnected from a binary mode perspective
                               # User will need to self.connect() and self.enter() again.
                               # Or at least self.enter() to get back to bb.

    def get_port(self) -> Optional[str]:
        """Detect Bus Pirate and return the device path of the first one found.

        Returns
        -------
        str or None
            Device path (e.g., /dev/ttyUSB0, COM3) if found, otherwise None.
        """
        ports = list_ports.comports()
        for port_info in ports:
            # Standard FTDI VID/PID for Bus Pirate
            if port_info.vid == 0x0403 and port_info.pid == 0x6001:
                return port_info.device
        return None

    def connect(self, portname: str = '', speed: int = 115200, timeout: float = 0.1) -> None:
        """Connect to the Bus Pirate.

        Attempts to automatically find a Bus Pirate if portname is not specified.

        Parameters
        ----------
        portname : str
            Device path (e.g., /dev/ttyUSB0 or COM3). If empty, autodetects.
        speed : int
            Serial communication speed (baud rate).
        timeout : float
            Serial read timeout in seconds.

        Raises
        ------
        IOError
            If a Bus Pirate device cannot be found or the port cannot be opened.
        """
        actual_portname = portname
        if not actual_portname:
            detected_port = self.get_port()
            if detected_port:
                actual_portname = detected_port
            else:
                raise IOError('Could not autodetect a BusPirate device. Please specify portname.')

        self.portname = actual_portname
        self._original_timeout = timeout # Store for restoring in enter_bb
        try:
            self.port = serial.Serial(self.portname, speed, timeout=timeout)
        except serial.serialutil.SerialException as e:
            raise IOError(f'Could not open port {self.portname}: {e}')

        self.connected = True
        self.minDelay = 1.0 / speed  # Ensure float division

    def disconnect(self) -> None:
        """ Disconnects from the Bus Pirate and closes the COM port. """
        if self.port and self.port.is_open:
            self.port.close()
        self.connected = False
        self.port = None

    def __enter__(self):
        # Allow using BusPirate with 'with' statement
        return self

    def __exit__(self, exc_type: Optional[type] = None, exc_val: Optional[Exception] = None, exc_tb: Optional[object] = None) -> None:
        """Ensures disconnection when exiting a 'with' statement context."""
        self.disconnect()

    def pause(self, duration: float = 0.1) -> None:
        """Pause execution for a specified duration.

        Parameters
        ----------
        duration : float
            Time to pause in seconds.
        """
        sleep(duration)

    def write(self, value: int) -> None:
        """Write a single byte to the Bus Pirate.

        Parameters
        ----------
        value : int
            The byte value (0-255) to write.
        """
        if self.port is None:
            raise BPError("Serial port not initialized.")
        if not (0 <= value <= 255):
            raise ValueError("Value must be a valid byte (0-255).")
        self.port.write(value.to_bytes(1, 'big'))

    def response(self, byte_count: int = 1, binary: bool = False) -> Union[bytes, str]:
        """Request a number of bytes from the Bus Pirate.

        Parameters
        ----------
        byte_count : int
            Number of bytes to read.
        binary : bool
            If True, return raw bytes. If False (default), decode as UTF-8 string.

        Returns
        -------
        bytes or str
            The data read from the Bus Pirate.
        """
        if self.port is None:
            raise BPError("Serial port not initialized.")
        data: bytes = self.port.read(byte_count)
        if binary:
            return data
        else:
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                # If UTF-8 fails, return as repr for safety, or raise error
                # This indicates non-textual data when binary=False was used.
                # Consider logging this case.
                return repr(data) # Or raise an error if strict UTF-8 is expected

    def recurse_end(self) -> None:
        self._attempts_ = 0

    def recurse(self, func, *args):
        # TODO: Add type hint for func: Callable[..., Any]
        if self._attempts_ < 15:
            self._attempts_ += 1
            return func(*args)
        self.recurse_end() # Reset attempts after failing
        raise BPError('Bus Pirate malfunctioning or unresponsive after multiple retries.')

    def recurse_flush(self, func, *args):
        # TODO: Add type hint for func: Callable[..., Any]
        if self._attempts_ < 15:
            self._attempts_ += 1
            if self.port is None:
                raise BPError("Serial port not initialized for recurse_flush.")
            # The purpose of writing 0x00 five times and flushing is likely
            # to clear any Bus Pirate internal state or buffers before retrying.
            for _n in range(5):
                self.write(0x00)
                self.port.flushInput() # flushInput, not flush()
            return func(*args)
        self.recurse_end() # Reset attempts after failing
        raise BPError('Bus Pirate malfunctioning or unresponsive after multiple flush retries.')

    # General Commands for Higher-Level Modes.
    # Note: Some of these do not have error checking implemented beyond retries
    # (they might return 0 or 1 from the BP). You may need to do your own
    # device-specific error checking. This is as planned, since behavior often
    # depends on the device you are interfacing with.

    def send_start_bit(self) -> int:
        """Sends a start bit command (0x02) to the Bus Pirate.

        Used in modes like I2C. Retries on failure.

        Returns
        -------
        int
            1 if the Bus Pirate acknowledged the command, otherwise raises BPError after retries.
        """
        if self.port is None: raise BPError("Serial port not initialized.")
        self.write(0x02)
        # self.response(1, True) # Original code had this, but BP 0x02 command doesn't send a byte back before the status byte
        if self.response(1, binary=True) == b'\x01':
            self.recurse_end()
            return 1
        return self.recurse(self.send_start_bit)

    def send_stop_bit(self) -> int:
        """Sends a stop bit command (0x03) to the Bus Pirate.

        Used in modes like I2C. Retries on failure.

        Returns
        -------
        int
            1 if the Bus Pirate acknowledged the command, otherwise raises BPError after retries.
        """
        if self.port is None: raise BPError("Serial port not initialized.")
        self.write(0x03)
        if self.response(1, binary=True) == b'\x01':
            self.recurse_end()
            return 1
        return self.recurse(self.send_stop_bit)

    def read_byte(self) -> bytes:
        """Reads a byte from the bus.

        In 'raw' mode, sends command 0x06. Otherwise, sends 0x04.
        You must ACK or NACK each byte manually in relevant modes (e.g., I2C).

        Returns
        -------
        bytes
            The byte read from the bus.
        """
        if self.port is None: raise BPError("Serial port not initialized.")
        if self.mode == 'raw': # Assuming 'raw' refers to rawwire mode
            self.write(0x06)
        else:
            self.write(0x04)
        return self.response(1, binary=True)

    def bulk_trans(self, byte_count: int, byte_list: List[int]) -> bytes:
        """Performs a bulk transaction: writes multiple bytes and reads responses.

        Command: 0x10 | (count - 1)
        Sends each byte from byte_list, then reads (count) bytes back from the BP.
        The BP typically echos the byte sent or provides an ACK/NACK status.

        Parameters
        ----------
        byte_count : int
            The number of bytes to transfer (1-16).
        byte_list : List[int]
            A list of byte values (0-255) to send.

        Returns
        -------
        bytes
            The (byte_count) bytes returned by the Bus Pirate after transmission.
            The first byte of BP response (before these data bytes) is checked for ACK.

        Raises
        -------
        ValueError
            If byte_count is not between 1 and 16, or if len(byte_list) != byte_count.
        BPError
            If the Bus Pirate does not acknowledge the bulk transfer command or on other errors.
        """
        if self.port is None: raise BPError("Serial port not initialized.")
        if not (1 <= byte_count <= 16):
            raise ValueError("byte_count must be between 1 and 16.")
        if len(byte_list) != byte_count:
            raise ValueError(f"Length of byte_list ({len(byte_list)}) must match byte_count ({byte_count}).")

        self.write(0x10 | (byte_count - 1))
        # BP responds with 0x01 (ACK) if command is OK
        ack = self.response(1, binary=True)
        if ack != b'\x01':
            # If not ACK, attempt retry via recurse. The function itself will handle the command byte again.
            return self.recurse(self.bulk_trans, byte_count, byte_list)

        # Send the actual bytes
        for byte_val in byte_list:
            if not (0 <= byte_val <= 255):
                raise ValueError("All values in byte_list must be valid bytes (0-255).")
            self.write(byte_val) # This write is for each data byte in the bulk transfer

        # Read the Bus Pirate's response for each byte sent
        # BP returns one byte for each byte it was asked to send in the bulk command
        data_returned: bytes = self.response(byte_count, binary=True)
        self.recurse_end() # Successful transaction
        return data_returned
