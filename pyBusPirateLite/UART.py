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

from typing import Dict, Optional

from .base import BPError, BusPirate, ProtocolError


class UARTSpeed:
    """ Encapsulates the register values for predefined UART speeds. """
    S_300 = 0b0000
    S_1200 = 0b0001
    S_2400 = 0b0010
    S_4800 = 0b0011
    S_9600 = 0b0100
    S_19200 = 0b0101
    S_31250 = 0b0110 # Corrected from 33250 to 31250 as per some BP docs for MIDI etc.
    S_38400 = 0b0111
    S_57600 = 0b1000
    S_115200 = 0b1001
    # S_230400 = 0b1010 # some firmwares might support more speeds
    # S_250000 = 0b1011


class UART(BusPirate):
    """ Interface for Bus Pirate's UART (Universal Asynchronous Receiver/Transmitter) binary mode. """

    _FOSC: float = (32000000 / 2.0)  # Oscillator frequency divided by 2

    # UART Command Constants
    _CMD_ENTER_UART_MODE: int = 0x03
    _CMD_GET_MODE_VERSION: int = 0x01
    _CMD_RX_ECHO_OFF: int = 0x02
    _CMD_RX_ECHO_ON: int = 0x03 # Context-dependent: used when already in UART mode
    _CMD_SET_RAW_BRG: int = 0x07
    _CMD_ENABLE_RX: int = 0x04        # Also referred to as "manual RX enable" or "bulk RX enable"
    _CMD_DISABLE_RX: int = 0x05       # Also "manual RX disable" or "bulk RX disable"
    _CMD_UART_BRIDGE_MODE: int = 0x0F
    
    _CMD_SET_PREDEFINED_SPEED_BASE: int = 0x60  # 0110xxxx (Set speed, xxxx from UARTSpeed)
    _CMD_CONFIGURE_UART_BASE: int = 0x80      # 1000wxyz (Config: PinOut,Data/Parity,Stop,RX Pol)
    _CMD_SET_PERIPHERALS_BASE: int = 0x40     # 0100wxyz (Config: Pwr,PU,AUX,CS - CS N/A for UART)

    # Custom/Legacy register commands - use with caution
    _CMD_SET_CUSTOM_REGISTER_BASE: int = 0xC0 # 1100xxxx 
    _CMD_READ_CUSTOM_REGISTER: int = 0xD0     # 11010000

    _EXPECTED_MODE_VERSION: str = "ART1"

    # Baud rate string to UARTSpeed value mapping
    SPEEDS_MAP: Dict[str, int] = {
        "300bps": UARTSpeed.S_300,
        "1200bps": UARTSpeed.S_1200,
        "2400bps": UARTSpeed.S_2400,
        "4800bps": UARTSpeed.S_4800,
        "9600bps": UARTSpeed.S_9600,
        "19200bps": UARTSpeed.S_19200,
        "31250bps": UARTSpeed.S_31250,
        "38400bps": UARTSpeed.S_38400,
        "57600bps": UARTSpeed.S_57600,
        "115200bps": UARTSpeed.S_115200,
    }
    
    # Data bits and parity settings for configure_protocol's data_parity_setting parameter
    DATA_PARITY_8N: int = 0b00 # 8 data bits, no parity
    DATA_PARITY_8E: int = 0b01 # 8 data bits, even parity
    DATA_PARITY_8O: int = 0b10 # 8 data bits, odd parity
    DATA_PARITY_9N: int = 0b11 # 9 data bits, no parity


    _echo: bool
    _predefined_speed_key: Optional[str]
    _uart_protocol_config: Optional[int] # Stores the byte sent to 0x80 command
    _peripheral_config: Optional[int]    # Stores the byte sent to 0x40 command
    _custom_register_value: Optional[int]# Stores the value set by _set_custom_register

    def __init__(self, portname: str = '', speed: int = 115200, timeout: float = 0.1, connect: bool = True):
        """ Provide access to the Bus Pirate UART interface.

        Parameters
        ----------
        portname : str, optional
            Name of comport (e.g., '/dev/ttyUSB0' or 'COM3'). Default empty.
        speed : int, optional
            Serial communication speed for the FTDI chip. Default is 115200.
        timeout : float, optional
            Timeout in seconds for serial communication. Default is 0.1.
        connect : bool, optional
            Whether to connect to BusPirate immediately. Default is True.

        Example
        -------
        >>> from pyBusPirateLite.UART import UART
        >>> uart = UART('/dev/ttyUSB0')
        >>> if uart.enter():
        ...     uart.speed = "9600bps"
        ...     uart.configure_protocol(output_3v3=True, 
        ...                             data_parity_setting=UART.DATA_PARITY_8N, 
        ...                             stop_1bit=True, 
        ...                             rx_idle_high=True)
        ...     uart.echo = False
        ...     # uart operations ...
        """
        self._echo = False
        self._predefined_speed_key = None
        self._uart_protocol_config = None
        self._peripheral_config = None
        self._custom_register_value = None
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
        """ Enter UART mode.

        Sends command `_CMD_ENTER_UART_MODE` (0x03) to enter raw UART mode
        if not already in UART mode. Requires BitBang mode to be active first.
        The Bus Pirate responds 'ARTx', where x is the raw UART protocol version.

        Raises
        -------
        BPError
            If already in UART mode or cannot enter BitBang mode first.
        ProtocolError
            If UART mode could not be entered or unexpected response.
        """
        if self.mode == 'uart':
            # raise BPError("Already in UART mode.") # Or just return silently
            return
        if self.mode != 'bb':
           super().enter() # Ensure BitBang mode

        self.write(self._CMD_ENTER_UART_MODE)
        # self.timeout(self.minDelay * 10) # May not be needed, default timeout should apply
        response_str = self.response(4) 
        if response_str == self._EXPECTED_MODE_VERSION:
            self.mode = 'uart'
            self.recurse_end() # Finalize mode entry
            return
        # self.recurse_flush(self.enter) # Old error recovery, prefer direct error
        raise ProtocolError(f"Could not enter UART mode. Expected '{self._EXPECTED_MODE_VERSION}', got '{response_str}'.")

    @property
    def modestring(self) -> str:
        """ Return UART mode version string (e.g., "ART1")."""
        self.check_mode('uart')
        self.write(self._CMD_GET_MODE_VERSION)
        return self.response(4)

    @property
    def echo(self) -> bool:
        """ Get the current RX echo status (True if enabled, False if disabled)."""
        self.check_mode('uart')
        return self._echo

    @echo.setter
    def echo(self, mode: bool) -> None:
        """ Set RX echo mode. 
        
        If True, received UART data is echoed back by the Bus Pirate.
        If False, echo is disabled.
        """
        self.check_mode('uart')
        command = self._CMD_RX_ECHO_ON if mode else self._CMD_RX_ECHO_OFF
        self.write(command)
        if self.response(1, binary=True) != b'\x01':
            action = "enable" if mode else "disable"
            raise ProtocolError(f"Could not {action} UART RX echo. Bus Pirate did not acknowledge.")
        self._echo = mode

    @property
    def speed(self) -> Optional[str]:
        """Get the current predefined UART bus speed setting (e.g., "9600bps").
        Returns None if speed was set manually or not yet set via this property.
        """
        self.check_mode('uart')
        return self._predefined_speed_key

    @speed.setter
    def speed(self, speed_key: str) -> None:
        """ Set UART bus speed using predefined values.

        Parameters
        ----------
        speed_key : str
            UART clock speed. Must be one of the keys in `UART.SPEEDS_MAP` 
            (e.g., '9600bps', '115200bps').

        Raises
        -------
        ValueError
            If `speed_key` string is not a supported speed.
        ProtocolError
            If Bus Pirate does not acknowledge the speed change command.
        """
        self.check_mode('uart')
        if speed_key not in self.SPEEDS_MAP:
            raise ValueError(f'UART speed "{speed_key}" not supported. Valid speeds: {list(self.SPEEDS_MAP.keys())}')
        
        speed_val = self.SPEEDS_MAP[speed_key]
        self.write(self._CMD_SET_PREDEFINED_SPEED_BASE | speed_val)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError(f'Could not set UART speed to "{speed_key}". Bus Pirate did not acknowledge.')
        self._predefined_speed_key = speed_key
        # Invalidate raw speed if one was set? Or assume this overrides it.

    def set_baudrate_raw(self, baudrate: int) -> None:
        """ Manual baud rate configuration using BRG calculation.

        Configures the UART using custom baud rate generator settings.
        Sends command `_CMD_SET_RAW_BRG` (0x07) followed by two data bytes (BRGH, BRGL)
        that represent the BRG register value.
        The Bus Pirate responds with a single 0x01 on success after all three bytes are sent.

        Parameters
        ----------
        baudrate: int
            The desired baud rate (e.g., 9600, 115200).

        Raises
        -------
        ValueError
            If baudrate is out of a reasonable range.
        ProtocolError
            If Bus Pirate does not acknowledge the command.
        """
        self.check_mode('uart')
        if not (0 < baudrate <= self._FOSC / 4): # Theoretical max, practical is lower
             raise ValueError(f"Baud rate {baudrate} is out of a practical range.")

        brg_val_float = (self._FOSC / (4 * baudrate)) - 1
        brg_val_int = int(round(brg_val_float)) # Round to nearest integer for BRG

        if not (0 <= brg_val_int <= 0xFFFF):
            raise ValueError(f"Calculated BRG value {brg_val_int} for baudrate {baudrate} is out of 16-bit range.")

        brgh = (brg_val_int >> 8) & 0xFF
        brgl = brg_val_int & 0xFF
        
        self.write(self._CMD_SET_RAW_BRG)
        self.write(brgh)
        self.write(brgl)
        
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError(f"Could not set raw baud rate to {baudrate} (BRG: {brgh:02X}{brgl:02X}). Bus Pirate did not acknowledge.")
        self._predefined_speed_key = None # Raw speed overrides predefined

    def configure_protocol(self, output_3v3: bool, data_parity_setting: int, 
                           stop_1bit: bool, rx_idle_high: bool) -> None:
        """ Configure UART protocol parameters: pin output, data/parity, stop bits, RX polarity.

        Uses command `_CMD_CONFIGURE_UART_BASE` (0x80).
        Bit 3: Pin output (0=Open Drain/HiZ, 1=Push-Pull 3.3V)
        Bits 2-1: Data bits & Parity (00=8N, 01=8E, 10=8O, 11=9N) - Use UART.DATA_PARITY_* constants.
        Bit 0: Stop bits (0=1 stop bit, 1=2 stop bits)
        RX Polarity (Idle State): (0=RX Idle Low (inverted), 1=RX Idle High (standard))
        
        Note: The command structure for RX polarity bit within 0x80 might vary slightly with firmware.
        This implementation assumes RX polarity is the LSB of a different config byte for some BPs,
        but the common BBIO UART spec puts it in the 0x80 command.
        For simplicity, this method controls the main 0x80 configuration bits.
        The `rx_idle_high` affects the interpretation of UART signals.

        Parameters
        ----------
        output_3v3 : bool
            True for push-pull 3.3V output, False for open-drain (HiZ).
        data_parity_setting : int
            One of `UART.DATA_PARITY_8N`, `UART.DATA_PARITY_8E`, `UART.DATA_PARITY_8O`, `UART.DATA_PARITY_9N`.
        stop_1bit : bool
            True for 1 stop bit, False for 2 stop bits.
        rx_idle_high : bool 
            True if RX line is idle high (standard), False if idle low (inverted). This sets the UART RX polarity bit.

        Raises
        ------
        ValueError
            If `data_parity_setting` is invalid.
        ProtocolError
            If Bus Pirate does not acknowledge the command.
        """
        self.check_mode('uart')
        if not (0b00 <= data_parity_setting <= 0b11):
            raise ValueError(f"Invalid data_parity_setting: {data_parity_setting}. Use UART.DATA_PARITY_* constants.")

        # Construct the configuration byte for 0x80 command
        # Bit 3: Output type (1 for 3.3V push-pull, 0 for open drain)
        # Bit 2-1: Data/Parity (as per data_parity_setting)
        # Bit 0: Stop bits (0 for 1 stop bit, 1 for 2 stop bits)
        # The RX polarity (rx_idle_high) is also part of this byte for some BP UART modes.
        # Config byte: 1000wxyz (x=Out, y=Data/Parity, z=Stop, w=RX Polarity - this order can vary)
        # BBIO v1 UART spec: 0x80 | (Pin Output << 3) | (Data/Parity << 1) | (Stop Bit << 0)
        # RX polarity (bit 0 of a *different* config byte 0x0X usually, or part of 0x80 for some)
        # The common interpretation for 0x80 command:
        # bit3: Output type (0=ODC, 1=Normal)
        # bit2: RX Polarity (0=IdleLow, 1=IdleHigh) <<< THIS IS WHERE IT IS IN SOME SPECS for 0x80
        # bit1: Data/Parity (0=8N1/8N2, 1=9N1/9N2) <<< Only two options, this means 8E/8O done elsewhere
        # bit0: Stop bits (0=1 stop, 1=2 stops)
        # This is confusing. Let's follow the common_functions.py example structure as a guide.
        # common_functions.py uses: (output_type_val << 3) | (parity_val << 1) | (stop_bits_val << 0)
        # where parity_val is 00=8N, 01=8E, 10=8O, 11=9N. This uses 2 bits.
        # And it does not include RX polarity in this byte.
        # Let's assume RX polarity is a separate command or part of the peripheral config for now.
        # For this function, we will set the 0x80 based values.

        config_byte = 0
        if output_3v3:
            config_byte |= (1 << 3)
        
        config_byte |= (data_parity_setting << 1) # Uses 2 bits for data/parity

        if not stop_1bit: # if stop_1bit is False, it means 2 stop bits (value 1)
            config_byte |= 1 
        
        # The RX polarity bit: Some specs say it's bit 0 of 0x8X command for UART config.
        # e.g., 0x8_ | (output_type << 3) | (databits_parity << 2) | (stop_bits << 1) | (rx_polarity << 0)
        # If we follow common_functions' structure, rx_polarity is not here.
        # However, the parameter is rx_idle_high. Let's try to include it if possible,
        # assuming it's the most significant of the lower 4 bits if that was the case (100WXYZ).
        # For now, stick to the 3 parameters for 0x80 that are common: output, data/parity, stop.
        # We can add a separate method for RX polarity if needed, or adjust if a clear spec for this BP version emerges.
        # The `rx_idle_high` parameter implies control. The `_CMD_CONFIGURE_UART_BASE` is 0x80.
        # Let's assume `rx_idle_high` controls the standard RX polarity (idle high = normal).
        # Bus Pirate UART mode usually has a separate command for RX polarity inversion.
        # Let's assume this 0x80 command *does not* set RX polarity directly.
        # TODO: Clarify RX polarity setting for this Bus Pirate UART implementation.
        # For now, `rx_idle_high` will be used to set a flag or raise if we can't control it here.

        self.write(self._CMD_CONFIGURE_UART_BASE | config_byte)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError(f"Could not configure UART protocol (0x{self._CMD_CONFIGURE_UART_BASE | config_byte:02X}). Bus Pirate did not acknowledge.")
        self._uart_protocol_config = config_byte
        # Note: rx_idle_high parameter is not directly used to form config_byte here yet.
        # A separate command like 0x08/0x09 for RX polarity might be needed.


    def configure_peripherals(self, power: bool, pullups: bool, aux_control: bool) -> None:
        """ Configure UART related peripherals: Power, Pull-ups, AUX pin.
        
        Uses command `_CMD_SET_PERIPHERALS_BASE` (0x40).
        Bit 3: Power (1=On, 0=Off)
        Bit 2: Pull-up resistors (1=On, 0=Off)
        Bit 1: AUX pin state/control (1=High/Active, 0=Low/Inactive/Input)
        Bit 0: CS pin (Not applicable for UART, typically set to 0)

        Parameters
        ----------
        power : bool
            True to enable power supplies, False to disable.
        pullups : bool
            True to enable on-board pull-up resistors, False to disable.
        aux_control : bool 
            True to set AUX pin high/active, False for low/inactive (or input depending on FW).
        
        Raises
        ------
        ProtocolError
            If Bus Pirate does not acknowledge the command.
        """
        self.check_mode('uart')
        config_byte = 0
        if power:
            config_byte |= (1 << 3)
        if pullups:
            config_byte |= (1 << 2)
        if aux_control:
            config_byte |= (1 << 1)
        # Bit 0 for CS is not used in UART, keep 0.

        self.write(self._CMD_SET_PERIPHERALS_BASE | config_byte)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError(f"Could not configure UART peripherals (0x{self._CMD_SET_PERIPHERALS_BASE | config_byte:02X}). Bus Pirate did not acknowledge.")
        self._peripheral_config = config_byte

    def enable_rx(self) -> None:
        """ Enable receiving UART data (e.g., before a bulk read). 
        Some firmwares might require this before `self.read()` is effective for continuous streaming.
        Uses command `_CMD_ENABLE_RX` (0x04).
        """
        self.check_mode('uart')
        self.write(self._CMD_ENABLE_RX)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError("Could not enable UART RX. Bus Pirate did not acknowledge.")

    def disable_rx(self) -> None:
        """ Disable receiving UART data. Counterpart to `enable_rx`.
        Uses command `_CMD_DISABLE_RX` (0x05).
        """
        self.check_mode('uart')
        self.write(self._CMD_DISABLE_RX)
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError("Could not disable UART RX. Bus Pirate did not acknowledge.")

    def enter_bridge_mode(self) -> None:
        """ UART bridge mode (Bus Pirate reset required to exit).

        Starts a transparent UART bridge using the current configuration.
        Unplug the Bus Pirate or send a reset sequence to exit this mode.
        Uses command `_CMD_UART_BRIDGE_MODE` (0x0F).
        """
        self.check_mode('uart')
        self.write(self._CMD_UART_BRIDGE_MODE)
        if self.response(1, binary=True) != b'\x01': # Expect acknowledge
             raise ProtocolError("Could not enter UART bridge mode. Bus Pirate did not acknowledge.")
        # BP is now in bridge mode, no further commands typically processed until reset.

    def _set_custom_register(self, value: int) -> None:
        """ Sets a custom/legacy UART configuration register.
        
        Uses command `_CMD_SET_CUSTOM_REGISTER_BASE` (0xC0).
        The lower 4 bits of `value` are ORed with the command.
        WARNING: The exact behavior of this register is firmware-dependent and may not be standard.

        Parameters
        ----------
        value : int
            A 4-bit value (0-15) to be written to the custom register.
        
        Raises
        ------
        ValueError
            If value is not between 0 and 15.
        ProtocolError
            If Bus Pirate does not acknowledge.
        """
        self.check_mode('uart')
        if not (0 <= value <= 0x0F):
            raise ValueError(f"Custom register value must be between 0 and 15, got {value}.")
        
        self.write(self._CMD_SET_CUSTOM_REGISTER_BASE | value)
        # self.timeout(0.1) # Old code had this, default should be fine
        if self.response(1, binary=True) != b'\x01':
            raise ProtocolError(f"Could not set custom UART register to {value:#02x}. Bus Pirate did not acknowledge.")
        self._custom_register_value = value

    def _read_custom_register(self) -> int:
        """ Reads from a custom/legacy UART configuration register.
        
        Uses command `_CMD_READ_CUSTOM_REGISTER` (0xD0).
        WARNING: The exact behavior and meaning of the returned value is firmware-dependent.

        Returns
        -------
        int
            The 8-bit value read from the custom register.
            
        Raises
        ------
        ProtocolError
            If Bus Pirate does not return a valid byte.
        """
        self.check_mode('uart')
        self.write(self._CMD_READ_CUSTOM_REGISTER)
        # self.timeout(0.1) # Old code had this
        response_byte = self.response(1, binary=True)
        if not response_byte: # Should not happen if timeout works correctly
            raise ProtocolError("Did not receive a response when reading custom UART register.")
        return response_byte[0]

    # Note: The original UARTCfg class was removed as its constants were unclear
    # and did not directly map to standard Bus Pirate UART commands.
    # Use the new `configure_protocol` and `configure_peripherals` methods instead.
    # The original FOSC global constant was moved into the class as _FOSC.
    # The UARTSpeed class was kept and used for the `speed` property.
    # Original `manual_speed_cfg` renamed to `set_baudrate_raw`.
    # Original `begin_input`/`end_input` renamed to `enable_rx`/`disable_rx`.
    # Original `set_cfg`/`read_cfg` renamed to `_set_custom_register`/`_read_custom_register`.
