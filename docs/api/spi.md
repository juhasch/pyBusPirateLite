# SPI Interface

The SPI interface provides access to the Bus Pirate's SPI functionality.

## Class: SPI

```python
from pyBusPirateLite.SPI import SPI
```

### Initialization

```python
spi = SPI(portname='', speed=115200, timeout=0.1, connect=True)
```

Parameters:
- `portname` (str): Name of comport (e.g., '/dev/bus_pirate' or 'COM3')
- `speed` (int): Communication speed (default: 115200)
- `timeout` (float): Timeout in seconds to wait for reply
- `connect` (bool): Whether to connect immediately

### Methods

#### enter()
Enter SPI mode. Returns True if successful.

#### config
Property to get/set SPI configuration:
- `CFG_IDLE`: Clock idle state
- `CFG_SAMPLE`: Clock edge to sample on
- `CFG_CLK_EDGE`: Clock edge to output on
- `CFG_PUSH_PULL`: Output type

#### write_then_read(numtx, numrx, txdata)
Write then read data:
- `numtx`: Number of bytes to write
- `numrx`: Number of bytes to read
- `txdata`: Data to write

Returns the read data as bytes.

### Example

```python
from pyBusPirateLite.SPI import SPI

# Initialize SPI
spi = SPI()

# Configure SPI
spi.config = SPI.CFG_PUSH_PULL | SPI.CFG_IDLE

# Write and read data
data = spi.write_then_read(1, 1, [0x00])
``` 