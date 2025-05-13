# BitBang Interface

The BitBang interface provides direct access to the Bus Pirate's pins and basic functionality.

## Class: BitBang

```python
from pyBusPirateLite.BitBang import BitBang
```

### Initialization

```python
bb = BitBang(portname='', speed=115200, timeout=0.1, connect=True)
```

Parameters:
- `portname` (str): Name of comport (e.g., '/dev/bus_pirate' or 'COM3')
- `speed` (int): Communication speed (default: 115200)
- `timeout` (float): Timeout in seconds to wait for reply
- `connect` (bool): Whether to connect immediately

### Pin Constants

```python
PIN_CS     = 0b00001
PIN_MISO   = 0b00010
PIN_CLK    = 0b00100
PIN_MOSI   = 0b01000
PIN_AUX    = 0b10000
PIN_POWER  = 0b100000
PIN_PULLUP = 0b1000000
```

### Methods

#### enter()
Enter BitBang mode. Returns True if successful.

#### outputs
Property to get/set pin directions:
- Get: Returns current state of pins
- Set: Configure pins as inputs or outputs

#### pins
Property to get/set pin states:
- Get: Returns current state of pins
- Set: Set pins high or low

#### adc
Property to read ADC voltage.

#### selftest(complete=False)
Run self-test:
- `complete`: Whether to run complete test (requires jumpers)

Returns number of errors.

#### enable_PWM(frequency, dutycycle=0.5)
Enable PWM output:
- `frequency`: PWM frequency in Hz
- `dutycycle`: Duty cycle (0.0 to 1.0)

#### disable_PWM()
Disable PWM output.

### Example

```python
from pyBusPirateLite.BitBang import BitBang, PIN_CS, PIN_MOSI

# Initialize BitBang
bb = BitBang()

# Configure pins
bb.outputs = PIN_CS | PIN_MOSI  # Set CS and MOSI as outputs

# Set pin states
bb.pins = PIN_CS  # Set CS high

# Read ADC
voltage = bb.adc

# Run self-test
errors = bb.selftest()
``` 