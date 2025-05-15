# UART Interface

The UART interface provides access to the Bus Pirate's UART functionality.

## Class: UART

```python
from pyBusPirateLite.UART import UART
```

### Initialization

```python
uart = UART(portname='', speed=115200, timeout=0.1, connect=True)
```

Parameters:
- `portname` (str): Name of comport (e.g., '/dev/bus_pirate' or 'COM3')
- `speed` (int): Communication speed (default: 115200)
- `timeout` (float): Timeout in seconds to wait for reply
- `connect` (bool): Whether to connect immediately

### Methods

#### enter()
Enter UART mode. Returns True if successful.

#### speed
Property to get/set UART speed. Available speeds:
- '300'
- '1200'
- '2400'
- '4800'
- '9600'
- '19200'
- '38400'
- '57600'
- '115200'

#### write(data)
Write data to UART:
- `data`: Bytes or string to write

#### read(length=1)
Read data from UART:
- `length`: Number of bytes to read

Returns the read data as bytes.

### Example

```python
from pyBusPirateLite.UART import UART

# Initialize UART
uart = UART()

# Set speed
uart.speed = '9600'

# Write data
uart.write(b'Hello')

# Read response
response = uart.read(5)
``` 