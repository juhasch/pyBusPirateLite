# I2C Interface

The I2C interface provides access to the Bus Pirate's I2C functionality.

## Class: I2C

```python
from pyBusPirateLite.I2C import I2C
```

### Initialization

```python
i2c = I2C(portname='', speed=115200, timeout=0.1, connect=True)
```

Parameters:
- `portname` (str): Name of comport (e.g., '/dev/bus_pirate' or 'COM3')
- `speed` (int): Communication speed (default: 115200)
- `timeout` (float): Timeout in seconds to wait for reply
- `connect` (bool): Whether to connect immediately

### Methods

#### enter()
Enter I2C mode. Returns True if successful.

#### speed
Property to get/set I2C speed. Available speeds:
- '5kHz'
- '50kHz'
- '100kHz'
- '400kHz'

#### start()
Send I2C start condition.

#### stop()
Send I2C stop condition.

#### ack()
Send ACK bit.

#### nack()
Send NACK bit.

#### transfer(txdata)
Bulk I2C write:
- `txdata`: List of bytes to send (1-16 bytes)

Returns list of ACK/NACK responses.

#### write_then_read(numtx, numrx, txdata)
Write then read data:
- `numtx`: Number of bytes to write
- `numrx`: Number of bytes to read
- `txdata`: Data to write

Returns the read data as bytes.

### Example

```python
from pyBusPirateLite.I2C import I2C

# Initialize I2C
i2c = I2C()

# Set speed
i2c.speed = '100kHz'

# Write to device
i2c.start()
i2c.transfer([0xA0, 0x00, 0x01])  # Write to address 0xA0
i2c.stop()

# Read from device
i2c.start()
data = i2c.write_then_read(1, 1, [0xA1])  # Read from address 0xA1
i2c.stop()
``` 