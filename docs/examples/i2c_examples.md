# I2C Examples

This page contains practical examples for using the I2C interface with pyBusPirateLite.

## Basic I2C Communication

```python
from pyBusPirateLite.I2C import I2C

# Initialize I2C interface
i2c = I2C()
i2c.speed = '400kHz'
i2c.configure(power=True)

# Write to device
i2c.write_then_read(2, 0, [0xec, 0xf6])  # Write 2 bytes to register 0

# Read from device
data = i2c.write_then_read(1, 1, [0xed])  # Read 1 byte from register 1
```

## Reading from an I2C Device

```python
from pyBusPirateLite.I2C import I2C

def read_i2c_device(address: int, register: int, length: int = 1) -> list:
    """Read data from an I2C device.
    
    Args:
        address: I2C device address (7-bit)
        register: Register address to read from
        length: Number of bytes to read
        
    Returns:
        List of bytes read from the device
    """
    i2c = I2C()
    i2c.speed = '400kHz'
    
    # Write register address then read data
    return i2c.write_then_read(length, register, [address])
```

## Writing to an I2C Device

```python
from pyBusPirateLite.I2C import I2C

def write_i2c_device(address: int, register: int, data: list) -> None:
    """Write data to an I2C device.
    
    Args:
        address: I2C device address (7-bit)
        register: Register address to write to
        data: List of bytes to write
    """
    i2c = I2C()
    i2c.speed = '400kHz'
    
    # Write register address and data
    i2c.write_then_read(len(data), register, [address] + data)
```

## Using Context Manager

```python
from pyBusPirateLite.I2C import I2C

def read_device_id(address: int) -> list:
    """Read device ID using context manager."""
    with I2C() as i2c:
        i2c.speed = '400kHz'
        # Read device ID register (common at 0x00)
        return i2c.write_then_read(1, 0x00, [address])
```

## Scanning I2C Bus

```python
from pyBusPirateLite.I2C import I2C

def scan_i2c_bus() -> list:
    """Scan I2C bus for devices.
    
    Returns:
        List of addresses where devices were found
    """
    found_devices = []
    
    with I2C() as i2c:
        i2c.speed = '100kHz'  # Use slower speed for scanning
        
        # Scan all possible 7-bit addresses
        for addr in range(0x08, 0x78):
            try:
                # Try to read from the device
                i2c.write_then_read(1, 0, [addr])
                found_devices.append(addr)
            except:
                continue
                
    return found_devices
```

## Error Handling Example

```python
from pyBusPirateLite.I2C import I2C
from pyBusPirateLite.exceptions import BusPirateError

def safe_i2c_transfer(address: int, register: int, data: list = None) -> list:
    """Perform I2C transfer with error handling.
    
    Args:
        address: I2C device address
        register: Register address
        data: Optional data to write
        
    Returns:
        List of bytes received
        
    Raises:
        BusPirateError: If communication fails
    """
    try:
        with I2C() as i2c:
            i2c.speed = '400kHz'
            if data is None:
                return i2c.write_then_read(1, register, [address])
            else:
                return i2c.write_then_read(len(data), register, [address] + data)
    except BusPirateError as e:
        print(f"I2C communication error: {e}")
        raise
```

## Common Use Cases

### Reading a Temperature Sensor

```python
from pyBusPirateLite.I2C import I2C

def read_temperature(address: int = 0x48) -> float:
    """Read temperature from an I2C temperature sensor.
    
    Args:
        address: I2C address of the sensor
        
    Returns:
        Temperature in degrees Celsius
    """
    with I2C() as i2c:
        i2c.speed = '400kHz'
        
        # Read temperature register (typically 0x00)
        data = i2c.write_then_read(2, 0x00, [address])
        
        # Convert raw data to temperature
        # This conversion depends on the specific sensor
        temp = (data[0] << 8 | data[1]) / 256.0
        return temp
```

### Writing to an EEPROM

```python
from pyBusPirateLite.I2C import I2C
import time

def write_eeprom(address: int, memory_address: int, data: list) -> None:
    """Write data to an I2C EEPROM.
    
    Args:
        address: I2C address of the EEPROM
        memory_address: Memory address to write to
        data: List of bytes to write
    """
    with I2C() as i2c:
        i2c.speed = '100kHz'  # EEPROMs typically need slower speed
        
        # Write data
        i2c.write_then_read(
            len(data),
            memory_address,
            [address] + data
        )
        
        # Wait for write to complete
        time.sleep(0.01)
``` 