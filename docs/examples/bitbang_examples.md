# Bitbang Examples

This page contains practical examples for using the Bitbang mode with pyBusPirateLite.

## Basic Bitbang Operations

```python
from pyBusPirateLite.BitBang import BitBang

# Initialize Bitbang interface
bb = BitBang()
bb.configure(power=True)

# Set pin directions
bb.direction = 0x0F  # Lower 4 pins as outputs, upper 4 as inputs

# Write to pins
bb.write(0x0A)  # Set pins 1 and 3 high

# Read pins
pins = bb.read()  # Read all pins
```

## Configuring Pin Directions

```python
from pyBusPirateLite.BitBang import BitBang

def configure_pins(output_pins: int) -> None:
    """Configure pin directions.
    
    Args:
        output_pins: Bitmask of pins to configure as outputs
                    (1 = output, 0 = input)
    """
    bb = BitBang()
    bb.direction = output_pins
```

## Reading Pin States

```python
from pyBusPirateLite.BitBang import BitBang

def read_pin_states() -> int:
    """Read current state of all pins.
    
    Returns:
        Bitmask of pin states (1 = high, 0 = low)
    """
    bb = BitBang()
    return bb.read()
```

## Writing to Pins

```python
from pyBusPirateLite.BitBang import BitBang

def set_pin_states(states: int) -> None:
    """Set state of output pins.
    
    Args:
        states: Bitmask of desired pin states (1 = high, 0 = low)
    """
    bb = BitBang()
    bb.write(states)
```

## Using Context Manager

```python
from pyBusPirateLite.BitBang import BitBang

def read_button_state() -> bool:
    """Read state of a button connected to pin 0."""
    with BitBang() as bb:
        bb.direction = 0xFE  # Pin 0 as input, others as outputs
        return bool(bb.read() & 0x01)  # Check if pin 0 is high
```

## Error Handling Example

```python
from pyBusPirateLite.BitBang import BitBang
from pyBusPirateLite.exceptions import BusPirateError

def safe_pin_operation(operation: str, value: int = 0) -> int:
    """Perform pin operation with error handling.
    
    Args:
        operation: 'read' or 'write'
        value: Value to write (for write operation)
        
    Returns:
        Pin states (for read operation)
        
    Raises:
        BusPirateError: If operation fails
    """
    try:
        with BitBang() as bb:
            if operation == 'read':
                return bb.read()
            elif operation == 'write':
                bb.write(value)
                return 0
            else:
                raise ValueError("Invalid operation")
    except BusPirateError as e:
        print(f"Bitbang operation error: {e}")
        raise
```

## Common Use Cases

### LED Control

```python
from pyBusPirateLite.BitBang import BitBang
import time

def blink_led(pin: int, times: int = 5, delay: float = 0.5) -> None:
    """Blink an LED connected to a pin.
    
    Args:
        pin: Pin number (0-7)
        times: Number of times to blink
        delay: Delay between blinks in seconds
    """
    with BitBang() as bb:
        # Configure pin as output
        bb.direction = 1 << pin
        
        for _ in range(times):
            # Turn LED on
            bb.write(1 << pin)
            time.sleep(delay)
            # Turn LED off
            bb.write(0)
            time.sleep(delay)
```

### Button Debouncing

```python
from pyBusPirateLite.BitBang import BitBang
import time

def read_debounced_button(pin: int, debounce_time: float = 0.1) -> bool:
    """Read a debounced button state.
    
    Args:
        pin: Pin number (0-7)
        debounce_time: Debounce time in seconds
        
    Returns:
        True if button is pressed, False otherwise
    """
    with BitBang() as bb:
        # Configure pin as input
        bb.direction = ~(1 << pin) & 0xFF
        
        # Read initial state
        last_state = bool(bb.read() & (1 << pin))
        last_change = time.time()
        
        while True:
            current_state = bool(bb.read() & (1 << pin))
            current_time = time.time()
            
            if current_state != last_state:
                if current_time - last_change >= debounce_time:
                    return current_state
                last_change = current_time
                
            last_state = current_state
            time.sleep(0.01)
```

### Shift Register Control

```python
from pyBusPirateLite.BitBang import BitBang
import time

def shift_out_data(data: int, data_pin: int, clock_pin: int, 
                  latch_pin: int, bits: int = 8) -> None:
    """Shift data out to a shift register.
    
    Args:
        data: Data to shift out
        data_pin: Pin connected to shift register data input
        clock_pin: Pin connected to shift register clock
        latch_pin: Pin connected to shift register latch
        bits: Number of bits to shift out
    """
    with BitBang() as bb:
        # Configure pins as outputs
        bb.direction = (1 << data_pin) | (1 << clock_pin) | (1 << latch_pin)
        
        # Start with latch low
        bb.write(0)
        
        # Shift out data
        for i in range(bits):
            # Set data pin
            if data & (1 << (bits - 1 - i)):
                bb.write(1 << data_pin)
            else:
                bb.write(0)
                
            # Pulse clock
            bb.write(1 << clock_pin)
            time.sleep(0.001)
            bb.write(0)
            time.sleep(0.001)
            
        # Latch data
        bb.write(1 << latch_pin)
        time.sleep(0.001)
        bb.write(0)
```

### I2C Bitbang Implementation

```python
from pyBusPirateLite.BitBang import BitBang
import time

class I2CBitbang:
    def __init__(self, sda_pin: int, scl_pin: int):
        """Initialize I2C bitbang interface.
        
        Args:
            sda_pin: Pin number for SDA
            scl_pin: Pin number for SCL
        """
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        self.bb = BitBang()
        
        # Configure pins as outputs
        self.bb.direction = (1 << sda_pin) | (1 << scl_pin)
        
    def start_condition(self) -> None:
        """Generate I2C start condition."""
        # SDA high, SCL high
        self.bb.write((1 << self.sda_pin) | (1 << self.scl_pin))
        time.sleep(0.001)
        # SDA low while SCL high
        self.bb.write(1 << self.scl_pin)
        time.sleep(0.001)
        
    def stop_condition(self) -> None:
        """Generate I2C stop condition."""
        # SDA low, SCL high
        self.bb.write(1 << self.scl_pin)
        time.sleep(0.001)
        # SDA high while SCL high
        self.bb.write((1 << self.sda_pin) | (1 << self.scl_pin))
        time.sleep(0.001)
        
    def write_byte(self, byte: int) -> bool:
        """Write a byte to I2C bus.
        
        Args:
            byte: Byte to write
            
        Returns:
            True if ACK received, False if NACK
        """
        for i in range(8):
            # Set SDA
            if byte & (1 << (7 - i)):
                self.bb.write((1 << self.sda_pin) | (1 << self.scl_pin))
            else:
                self.bb.write(1 << self.scl_pin)
            time.sleep(0.001)
            
            # Clock pulse
            self.bb.write(0)
            time.sleep(0.001)
            self.bb.write(1 << self.scl_pin)
            time.sleep(0.001)
            
        # Read ACK
        self.bb.direction = 1 << self.scl_pin  # SDA as input
        self.bb.write(1 << self.scl_pin)
        time.sleep(0.001)
        ack = not bool(self.bb.read() & (1 << self.sda_pin))
        self.bb.direction = (1 << self.sda_pin) | (1 << self.scl_pin)
        
        return ack
``` 