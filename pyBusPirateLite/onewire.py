# Created by Sean Nelson on 2009-10-20.
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

"""
Provides an interface to the Bus Pirate's 1-Wire binary mode.

Binary 1-Wire Mode Commands (sent to Bus Pirate):
- 0x00 (RESET_TO_BBIO): Resets Bus Pirate to BitBang I/O mode.
- 0x01 (MODE_VERSION): Get mode version string (responds "1W01").
- 0x02 (ONEWIRE_RESET): Perform a 1-Wire bus reset. Responds 0x01 if presence pulse detected, 0x00 otherwise.
- 0x04 (READ_BYTE): Read a byte from the 1-Wire bus.
- 0x08 (ROM_SEARCH_MACRO): Execute ROM search macro (0xF0 command).
- 0x09 (ALARM_SEARCH_MACRO): Execute ALARM search macro (0xEC command).
- 0x1x (BULK_TRANSFER): Bulk transfer, send 1-16 bytes. xxxx = (num_bytes - 1).
- 0x4x (CONFIGURE_PERIPHERALS): Configure peripherals (power, pull-ups, AUX, CS).
                        w=power, x=pull-ups, y=AUX, z=CS.
- 0x5x (READ_PERIPHERALS): Read peripheral status (planned, not implemented by BP firmware at time of writing).
"""

from typing import Optional, List, Union

from .base import BusPirate, ProtocolError, BPError


class OneWire(BusPirate):
    """ Interface for Bus Pirate's 1-Wire binary communication mode. """

    # 1-Wire Command Constants
    _CMD_ENTER_1WIRE_MODE: int = 0x04
    _CMD_GET_MODE_VERSION: int = 0x01
    _CMD_RESET: int = 0x02
    _CMD_READ_BYTE_CMD: int = 0x04
    _CMD_ROM_SEARCH: int = 0x08
    _CMD_ALARM_SEARCH: int = 0x09

    _EXPECTED_MODE_VERSION: str = "1W01"

    def __init__(self, portname: str = '', speed: int = 115200, timeout: float = 0.1, connect: bool = True):
        """Provide access to the Bus Pirate Onewire protocol.

        Parameters
        ----------
        portname : str, optional
            Name of the serial port (e.g., '/dev/ttyUSB0' or 'COM3'). Default is empty.
        speed : int, optional
            Serial communication speed. Default is 115200.
        timeout : float, optional
            Timeout in seconds for serial communication. Default is 0.1.
        connect : bool, optional
            Whether to connect to the Bus Pirate immediately. Default is True.

        Example
        -------
        >>> from pyBusPirateLite.onewire import OneWire
        >>> ow = OneWire() # Connects to the first Bus Pirate found
        """
        super().__init__(portname, speed, timeout, connect)

    def enter_1wire(self) -> bool:
        """Enters 1-Wire binary mode on the Bus Pirate.

        Attempts to switch the Bus Pirate from BitBang mode to 1-Wire mode.

        Returns
        -------
        bool
            True if 1-Wire mode was entered successfully, False otherwise.

        Raises
        -------
        BPError
            If already in 1-Wire mode or cannot enter BitBang mode first.
        ProtocolError
            If an unexpected response is received from the Bus Pirate.
        """
        if self.mode == '1wire':
            raise BPError("Already in 1-Wire mode.") 
        
        if self.mode != 'bb':
            super().enter()

        self.write(self._CMD_ENTER_1WIRE_MODE)
        response_str = self.response(4)
        if response_str == self._EXPECTED_MODE_VERSION:
            self.mode = '1wire'
            self.recurse_end()
            return True
        raise ProtocolError(f"Failed to enter 1-Wire mode. Expected '{self._EXPECTED_MODE_VERSION}', got '{response_str}'")

    def reset(self) -> bool:
        """Performs a 1-Wire bus reset.

        Sends the 1-Wire reset command to the Bus Pirate.

        Returns
        -------
        bool
            True if a presence pulse was detected from a 1-Wire device, False otherwise.
            The Bus Pirate responds with b'\x01' for presence, b'\x00' for no presence.

        Raises
        -------
        ProtocolError
            If not in 1-Wire mode or if an unexpected response is received.
        """
        self.check_mode('1wire')
        self.write(self._CMD_RESET)
        response_byte = self.response(1, binary=True)
        if response_byte == b'\x01':
            return True
        elif response_byte == b'\x00':
            return False
        raise ProtocolError(f"Unexpected response after 1-Wire reset: {response_byte.hex()}. Expected b'01' or b'00'.")

    def rom_search(self) -> List[bytes]:
        """Executes the 1-Wire ROM search command (0xF0).

        This method initiates the ROM search sequence on the Bus Pirate and 
        processes the response to find 1-Wire device ROM IDs.
        Note: This is a simplified version that prints found data.
              A production version should parse and return the ROM IDs.

        Returns
        -------
        List[bytes]
            A list of found ROM IDs, each as an 8-byte `bytes` object.
            (Currently prints and returns, for full functionality, parsing is needed).

        Raises
        -------
        ProtocolError
            If not in 1-Wire mode.
        """
        self.check_mode('1wire')
        self.write(self._CMD_ROM_SEARCH)
        return self.__group_response()

    def alarm_search(self) -> List[bytes]:
        """Executes the 1-Wire ALARM search command (0xEC).

        This method initiates the ALARM search sequence on the Bus Pirate.
        Useful for finding devices that have their alarm flag set.
        Note: This is a simplified version that prints found data.

        Returns
        -------
        List[bytes]
            A list of found ROM IDs (devices in alarm state), each as an 8-byte `bytes` object.
            (Currently prints and returns, for full functionality, parsing is needed).

        Raises
        -------
        ProtocolError
            If not in 1-Wire mode.
        """
        self.check_mode('1wire')
        self.write(self._CMD_ALARM_SEARCH)
        return self.__group_response()

    def __group_response(self) -> List[bytes]:
        """Helper method to read and process grouped responses from ROM/Alarm search.

        The Bus Pirate sends data in 8-byte chunks for each device found.
        It indicates the end of data with a sequence of 0xFF bytes (typically 8 of them).
        This method reads these chunks until the End-Of-Data marker is detected.

        Returns
        -------
        List[bytes]
            A list of 8-byte device ROM IDs found during the search.

        Raises
        -------
        IOError (OSError)
            If an excessive number of End-Of-Data markers are received, 
            suggesting a communication issue.
        ProtocolError
            If not in 1-Wire mode.
        """
        self.check_mode('1wire')
        
        found_roms: List[bytes] = []
        eod_marker_byte: int = 0xFF
        eod_chunk: bytes = bytes([eod_marker_byte] * 8)
        
        eod_consecutive_chunks = 0

        for _ in range(256):
            data_chunk: bytes = self.port.read(8)
            
            if not data_chunk:
                break

            if data_chunk == eod_chunk:
                eod_consecutive_chunks += 1
                break 
            else:
                print(f"Found 1-Wire device data: {data_chunk.hex()}")
                found_roms.append(data_chunk)
                eod_consecutive_chunks = 0
        
        if eod_consecutive_chunks == 0 and not found_roms:
            print("No 1-Wire devices found or EOD marker not detected clearly.")
            
        return found_roms

    def read_byte(self) -> int:
        """Reads a single byte from the 1-Wire bus.

        The Bus Pirate handles the low-level 1-Wire read timing.

        Returns
        -------
        int
            The byte value read from the bus.

        Raises
        -------
        ProtocolError
            If not in 1-Wire mode or if an unexpected response is received.
        """
        self.check_mode('1wire')
        self.write(self._CMD_READ_BYTE_CMD)
        response_byte = self.response(1, binary=True)
        if not response_byte:
            raise ProtocolError("No response from Bus Pirate after 1-Wire read_byte command.")
        return response_byte[0]
