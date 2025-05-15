# UART Examples

This page contains practical examples for using the UART interface with pyBusPirateLite.

## Basic UART Communication

```python
from pyBusPirateLite.UART import UART

# Initialize UART interface
uart = UART()
uart.speed = '115200'
uart.configure(power=True)

# Send data
uart.write([0x48, 0x65, 0x6c, 0x6c, 0x6f])  # Send "Hello"

# Read data
data = uart.read(5)  # Read 5 bytes
```

## Reading from UART

```python
from pyBusPirateLite.UART import UART

def read_uart_data(length: int = 1) -> list:
    """Read data from UART.
    
    Args:
        length: Number of bytes to read
        
    Returns:
        List of bytes read
    """
    uart = UART()
    uart.speed = '115200'
    
    return uart.read(length)
```

## Writing to UART

```python
from pyBusPirateLite.UART import UART

def write_uart_data(data: list) -> None:
    """Write data to UART.
    
    Args:
        data: List of bytes to write
    """
    uart = UART()
    uart.speed = '115200'
    
    uart.write(data)
```

## Using Context Manager

```python
from pyBusPirateLite.UART import UART

def send_command(command: str) -> list:
    """Send a command and read response using context manager."""
    with UART() as uart:
        uart.speed = '115200'
        # Send command
        uart.write([ord(c) for c in command])
        # Read response
        return uart.read(10)  # Adjust length as needed
```

## Configuring UART Parameters

```python
from pyBusPirateLite.UART import UART

def configure_uart(baudrate: str = '115200', 
                  data_bits: int = 8,
                  parity: str = 'none',
                  stop_bits: int = 1) -> None:
    """Configure UART parameters.
    
    Args:
        baudrate: Communication speed (e.g., '9600', '115200')
        data_bits: Number of data bits (5-9)
        parity: Parity type ('none', 'even', 'odd')
        stop_bits: Number of stop bits (1-2)
    """
    uart = UART()
    uart.speed = baudrate
    
    # Configure UART parameters
    uart.configure(
        data_bits=data_bits,
        parity=parity,
        stop_bits=stop_bits
    )
```

## Error Handling Example

```python
from pyBusPirateLite.UART import UART
from pyBusPirateLite.exceptions import BusPirateError

def safe_uart_transfer(data: list, read_length: int = 0) -> list:
    """Perform UART transfer with error handling.
    
    Args:
        data: Data to write
        read_length: Number of bytes to read after writing
        
    Returns:
        List of bytes received
        
    Raises:
        BusPirateError: If communication fails
    """
    try:
        with UART() as uart:
            uart.speed = '115200'
            uart.write(data)
            if read_length > 0:
                return uart.read(read_length)
            return []
    except BusPirateError as e:
        print(f"UART communication error: {e}")
        raise
```

## Common Use Cases

### Reading from a GPS Module

```python
from pyBusPirateLite.UART import UART
import time

def read_gps_data() -> str:
    """Read NMEA data from a GPS module.
    
    Returns:
        NMEA sentence as string
    """
    with UART() as uart:
        uart.speed = '9600'  # Common GPS baudrate
        
        # Read until we get a complete NMEA sentence
        data = []
        while True:
            byte = uart.read(1)
            if byte:
                data.append(byte[0])
                if byte[0] == 0x0A:  # End of sentence
                    break
                    
        return bytes(data).decode('ascii')
```

### Communicating with an Arduino

```python
from pyBusPirateLite.UART import UART
import time

def send_to_arduino(command: str) -> str:
    """Send command to Arduino and read response.
    
    Args:
        command: Command string to send
        
    Returns:
        Response from Arduino
    """
    with UART() as uart:
        uart.speed = '9600'  # Common Arduino baudrate
        
        # Send command
        uart.write([ord(c) for c in command + '\n'])
        
        # Wait for response
        time.sleep(0.1)
        
        # Read response
        data = []
        while True:
            byte = uart.read(1)
            if not byte:
                break
            data.append(byte[0])
            if byte[0] == 0x0A:  # End of response
                break
                
        return bytes(data).decode('ascii').strip()
```

### Binary Protocol Example

```python
from pyBusPirateLite.UART import UART
import struct

def send_binary_command(command_id: int, data: list) -> list:
    """Send binary command and read response.
    
    Args:
        command_id: Command identifier
        data: Command data
        
    Returns:
        Response data
    """
    with UART() as uart:
        uart.speed = '115200'
        
        # Create command packet
        length = len(data)
        packet = [0xAA, command_id, length] + data
        
        # Add checksum
        checksum = sum(packet) & 0xFF
        packet.append(checksum)
        
        # Send packet
        uart.write(packet)
        
        # Read response
        response = uart.read(3)  # Header + length
        if len(response) < 3:
            raise BusPirateError("Incomplete response")
            
        # Verify response header
        if response[0] != 0xAA:
            raise BusPirateError("Invalid response header")
            
        # Read response data
        data_length = response[2]
        data = uart.read(data_length + 1)  # +1 for checksum
        
        # Verify checksum
        received_checksum = data[-1]
        calculated_checksum = sum(response + data[:-1]) & 0xFF
        if received_checksum != calculated_checksum:
            raise BusPirateError("Checksum error")
            
        return data[:-1]  # Return data without checksum
``` 