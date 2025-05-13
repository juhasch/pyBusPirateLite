# SI1145 Light Sensor Example

This example demonstrates how to use the SI1145 light sensor with pyBusPirateLite. The SI1145 is an I2C-based sensor that can measure:
- UV index
- Ambient light (visible and IR)
- Proximity

## Hardware Setup

Connect the SI1145 to the BusPirate as follows:

- VDD → 3.3V
- GND → GND
- SDA → SDA
- SCL → SCL

## Basic Usage

```python
from pyBusPirateLite.I2C import I2C
import time

class SI1145:
    # I2C address
    ADDR = 0x60
    
    # Register addresses
    REG_PART_ID = 0x00
    REG_REV_ID = 0x01
    REG_SEQ_ID = 0x02
    REG_INT_CFG = 0x03
    REG_IRQ_ENABLE = 0x04
    REG_IRQ_MODE1 = 0x05
    REG_IRQ_MODE2 = 0x06
    REG_HW_KEY = 0x07
    REG_MEAS_RATE = 0x08
    REG_ALS_RATE = 0x09
    REG_PS_RATE = 0x0A
    REG_ALS_LOW_TH0 = 0x0B
    REG_ALS_LOW_TH1 = 0x0C
    REG_ALS_HIGH_TH0 = 0x0D
    REG_ALS_HIGH_TH1 = 0x0E
    REG_PS_LED21 = 0x0F
    REG_PS_LED3 = 0x10
    REG_PS1_TH0 = 0x11
    REG_PS1_TH1 = 0x12
    REG_PS2_TH0 = 0x13
    REG_PS2_TH1 = 0x14
    REG_PS3_TH0 = 0x15
    REG_PS3_TH1 = 0x16
    REG_PARAM_WR = 0x17
    REG_COMMAND = 0x18
    REG_RESPONSE = 0x20
    REG_IRQ_STATUS = 0x21
    REG_ALS_VIS_DATA0 = 0x22
    REG_ALS_VIS_DATA1 = 0x23
    REG_ALS_IR_DATA0 = 0x24
    REG_ALS_IR_DATA1 = 0x25
    REG_PS1_DATA0 = 0x26
    REG_PS1_DATA1 = 0x27
    REG_PS2_DATA0 = 0x28
    REG_PS2_DATA1 = 0x29
    REG_PS3_DATA0 = 0x2A
    REG_PS3_DATA1 = 0x2B
    REG_AUX_DATA0 = 0x2C
    REG_AUX_DATA1 = 0x2D
    
    # Commands
    CMD_PARAM_QUERY = 0x80
    CMD_PARAM_SET = 0xA0
    CMD_NOP = 0x00
    CMD_RESET = 0x01
    CMD_BUSADDR = 0x02
    CMD_PS_FORCE = 0x05
    CMD_ALS_FORCE = 0x06
    CMD_PSALS_FORCE = 0x07
    CMD_PS_PAUSE = 0x09
    CMD_ALS_PAUSE = 0x0A
    CMD_PSALS_PAUSE = 0x0B
    CMD_PS_AUTO = 0x0D
    CMD_ALS_AUTO = 0x0E
    CMD_PSALS_AUTO = 0x0F
    CMD_GET_CAL = 0x12
    
    def __init__(self):
        """Initialize SI1145 sensor."""
        self.i2c = I2C()
        self.i2c.speed = '400kHz'
        self.i2c.configure(power=True)
        
        # Check if sensor is present
        if not self._check_id():
            raise RuntimeError("SI1145 not found")
            
        # Initialize sensor
        self._init_sensor()
        
    def _check_id(self) -> bool:
        """Check if sensor is present by reading part ID."""
        try:
            part_id = self.i2c.write_then_read(1, self.REG_PART_ID, [self.ADDR])[0]
            return part_id == 0x45  # SI1145 part ID
        except:
            return False
            
    def _init_sensor(self) -> None:
        """Initialize sensor with default settings."""
        # Reset
        self._write_reg(self.REG_COMMAND, self.CMD_RESET)
        time.sleep(0.01)
        
        # Set hardware key
        self._write_reg(self.REG_HW_KEY, 0x17)
        
        # Enable UV, visible, and IR measurements
        self._write_reg(self.REG_MEAS_RATE, 0x01)  # 1 measurement per second
        self._write_reg(self.REG_ALS_RATE, 0x01)
        self._write_reg(self.REG_PS_RATE, 0x01)
        
        # Configure LED current
        self._write_reg(self.REG_PS_LED21, 0x03)  # LED1 = 20mA, LED2 = 20mA
        self._write_reg(self.REG_PS_LED3, 0x03)   # LED3 = 20mA
        
        # Start measurements
        self._write_reg(self.REG_COMMAND, self.CMD_PSALS_AUTO)
        
    def _write_reg(self, reg: int, value: int) -> None:
        """Write to a register.
        
        Args:
            reg: Register address
            value: Value to write
        """
        self.i2c.write_then_read(1, reg, [self.ADDR, value])
        
    def _read_reg(self, reg: int) -> int:
        """Read from a register.
        
        Args:
            reg: Register address
            
        Returns:
            Register value
        """
        return self.i2c.write_then_read(1, reg, [self.ADDR])[0]
        
    def read_uv_index(self) -> float:
        """Read UV index.
        
        Returns:
            UV index value
        """
        # Read UV data
        data = self.i2c.write_then_read(2, self.REG_AUX_DATA0, [self.ADDR])
        uv_raw = (data[1] << 8) | data[0]
        
        # Convert to UV index (depends on calibration)
        # This is a simplified conversion
        return uv_raw / 100.0
        
    def read_visible(self) -> int:
        """Read visible light level.
        
        Returns:
            Visible light level in counts
        """
        data = self.i2c.write_then_read(2, self.REG_ALS_VIS_DATA0, [self.ADDR])
        return (data[1] << 8) | data[0]
        
    def read_ir(self) -> int:
        """Read IR light level.
        
        Returns:
            IR light level in counts
        """
        data = self.i2c.write_then_read(2, self.REG_ALS_IR_DATA0, [self.ADDR])
        return (data[1] << 8) | data[0]
        
    def read_proximity(self, led: int = 1) -> int:
        """Read proximity value.
        
        Args:
            led: LED number (1-3)
            
        Returns:
            Proximity value in counts
        """
        if led not in (1, 2, 3):
            raise ValueError("LED must be 1, 2, or 3")
            
        reg = self.REG_PS1_DATA0 + (led - 1) * 2
        data = self.i2c.write_then_read(2, reg, [self.ADDR])
        return (data[1] << 8) | data[0]
        
    def read_all(self) -> dict:
        """Read all sensor values.
        
        Returns:
            Dictionary containing all sensor readings
        """
        return {
            'uv_index': self.read_uv_index(),
            'visible': self.read_visible(),
            'ir': self.read_ir(),
            'proximity': {
                'led1': self.read_proximity(1),
                'led2': self.read_proximity(2),
                'led3': self.read_proximity(3)
            }
        }

# Example usage
def main():
    try:
        # Create sensor instance
        sensor = SI1145()
        
        # Read all values
        values = sensor.read_all()
        print("Sensor readings:")
        print(f"UV Index: {values['uv_index']:.2f}")
        print(f"Visible Light: {values['visible']} counts")
        print(f"IR Light: {values['ir']} counts")
        print("Proximity:")
        print(f"  LED1: {values['proximity']['led1']} counts")
        print(f"  LED2: {values['proximity']['led2']} counts")
        print(f"  LED3: {values['proximity']['led3']} counts")
        
        # Continuous monitoring example
        print("\nMonitoring for 10 seconds...")
        start_time = time.time()
        while time.time() - start_time < 10:
            values = sensor.read_all()
            print(f"\rUV: {values['uv_index']:.2f}  "
                  f"Visible: {values['visible']}  "
                  f"IR: {values['ir']}", end='')
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == '__main__':
    main()
```

## Advanced Usage

### Calibration

The SI1145 requires calibration for accurate UV index measurements. Here's how to calibrate the sensor:

```python
def calibrate_uv(sensor: SI1145, known_uv: float) -> float:
    """Calibrate UV index measurement.
    
    Args:
        sensor: SI1145 instance
        known_uv: Known UV index value for calibration
        
    Returns:
        Calibration factor
    """
    # Take multiple readings
    readings = []
    for _ in range(10):
        readings.append(sensor.read_uv_index())
        time.sleep(0.1)
        
    # Calculate average raw value
    avg_raw = sum(readings) / len(readings)
    
    # Calculate calibration factor
    return known_uv / avg_raw
```

### Proximity Detection

Here's an example of using the proximity sensor to detect objects:

```python
def detect_proximity(sensor: SI1145, 
                    threshold: int = 1000,
                    led: int = 1) -> bool:
    """Detect if an object is near the sensor.
    
    Args:
        sensor: SI1145 instance
        threshold: Proximity threshold
        led: LED to use (1-3)
        
    Returns:
        True if object detected, False otherwise
    """
    return sensor.read_proximity(led) > threshold
```

### Light Level Monitoring

This example shows how to monitor light levels over time:

```python
def monitor_light_levels(sensor: SI1145, 
                        duration: float = 60.0,
                        interval: float = 1.0) -> list:
    """Monitor light levels for a specified duration.
    
    Args:
        sensor: SI1145 instance
        duration: Total monitoring duration in seconds
        interval: Time between readings in seconds
        
    Returns:
        List of (timestamp, readings) tuples
    """
    readings = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        values = sensor.read_all()
        timestamp = time.time() - start_time
        readings.append((timestamp, values))
        time.sleep(interval)
        
    return readings
```

## Notes

1. The SI1145 requires proper initialization before use. The example includes basic initialization, but you may need to adjust parameters based on your specific needs.

2. UV index measurements require calibration for accuracy. The example includes a calibration function, but you'll need a reference UV sensor or known UV conditions for proper calibration.

3. The proximity sensor uses IR LEDs. The detection range and sensitivity can be adjusted by changing the LED current and threshold values.

4. The sensor supports interrupt-driven operation, but this example uses polling for simplicity. For more efficient operation, you can configure the interrupt pins and use the IRQ_STATUS register.

5. The example uses the default I2C address (0x60). If your sensor has a different address, modify the ADDR constant accordingly. 