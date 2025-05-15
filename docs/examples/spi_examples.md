# SPI Examples

This page contains practical examples for using the SPI interface with pyBusPirateLite.

## Basic SPI Communication

```python
from pyBusPirateLite.SPI import SPI

# Initialize SPI interface
spi = SPI()
spi.pins = SPI.PIN_POWER | SPI.PIN_CS 
spi.config = SPI.CFG_PUSH_PULL | SPI.CFG_IDLE
spi.speed = '1MHz'

# Basic transfer
spi.cs = True
data = spi.transfer([0x82, 0x00])
spi.cs = False
```

## Reading from an SPI Device

```python
from pyBusPirateLite.SPI import SPI

def read_spi_device(address: int, length: int) -> list:
    """Read data from an SPI device.
    
    Args:
        address: Register address to read from
        length: Number of bytes to read
        
    Returns:
        List of bytes read from the device
    """
    spi = SPI()
    spi.speed = '1MHz'
    
    # Send read command and address
    spi.cs = True
    spi.transfer([0x03, address])  # 0x03 is typical read command
    
    # Read the data
    data = spi.transfer([0x00] * length)
    spi.cs = False
    
    return data
```

## Writing to an SPI Device

```python
from pyBusPirateLite.SPI import SPI

def write_spi_device(address: int, data: list) -> None:
    """Write data to an SPI device.
    
    Args:
        address: Register address to write to
        data: List of bytes to write
    """
    spi = SPI()
    spi.speed = '1MHz'
    
    # Send write command, address, and data
    spi.cs = True
    spi.transfer([0x02, address] + data)  # 0x02 is typical write command
    spi.cs = False
```

## Using Context Manager

```python
from pyBusPirateLite.SPI import SPI

def read_device_id() -> list:
    """Read device ID using context manager."""
    with SPI() as spi:
        spi.speed = '1MHz'
        spi.cs = True
        # Send read ID command (0x9F is common for many SPI devices)
        data = spi.transfer([0x9F, 0x00, 0x00, 0x00])
        spi.cs = False
        return data
```

## Configuring SPI Mode

```python
from pyBusPirateLite.SPI import SPI

def setup_spi_mode(mode: int = 0) -> None:
    """Configure SPI mode.
    
    Args:
        mode: SPI mode (0-3)
            Mode 0: CPOL=0, CPHA=0
            Mode 1: CPOL=0, CPHA=1
            Mode 2: CPOL=1, CPHA=0
            Mode 3: CPOL=1, CPHA=1
    """
    spi = SPI()
    
    # Set clock polarity and phase
    if mode in (0, 1):
        spi.config = SPI.CFG_IDLE
    else:
        spi.config = SPI.CFG_IDLE | SPI.CFG_CLK_HI
        
    if mode in (0, 2):
        spi.config |= SPI.CFG_EDGE
```

## Error Handling Example

```python
from pyBusPirateLite.SPI import SPI
from pyBusPirateLite.exceptions import BusPirateError

def safe_spi_transfer(data: list) -> list:
    """Perform SPI transfer with error handling.
    
    Args:
        data: List of bytes to transfer
        
    Returns:
        List of bytes received
        
    Raises:
        BusPirateError: If communication fails
    """
    try:
        with SPI() as spi:
            spi.speed = '1MHz'
            spi.cs = True
            result = spi.transfer(data)
            spi.cs = False
            return result
    except BusPirateError as e:
        print(f"SPI communication error: {e}")
        raise
```

## Common Use Cases

### Reading an EEPROM

```python
from pyBusPirateLite.SPI import SPI

def read_eeprom(address: int, length: int) -> list:
    """Read data from an SPI EEPROM.
    
    Args:
        address: Memory address to read from
        length: Number of bytes to read
        
    Returns:
        List of bytes read from EEPROM
    """
    with SPI() as spi:
        spi.speed = '1MHz'
        
        # Send read command and address
        spi.cs = True
        spi.transfer([0x03, (address >> 8) & 0xFF, address & 0xFF])
        
        # Read the data
        data = spi.transfer([0x00] * length)
        spi.cs = False
        
        return data
```

### Writing to an EEPROM

```python
from pyBusPirateLite.SPI import SPI
import time

def write_eeprom(address: int, data: list) -> None:
    """Write data to an SPI EEPROM.
    
    Args:
        address: Memory address to write to
        data: List of bytes to write
    """
    with SPI() as spi:
        spi.speed = '1MHz'
        
        # Enable write
        spi.cs = True
        spi.transfer([0x06])  # Write enable command
        spi.cs = False
        
        # Wait for write enable to take effect
        time.sleep(0.001)
        
        # Write data
        spi.cs = True
        spi.transfer([0x02, (address >> 8) & 0xFF, address & 0xFF] + data)
        spi.cs = False
        
        # Wait for write to complete
        time.sleep(0.01)
``` 