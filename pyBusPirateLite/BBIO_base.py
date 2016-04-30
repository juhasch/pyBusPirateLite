#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
 * Summary :
 * 
 * Created on Jan 26, 2011
 * @author: garrett
"""

import select
from time import sleep
import serial


class BPError(IOError):
    pass


class ProtocolError(IOError):
    pass

"""
PICSPEED = 24MHZ / 16MIPS
"""

"""pinout_uc prior to translating be careful, you have to translate this
when you use it!!! (only wory about this if you are developing code for the editing
this class)"""
pinout_bb = {'AUX':     0b10000,
             'MOSI':    0b01000,
             'CLK':     0b00100,
             'MISO':    0b00010,
             'CS':      0b00001}

class PinCfg:
    POWER = 0x8
    PULLUPS = 0x4
    AUX = 0x2
    CS = 0x1


class BBIOPins:
    # Bits are assigned as such:
    MOSI = 0x01
    CLK = 0x02
    MISO = 0x04
    CS = 0x08
    AUX = 0x10
    PULLUP = 0x20
    POWER = 0x40


class BBIOModes:
    # modes are assigned as such.  Use either the strings or this class in your
    # code
    I2C = 'i2c'
    UART = 'uart'
    SPI = 'spi'
    _1WIRE = '1wire'
    RAW = 'raw'
    BB = 'bb'
    ADC = 'adc'

all_modes = ['i2c', 'uart', 'spi', '1wire', 'raw', 'bb']
all_modes_and_special = ['i2c', 'uart', 'spi', '1wire', 'raw', 'bb', 'adc']
not_bb = ['i2c', 'uart', 'spi', '1wire', 'raw']

def translator(byte, translate):
    """translates a byte so that the pinout is more user friendly (for the standard connector
    orientation)"""
    if translate:
        """maps AUX|MOSI|CLK|MISO|CS to AUX|CLK|MOSI|CS|MISO"""
        if byte > 255:
            raise ValueError('Value Too Large')
        return (byte & 0b11110000) | ((byte & 0b0101) << 1) | ((byte & 0b1010) >> 1)
    else:
        return byte

"""if transltor (self.t) is True then pinout is AUX|CLK|MOSI|CS|MISO
   if translator is False then:                 AUX|MOSI|CLK|MISO|CS
   The first is much more user friendly, the second is the order the
   bus pirate uses (and expects)
   the values in self.uc_port and self.uc_dir are the values you **want**,
   i.e. if you have translate on then they will read AUX|CLK|MOSI|CS|MISO
"""

class BBIO_base:
    """functions used in every mode, the base of class.  Most of these you can
    probably ignore, as they are just used in the other member classes
    Note: Also contains some of the older functions that are now probably outdated
    """
    def __init__(self):
        self.minDelay = 1 / 115200
        self.mode = None
        self.port = None
        self.connected = False
        self.t = True
        self.bp_config = None
        self.bp_port = None
        self.bp_dir = None
        self.portname = ''

    def modestring(self):
        """ Return mode version string """
        self.write(0x01)
        self.timeout(self.minDelay * 10)
        return self.response(4)

    _attempts_ = 0  # global stored for use in enter

    def enter(self):
        """Enter bitbang mode

        This is the be-all-end-all restart function.  It will keep trying
        to get the bus pirate into bit bang mode even if it is stuck.  Call this
        to get the bus pirate into a known state (bb mode)

        This command resets the Bus Pirate into raw bitbang mode from the user terminal.
        It also resets to raw bitbang mode from raw SPI mode, or any other protocol mode.
        This command always returns a five byte bitbang version string "BBIOx", w
        here x is the current protocol version (currently 1).
        Some terminals send a NULL character (0x00) on start-up, causing the Bus Pirate to enter binary mode when
        it wasn't wanted. To get around this, you must now enter 0x00 at least 20 times to enter raw bitbang mode.
        Note: The Bus Pirate user terminal could be stuck in a configuration menu when your program attempts to enter
        binary mode. One way to ensure that you're at the command line is to send <enter> at least 10 times,
        and then send '#' to reset. Next, send 0x00 to the command line 20+ times until you get the BBIOx version string.
        After entering bitbang mode, you can enter other binary protocol modes.

        Raises
        ------
        IOError
            If device is not connected
        """
        if self.mode == 'bb':
            return
        if self.connected is not True:
            raise IOError('Device not connected')
        self.port.flushInput()
        for i in range(20):
            self.write(0x00)
            r = self.response(1, True)
            if r:
                break
        self.port.flushInput()
        self.write(0x00)
        if self.response(5, True) == "BBIO1":
            self.mode = 'bb'
            self.bp_config = 0x00  # configuration bits determine action of power sources and pullups
            self.bp_port = 0x00  # out_port similar to ports in microcontrollers
            self.bp_dir = 0x1F  # direction port similar to microchip microcontrollers.  (1) is input, (0) is output
            self.recurse_end()
        self.recurse_flush(self.enter)
        raise BPError('Could not enter bitbang mode')

    def resetBP(self):
        """Reset Bus Pirate

        The Bus Pirate responds 0x01 and then performs a complete hardware reset.
        The hardware and firmware version is printed (same as the 'i' command in the terminal),
        and the Bus Pirate returns to the user terminal interface. Send 0x00 20 times to enter binary mode again.
        """
        self.reset()
        self.write(0x0f)
        self.timeout(.1)
        self.port.flushInput()
        self.mode = None

    def connect(self, portname='', speed=115200, timeout=1):
        """ will try to automatically find a port regardless of os

        Parameters
        ----------
        portname : str
            Name of comport (/dev/bus_pirate or COM3)
        speed : int
            Communication speed, use default of 115200
        timeout : int
            Timeout in s to wait for reply

        Raises
        ------
        ImportError
            If helper function to find serial port is not available
        IOError
            If device could not be opened
        """

        try:
            import serial.tools.list_ports as list_ports
        except ImportError:
            raise ImportError('Pyserial version with serial.tools.list_port required (> 3.0')

        if portname == '':
            ports = list_ports.comports()
            for port in ports:
                if port.description == 'FT232R USB UART':
                    portname = port.device
                    break
        self.portname = portname
        try:
            self.port = serial.Serial(portname, speed, timeout=timeout)
        except serial.serialutil.SerialException:
            raise IOError('Could not open port %s' % portname)
        self.connected = True
        self.minDelay = 1 / speed

    def disconnect(self):
        """ Disconnect bus pirate, close com port """
        if self.port:
            self.port.close()

    def timeout(self, timeout = 0.1):
        sleep(timeout)

    def write(self, byte):
        self.port.write(bytes([byte]))
        
    def response(self, byte_count = 1, return_data = False):
        """request a number of bytes and whether you want the data itself.  If it receives a
        '1' then it returns a 1 ('1' is the std bus pirate response for most functions)"""
        data = self.port.read(byte_count)
        if byte_count == 1 and return_data == False:
            if data == 0x01:
                return 1
            else:
                return None
        else:
            return data.decode()

    @property
    def pins(self):
        return self._pins

    @pins.setter
    def pins(self, cfg=0):
        """used in every mode to configure pins.  In bb it configures as either input or output,
        in the other modes it normally configures peripherals such as power supply and the aux pin"""
        self.write(0x40 | cfg)
        self.timeout(self.minDelay * 10)
        if self.response(1, True) != '\x01':
            raise ValueError("Could not set configure pins")
        self._pins = cfg

    def set_pins_bb(self, pins):
        """same as raw_set_pins, except it returns the value it obtains.
        Necessary to read values in bb mode.  Can be used instead of
        the raw one if you want to know the output"""
        self.check_mode(all_modes_and_special)
        self.write(0x80 | pins)
        self.timeout(self.minDelay)
        return self.response(1, True)

    _attempts_ = 0
    def recurse_end(self):
        self._attempts_ = 0

    def recurse(self, function, *args):
        if self._attempts_ < 15:
            self._attempts_ += 1
            return function(*args)
        raise IOError('bus pirate malfunctioning')

    def recurse_flush(self, function, *args):
        if self._attempts_ < 15:
            self._attempts_ += 1
            for n in range(5):
                self.write(0x00)
            self.port.flushInput()
            return function(*args)
        raise IOError('bus pirate malfunctioning')

    # Self Tests
    def short_selftest(self):
        self.check_mode('bb')
        self.write(0x10)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)

    def long_selftest(self):
        self.check_mode('bb')
        self.write(0x11)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)


    # PWM control
    def setup_PWM(self, prescaler, dutycycle, period):
        self.check_mode('bb')
        self.write(0x12)
        self.write(prescaler)
        self.write((dutycycle >> 8) & 0xFF)
        self.write(dutycycle & 0xFF)
        self.write((period >> 8) & 0xFF)
        self.write(period & 0xFF)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)

    # ADC control
    def ADC_measure(self):
        self.check_mode('bb')
        self.write(0x14)
        self.timeout(self.minDelay)
        return self.response(2, True)

    def mode_string(self):
        self.write(0x01)
        self.timeout(self.minDelay * 10)
        return self.response(1, True)

    """unused legacy code or code I'm not so sure of..."""
    def raw_set_pins(self, pins):
        """kept in for legacy purposes, but not used or recomended"""
        self.check_mode('raw')
        self.write(0x80 | pins)
        self.timeout(self.minDelay)
        return self.response(1)

    def raw_cfg_pins(self, config):
        """practically identical to cfg_pins except it returns a different value"""
        self.write(0x40 | config)
        self.timeout(self.minDelay * 10)
        return self.response(1)

    def read_pins(self):
        """I'm not sure what this is used for.  I can't find reference to the command 0x50"""
        self.write(0x50)
        self.timeout(self.minDelay)
        return self.response(1, True)

    def read_speed(self):
        """I don't see reference to this in the documentation, but it was in the old pyBusPirateLite
        so I'm leaving it in."""
        self.write(0x70)
        select.select(None, None, None, 0.1)
        return self.response(1, True)

    def reset(self):
        """I would recommend not using this.  Use enter_bb instead.  Kept and NOT UPDTADED
        if people are using old code they should probably change their code :D"""
        self.write(0x00)
        self.timeout(self.minDelay * 10)
        self.mode = 'bb'

    # These commands are very strange, because you can also influence the cs
    # pin through the configuration register.  Additional testing needed.
    # These commands MAY OR MAY NOT BE SUPPORTED.
    # They should keep track of everything though, so please
    # test these and report if they work! (also test set_pin('cs') :D
    def cs_low(self):
        self.check_mode(['raw', 'spi'])
        self.bp_port &= ~0b01
        self.write(0x04)
        self.timeout(0.1)
        return self.response(1)

    def cs_high(self):
        self.check_mode(['raw', 'spi'])
        self.bp_port |= 0b01
        self.write(0x05)
        self.timeout(0.1)
        return self.response(1)


""" Higher level commands that can be used in ANY mode"""


def configure_peripherals(self, power=None, pullups=None):
    """sets configuration settings of peripherals.  Use set_pin and clear_pin to
    adjust pins.  Can be used in ANY mode"""
    if self.mode == 'bb':
        if power is not None:
            if (power.upper() == 'YES') or (power.upper() == 'ON'):
                self.bp_config |= 0b01000000
            elif (power.upper() == 'NO') or (power.upper() == 'OFF'):
                self.bp_config &= 0b10111111
            else:
                raise ValueError('incorrect value given for power')
        if pullups is not None:
            if (pullups.upper() == 'YES') or (pullups.upper() == 'ON'):
                self.bp_config |= 0b00100000
            elif (pullups.upper() == 'NO') or (pullups.upper() == 'OFF'):
                self.bp_config &= 0b11011111
            else:
                raise ValueError('incorrect value given for pullups')
        check = (  # returns the whole port back so we filter
            0b11100000 & (translator(ord(self.set_pins_bb(
                translator(self.bp_config | self.bp_port, self.t))), self.t)))
        if check == 0x80 | self.bp_config:
            self.recurse_end()
            return 1
    else:
        self.check_mode(not_bb)
        if power is not None:
            if (power.upper() == 'YES') or (power.upper() == 'ON'):
                self.bp_config |= 0b1000
            elif (power.upper() == 'NO') or (power.upper() == 'OFF'):
                self.bp_config &= 0b0111
        else:
            raise ValueError('incorrect value given for i2c_dir')
        if pullups is not None:
            if (pullups.upper() == 'YES') or (pullups.upper() == 'ON'):
                self.bp_config |= 0b0100
            elif (pullups.upper() == 'NO') or (pullups.upper() == 'OFF'):
                self.bp_config &= 0b1011
        else:
            raise ValueError('incorrect value given for i2c_dir')
        if self.cfg_pins(self.bp_config | self.bp_port):
            self.recurse_end()
            return 1
    return self.recurse(self.configure_peripherals, power, pullups)


def get_peripheral_configuration(self):
    """more of a placeholder than anything right now"""
    if self.mode == 'bb':
        return 0b01100000 & self.bp_config
    else:
        self.check_mode(not_bb)
        return 0b1100 & self.bp_config


def set_pin(self, pin):
    """sets the pin.  needs more testing for non-bb modes, but works in i2c
    and bb modes"""
    self.check_mode(all_modes)
    if self.mode == 'bb':
        pin = pin.upper()
        self.bp_port |= translator(pinout_bb[pin], self.t)
        return self.set_port(self.bp_port)
    else:
        """this code works very strangely, it seems that
        CS and AUX work differently.  Needs more testing
        I think that CS = 1 makes it input (sinks and goes
        low) and CS = 0 makes it output (so it goes high
        w/ pullup)."""
        pin = pin.upper()
        if pin == 'CS':
            self.bp_port |= 0b01
        elif pin == 'AUX':
            self.bp_port &= ~0b10
        else:
            raise ValueError('wrong value')
    self.cfg_pins(self.bp_config | self.bp_port)


def clear_pin(self, pin):
    """clears the pin, needs more testing for non-bb modes"""
    self.check_mode(all_modes)
    if self.mode == 'bb':
        pin = pin.upper()
        # print 'internal port', bin(self.bp_port); #print 'bp port', bin(self.read_port_bb())
        self.bp_port &= ~translator(pinout_bb[pin], self.t)
        # print 'and now internal port', bin(self.bp_port)
        return self.set_port(self.bp_port)
    else:
        """this code works very strangely, it seems that
        CS and AUX work differently.  Needs more testing
        I think that CS = 1 makes it input (sinks and goes
        low) and CS = 0 makes it output (so it goes high
        w/ pullup)."""
        pin = pin.upper()
        if pin == 'CS':
            self.bp_port &= ~0b01
        elif pin == 'AUX':
            self.bp_port |= 0b10
        else:
            raise ValueError('wrong value')
    self.cfg_pins(self.bp_config | self.bp_port)


""" General Commands for Higher-Level Modes.
Note: Some of these do not have error checking implemented
(they return a 0 or 1.  You have to do your own error
checking.  This is as planned, since all of these
depend on the device you are interfacing with)"""


def set_speed(self, speed=0):
    """sets the speed of communication.  Used in every extra mode (not bb)"""
    self.check_mode(not_bb)
    self.write(0x60 | speed)
    self.timeout(self.minDelay * 10)
    if self.response(1, True) == '\x01':
        self.recurse_end()
        return 1
    return self.recurse(self.set_speed, speed)


def send_start_bit(self):
    self.check_mode(['i2c', 'raw'])
    self.write(0x02)
    resp = self.response(1, True)
    if self.response(1, True) == '\x01':
        self.recurse_end()
        return 1
    return self.recurse(self.send_start_bit)


def send_stop_bit(self):
    self.check_mode(['i2c', 'raw'])
    self.write(0x03)
    if self.response(1, True) == 'x01':
        self.recurse_end()
        return 1
    return self.recurse(self.send_stop_bit)


def read_byte(self):
    """Reads a byte from the bus, returns the byte. You must ACK or NACK each
    byte manually.  NO ERROR CHECKING (obviously)"""
    self.check_mode(not_bb)
    if self.mode == 'raw':
        self.write(0x06)
        return self.response(1, True)  # this was changed, before it didn't have the 'True' which means it
        # would have never returned any real data!
    else:
        self.write(0x04)
        return self.response(1, True)


def bulk_trans(self, byte_count=1, byte_string=None):
    """this is how you send data in most of the communication modes.
    See the i2c example function in common_functions.
    Send the data, and read the returned array.
    In I2C:  A '1' means that it was NOT ACKNOWLEDGED, and a '0' means that
    it WAS ACKNOWLEDGED (the reason for this is because this is what the
    bus pirate itself does...)
    In modes other than I2C I think it returns whatever data it gets while
    sending, but this feature is untested.  PLEASE REPORT so that I can
    document it."""
    self.check_mode(not_bb)
    if byte_string is None:
        pass
    self.write(0x10 | (byte_count - 1))
    for i in range(byte_count):
        self.write(byte_string[i])
    data = self.response(byte_count + 1, True)
    if ord(data[0]) == 1:  # bus pirate sent an acknolwedge properly
        self.recurse_end()
        return data[1:]
    self.recurse(self.bulk_trans, byte_count, byte_string)
