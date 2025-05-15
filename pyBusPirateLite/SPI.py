# Created by Sean Nelson on 2009-10-14.
# Copyright 2009 Sean Nelson <audiohacked@gmail.com>
# 
# Overhauled and edited by Garrett Berg on 2011- 1 - 22
# Copyright 2011 Garrett Berg <cloudform511@gmail.com>
# 
# Updated and made Python3 compatible by Juergen Hasch, 20160501
# Copyright 2016 Juergen Hasch <juergen.hasch@elbonia.de>
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

from typing import Dict, List, Optional

from .base import BPError, BusPirate, ProtocolError


class SPI(BusPirate):
    """ Interface for Bus Pirate's SPI (Serial Peripheral Interface) binary mode. """

    # SPI Speed Constants (value for speed configuration register)
    SPEEDS: Dict[str, int] = {
        '30kHz' : 0b000,
        '125kHz': 0b001,
        '250kHz': 0b010,
        '1MHz'  : 0b011,
        '2MHz'  : 0b100,
        '2.6MHz': 0b101,
        '4MHz'  : 0b110,
        '8MHz'  : 0b111
    }

    # SPI Configuration Flags (for SPI.config property / 0x80 command)
    CFG_SAMPLE: int = 0x01      # Sample time: 0=middle, 1=end
    CFG_CLK_EDGE: int = 0x02    # Clock edge: 0=idle to active, 1=active to idle
    CFG_IDLE: int = 0x04        # Clock polarity (idle state): 0=low, 1=high
    CFG_PUSH_PULL: int = 0x08   # Output type: 0=open drain (HiZ), 1=push-pull (3.3V)

    # Pin Configuration Flags (for SPI.pins property / 0x40 command)
    # These are bitmasks for the lower 4 bits of the config byte.
    PIN_CS: int = 0x01          # Enable/control CS pin (typically active low)
    PIN_AUX: int = 0x02         # Enable/control AUX pin
    PIN_PULLUP: int = 0x04      # Enable on-board pull-up resistors
    PIN_POWER: int = 0x08       # Enable power supplies (VCC & VPU)

    # SPI Command Constants
    _CMD_ENTER_SPI_MODE: int = 0x01
    _CMD_GET_MODE_VERSION: int = 0x01 # Same command, but after entering SPI mode
    _CMD_CONFIGURE_PINS_BASE: int = 0x40 # 0100xxxx (Pins: Pwr,PU,AUX,CS)
    _CMD_CONFIGURE_SPI_BASE: int = 0x80  # 1000xxxx (SPI Cfg: OutType,Idle,Edge,Sample)
    _CMD_BULK_TRANSFER_BASE: int = 0x10  # 0001xxxx (Bulk transfer, xxxx = count-1)
    _CMD_SET_SPEED_BASE: int = 0x60      # 0110xxxx (Set speed, xxxx = from SPEEDS dict)
    
    _CMD_CS_LOW: int = 0x02  # Command to set CS low (active)
    _CMD_CS_HIGH: int = 0x03 # Command to set CS high (inactive)

    _CMD_WRITE_THEN_READ_CS_MANAGED: int = 0x04 # Write-then-read with BP managing CS
    _CMD_WRITE_THEN_READ_NO_CS: int = 0x05    # Write-then-read, user manages CS

    _CMD_SNIFFER_ALL: int = 0x0D       # Sniff all SPI traffic
    _CMD_SNIFFER_CS_LOW: int = 0x0E    # Sniff SPI traffic when CS is low

    _EXPECTED_MODE_VERSION: str = "SPI1"

    _config: Optional[int]
    _speed: Optional[str]
    _cs: Optional[bool] # True if CS is asserted (low), False if de-asserted (high)
    _pins: Optional[int]

    def __init__(self, portname: str = '', speed: int = 115200, timeout: float = 0.1, connect: bool = True):
        """ Provide high-speed access to the Bus Pirate SPI hardware.

        Parameters
        ----------
        portname : str, optional
            Name of comport (e.g., '/dev/ttyUSB0' or 'COM3'). Default empty.
        speed : int, optional
            Serial communication speed. Default is 115200.
        timeout : float, optional
            Timeout in seconds for serial communication. Default is 0.1.
        connect : bool, optional
            Whether to connect to BusPirate immediately. Default is True.

        Example
        -------
        >>> from pyBusPirateLite.SPI import SPI
        >>> spi = SPI()
        >>> spi.pins = SPI.PIN_POWER | SPI.PIN_CS # Enable power and CS pin control
        >>> spi.config = SPI.CFG_PUSH_PULL | SPI.CFG_IDLE # Push-pull, Idle low
        >>> spi.speed = '1MHz'
        >>> spi.cs = True  # Assert CS (set low)
        >>> data = spi.transfer([0x82, 0x00]) # Send 0x82, 0x00 and read 2 bytes
        >>> spi.cs = False # De-assert CS (set high)
        """
        self._config = None
        self._speed = None
        self._cs = None
        self._pins = None
        super().__init__(portname, speed, timeout, connect)

    def check_mode(self, expected_mode: str) -> None:
        """ Check if the Bus Pirate is in the expected operational mode.

        Raises
        ------
        BPError
            If the current mode does not match `expected_mode`.
        """
        if self.mode != expected_mode:
            raise BPError(f"Bus Pirate must be in '{expected_mode}' mode, current mode is '{self.mode}'.")

    def enter(self) -> None:
        """ Enter raw SPI mode.

        Once in raw bitbang mode, sends command `_CMD_ENTER_SPI_MODE` (0x01) to enter raw SPI mode.
        The Bus Pirate responds 'SPIx', where x is the raw SPI protocol version (currently 1).
        Get the version string at any time by sending `_CMD_GET_MODE_VERSION` again.

        Raises
        -------
        BPError
            If already in SPI mode or cannot enter BitBang mode first.
        ProtocolError
            If SPI mode could not be entered or unexpected response.
        """
        if self.mode == 'spi':
            raise BPError("Already in SPI mode.")
        if self.mode != 'bb':
           super().enter() # Ensure BitBang mode

        self.write(self._CMD_ENTER_SPI_MODE)
        response_str = self.response(4) 
        if response_str == self._EXPECTED_MODE_VERSION:
            self.mode = 'spi'
            self.recurse_end()
            return
        raise ProtocolError(f"Could not enter SPI mode. Expected '{self._EXPECTED_MODE_VERSION}', got '{response_str}'.")

    @property
    def modestring(self) -> str:
        """ Return SPI mode version string (e.g., "SPI1")."""
        self.check_mode('spi')
        self.write(self._CMD_GET_MODE_VERSION)
        # self.timeout(self.minDelay * 10) # Sets response timeout, usually not needed for quick commands
        return self.response(4)

    @property
    def pins(self) -> Optional[int]:
        """Get the current peripheral pin configuration state (raw integer value)."""
        return self._pins

    @pins.setter
    def pins(self, cfg: int) -> None:
        """ Configure peripherals (Power, Pull-ups, AUX, CS).

        Sends command `0x40 | (cfg & 0x0F)`.
        The lower 4 bits of `cfg` control Power, Pull-ups, AUX, and CS respectively.
        Use `PIN_*` constants ORed together (e.g., `SPI.PIN_POWER | SPI.PIN_CS`).

        Parameters
        ----------
        cfg: int
            Pin configuration bitmask. Use `SPI.PIN_*` constants.
            Bit 0 (0x01): CS (Chip Select)
            Bit 1 (0x02): AUX (Auxiliary Pin)
            Bit 2 (0x04): Pull-ups
            Bit 3 (0x08): Power

        Raises
        -------
        ProtocolError
            If the Bus Pirate does not acknowledge the command.
        ValueError
            If `cfg` is not a valid 4-bit integer (0-15).
        """
        self.check_mode('spi')
        if not (0 <= cfg <= 0x0F):
            raise ValueError(f"Pins configuration must be a 4-bit value (0-15), got {cfg:#04x}.")
        
        self.write(self._CMD_CONFIGURE_PINS_BASE | cfg)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError(f"Could not set SPI pins configuration to {cfg:#04x}. Bus Pirate did not acknowledge.")
        self._pins = cfg

    @property
    def config(self) -> Optional[int]:
        """Get the current SPI specific configuration (raw integer value)."""
        return self._config

    @config.setter
    def config(self, cfg: int) -> None:
        """ Set SPI specific configuration (output type, clock polarity, edge, sample time).

        Sends command `0x80 | cfg`.
        The lower 4 bits of `cfg` control these SPI parameters.
        Use `CFG_*` constants ORed together (e.g., `SPI.CFG_PUSH_PULL | SPI.CFG_IDLE`).

        Parameters
        ----------
        cfg : int
            SPI configuration bitmask. Use `SPI.CFG_*` constants.
            Bit 0 (0x01): Sample time (CFG_SAMPLE: 0=middle, 1=end)
            Bit 1 (0x02): Clock edge (CFG_CLK_EDGE: 0=idle-to-active, 1=active-to-idle)
            Bit 2 (0x04): Clock polarity (CFG_IDLE: 0=low, 1=high)
            Bit 3 (0x08): Pin output type (CFG_PUSH_PULL: 0=Open-Drain/HiZ, 1=Push-Pull)

        Raises
        -------
        ProtocolError
            If Bus Pirate does not acknowledge the configuration.
        ValueError
            If `cfg` is not a valid 4-bit integer (0-15).
        """
        self.check_mode('spi')
        if not (0 <= cfg <= 0x0F):
            raise ValueError(f"SPI configuration must be a 4-bit value (0-15), got {cfg:#04x}.")

        self.write(self._CMD_CONFIGURE_SPI_BASE | cfg)
        # self.timeout(self.minDelay) # Very short timeout, might be risky. Default should be fine.
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError(f"Could not set SPI configuration to {cfg:#04x}. Bus Pirate did not acknowledge.")
        self._config = cfg

    def transfer(self, txdata: List[int]) -> bytes:
        """ Bulk SPI transfer: send data and simultaneously read data.

        Sends 1-16 bytes from `txdata`. For each byte sent, a byte is read from SPI.
        Command: `0x10 | (length - 1)`.

        Parameters
        ----------
        txdata: List[int]
            List of byte values (0-255) to send. Length must be 1-16.

        Returns
        -------
        bytes
            A bytes object containing the data read from SPI, same length as `txdata`.

        Raises
        -------
        ValueError
            If `txdata` length is invalid or contains non-byte values.
        ProtocolError
            If Bus Pirate fails to acknowledge the transfer command.
        """
        self.check_mode('spi')
        length = len(txdata)
        if not (1 <= length <= 16):
            raise ValueError(f'Data length for SPI transfer must be 1-16 bytes, got {length}.')
        
        command_byte = self._CMD_BULK_TRANSFER_BASE | (length - 1)
        self.write(command_byte)
        
        for i, byte_val in enumerate(txdata):
            if not (0 <= byte_val <= 255):
                raise ValueError(f"Data byte at index {i} is not 0-255: got {byte_val}.")
            self.write(byte_val)
        
        # BP responds 0x01 to acknowledge the command, then `length` bytes read from SPI.
        ack_response = self.response(1, binary=True)
        if ack_response != b'\x01':
            raise ProtocolError(f"Bus Pirate did not acknowledge SPI bulk transfer command. Got: {ack_response.hex()}")
        
        rxdata = self.response(length, binary=True)
        return rxdata

    def write_then_read(self, numtx: int, numrx: int, txdata: List[int], cs_managed_by_bp: bool = True) -> bytes:
        """ Write data then read data in a single SPI operation, with optional CS control by Bus Pirate.

        Command 0x04: CS is enabled by BP before write, disabled after read.
        Command 0x05: CS is not changed by BP; user must manage CS externally.

        Parameters
        ----------
        numtx : int
            Number of bytes to write (0-4096). Should match `len(txdata)`.
        numrx : int
            Number of bytes to read (0-4096).
        txdata : List[int]
            List of byte values (0-255) to write.
        cs_managed_by_bp : bool, optional
            If True (default), Bus Pirate handles CS assertion/de-assertion (uses command 0x04).
            If False, user manages CS (uses command 0x05).

        Returns
        -------
        bytes
            A bytes object containing the `numrx` bytes read from SPI.

        Raises
        -------
        ValueError
            If `numtx`, `numrx` are out of range, or `len(txdata)` mismatch, or data values invalid.
        ProtocolError
            If Bus Pirate indicates an error during the operation.
        """
        self.check_mode('spi')
        if not (0 <= numtx <= 4096):
            raise ValueError(f"Number of bytes to write (numtx) must be 0-4096, got {numtx}.")
        if not (0 <= numrx <= 4096):
            raise ValueError(f"Number of bytes to read (numrx) must be 0-4096, got {numrx}.")
        if len(txdata) != numtx:
            raise ValueError(f"Length of txdata ({len(txdata)}) must match numtx ({numtx}).")

        command = self._CMD_WRITE_THEN_READ_CS_MANAGED if cs_managed_by_bp else self._CMD_WRITE_THEN_READ_NO_CS
        self.write(command)
        
        self.write(numtx >> 8 & 0xFF)  # numtx High byte
        self.write(numtx & 0xFF)       # numtx Low byte
        self.write(numrx >> 8 & 0xFF)  # numrx High byte
        self.write(numrx & 0xFF)       # numrx Low byte
        
        for i, byte_val in enumerate(txdata):
            if not (0 <= byte_val <= 255):
                 raise ValueError(f"Data byte at index {i} in txdata must be 0-255, got {byte_val}.")
            self.write(byte_val)
        
        ack_response = self.response(1, binary=True)
        if ack_response != b'\x01':
            raise ProtocolError(f"SPI Write-then-read command failed. Bus Pirate responded with {ack_response.hex()} instead of 0x01.")

        if numrx > 0:
            return self.response(numrx, binary=True)
        return b''

    @property
    def cs(self) -> Optional[bool]:
        """ Chip Select pin status. True if asserted (active, typically low), False if de-asserted (inactive, high)."""
        return self._cs

    @cs.setter
    def cs(self, active: bool) -> None:
        """ Set Chip Select (CS) pin state.

        Parameters
        ----------
        active: bool
            True to assert CS (typically drives pin low).
            False to de-assert CS (typically drives pin high or HiZ).

        Raises
        -------
        ProtocolError
            If Bus Pirate does not acknowledge the CS change command.
        """
        self.check_mode('spi')
        command = self._CMD_CS_LOW if active else self._CMD_CS_HIGH
        self.write(command)
        if self.response(1, binary=True) != b'\x01':
            action = "assert (low)" if active else "de-assert (high)"
            raise ProtocolError(f"Could not {action} SPI CS pin. Bus Pirate did not acknowledge.")
        self._cs = active

    @property
    def speed(self) -> Optional[str]:
        """ Get the current SPI bus speed setting (string like '1MHz')."""
        return self._speed

    @speed.setter
    def speed(self, frequency: str) -> None:
        """ Set SPI bus speed.

        Parameters
        ----------
        frequency : str
            SPI clock speed. Must be one of the keys in `SPI.SPEEDS` 
            (e.g., '30kHz', '1MHz', '8MHz').

        Raises
        -------
        ValueError
            If `frequency` string is not a supported speed.
        ProtocolError
            If Bus Pirate does not acknowledge the speed change command.
        """
        self.check_mode('spi')
        try:
            clock_val = self.SPEEDS[frequency]
        except KeyError:
            raise ValueError(f'SPI clock speed "{frequency}" not supported. Valid speeds: {list(self.SPEEDS.keys())}')
        
        self.write(self._CMD_SET_SPEED_BASE | clock_val)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError(f'Could not set SPI speed to "{frequency}". Bus Pirate did not acknowledge.')
        self._speed = frequency

    def sniffer(self, sniff_on_cs_low: bool = True) -> None:
        """ Start the SPI traffic sniffer.

        The sniffer uses current SPI configuration (polarity, edge, sample time).
        It can filter by CS pin state or capture all traffic.
        
        Note: This method only sends the command to start sniffing.
              The Bus Pirate will then stream data. Handling this data stream and 
              sending a byte to stop sniffing requires further implementation outside this method.

        Parameters
        ----------
        sniff_on_cs_low : bool, optional
            True (default): Capture traffic only when CS is low (active).
            False: Capture all SPI traffic regardless of CS state.

        Raises
        -------
        ProtocolError
            If Bus Pirate does not acknowledge the sniffer command.
        """
        self.check_mode('spi')
        command = self._CMD_SNIFFER_CS_LOW if sniff_on_cs_low else self._CMD_SNIFFER_ALL
        self.write(command)
        if self.response(1, binary=True) != b'\x01':
            mode = "CS low" if sniff_on_cs_low else "all traffic"
            raise ProtocolError(f"Could not start SPI sniffer for '{mode}'. Bus Pirate did not acknowledge.")
        # Sniffing starts now. Further interaction (reading data, stopping) is not handled here.
