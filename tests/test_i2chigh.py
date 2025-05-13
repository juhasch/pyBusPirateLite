import pytest
from unittest.mock import MagicMock, patch
from pyBusPirateLite.I2Chigh import I2Chigh
from pyBusPirateLite.base import ProtocolError # Though I2Chigh uses IOError for NACKs

# Use a common mock for serial.Serial for all tests in this module
# This prevents trying to connect to a real Bus Pirate
@pytest.fixture(autouse=True)
def mock_serial_fixture():
    with patch('serial.Serial') as mock_serial_constructor:
        mock_serial_instance = MagicMock()
        # Simulate successful open
        mock_serial_instance.is_open = True
        mock_serial_instance.in_waiting = 0
        mock_serial_constructor.return_value = mock_serial_instance
        yield mock_serial_constructor

@pytest.fixture
def i2chigh_instance():
    """Provides an I2Chigh instance with a mocked serial port, not connected."""
    # connect=False prevents __init__ from trying to connect and enter BB mode
    instance = I2Chigh(connect=False) 
    # Manually set mode as if enter_i2c() was successful
    instance.mode = 'i2c' 
    
    # Mock the low-level I2C methods that I2Chigh methods will call
    instance.start = MagicMock(return_value=b'\x00') # Assuming start might return status
    instance.stop = MagicMock(return_value=b'\x00')  # Assuming stop might return status
    instance.transfer = MagicMock()
    instance.read_byte = MagicMock()
    instance.ack = MagicMock(return_value=b'\x00') # Assuming ack might return status
    instance.nack = MagicMock(return_value=b'\x00') # Assuming nack might return status
    
    # Ensure port is a MagicMock if it wasn't set by autouse fixture (it should be)
    if not isinstance(instance.port, MagicMock):
        instance.port = MagicMock()
        instance.port.is_open = True
        instance.port.in_waiting = 0
        
    return instance

# --- Tests for get_byte ---
def test_get_byte_success(i2chigh_instance):
    bp = i2chigh_instance
    i2c_addr = 0x50
    reg_addr = 0x10
    expected_byte = 0xAA

    bp.transfer.side_effect = [
        b'\x00\x00',  # ACK for write i2c_addr, reg_addr
        b'\x00'      # ACK for write i2c_addr | 0x01
    ]
    bp.read_byte.return_value = bytes([expected_byte])

    result = bp.get_byte(i2c_addr, reg_addr)

    assert result == expected_byte
    assert bp.start.call_count == 2
    bp.transfer.assert_any_call([(i2c_addr << 1), reg_addr])
    bp.transfer.assert_any_call([(i2c_addr << 1) | 0x01])
    bp.read_byte.assert_called_once()
    bp.nack.assert_called_once() # nack after read
    bp.stop.assert_called_once()

def test_get_byte_nack_on_write_address_phase(i2chigh_instance):
    bp = i2chigh_instance
    i2c_addr = 0x51
    reg_addr = 0x11

    # Simulate NACK on the first transfer (addressing the device for write)
    bp.transfer.return_value = b'\x01\x00' # NACK on first byte of transfer

    with pytest.raises(IOError) as excinfo:
        bp.get_byte(i2c_addr, reg_addr)
    
    assert f"I2C device 0x{i2c_addr:02x} did not ACK register 0x{reg_addr:02x}" in str(excinfo.value)
    assert bp.start.call_count == 1 # Only the first start before failure
    bp.transfer.assert_called_once_with([(i2c_addr << 1), reg_addr])
    bp.read_byte.assert_not_called()
    bp.stop.assert_not_called() # Should not reach stop if NACKed early

def test_get_byte_nack_on_read_address_phase(i2chigh_instance):
    bp = i2chigh_instance
    i2c_addr = 0x52
    reg_addr = 0x12

    bp.transfer.side_effect = [
        b'\x00\x00',  # ACK for write i2c_addr, reg_addr
        b'\x01'      # NACK for write i2c_addr | 0x01
    ]

    with pytest.raises(IOError) as excinfo:
        bp.get_byte(i2c_addr, reg_addr)
    
    assert f"I2C device 0x{i2c_addr:02x} did not ACK for read operation" in str(excinfo.value)
    assert bp.start.call_count == 2
    bp.transfer.assert_any_call([(i2c_addr << 1), reg_addr])
    bp.transfer.assert_any_call([(i2c_addr << 1) | 0x01])
    bp.read_byte.assert_not_called()
    # bp.stop might or might not be called depending on where error handling is.
    # Based on I2Chigh.get_byte, stop is not called if the second transfer NACKs.

# --- Tests for set_byte ---
def test_set_byte_success(i2chigh_instance):
    bp = i2chigh_instance
    i2c_addr = 0x60
    reg_addr = 0x20
    value_to_set = 0xBB

    bp.transfer.return_value = b'\x00\x00\x00' # All ACKs

    bp.set_byte(i2c_addr, reg_addr, value_to_set)

    bp.start.assert_called_once()
    bp.transfer.assert_called_once_with([(i2c_addr << 1), reg_addr, value_to_set])
    bp.stop.assert_called_once()

def test_set_byte_value_out_of_range(i2chigh_instance):
    bp = i2chigh_instance
    with pytest.raises(ValueError):
        bp.set_byte(0x60, 0x20, 256)
    with pytest.raises(ValueError):
        bp.set_byte(0x60, 0x20, -1)

def test_set_byte_nack_received(i2chigh_instance):
    bp = i2chigh_instance
    i2c_addr = 0x61
    reg_addr = 0x21
    value_to_set = 0xCC

    # Simulate NACK on the data byte
    bp.transfer.return_value = b'\x00\x00\x01' 

    with pytest.raises(IOError) as excinfo:
        bp.set_byte(i2c_addr, reg_addr, value_to_set)
    
    assert f"I2C write to device 0x{i2c_addr:02x}, register 0x{reg_addr:02x} failed" in str(excinfo.value)
    assert "NACK received at transfer byte(s): [2]" in str(excinfo.value) # NACK on 3rd byte sent (index 2)
    bp.start.assert_called_once()
    bp.transfer.assert_called_once_with([(i2c_addr << 1), reg_addr, value_to_set])
    bp.stop.assert_called_once() # Stop is called even on NACK in set_byte 