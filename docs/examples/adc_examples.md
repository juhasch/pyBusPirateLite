# ADC Examples

This page contains practical examples for using the ADC functionality with pyBusPirateLite.

## Basic ADC Reading

```python
from pyBusPirateLite.ADC import ADC

# Initialize ADC interface
adc = ADC()
adc.configure(power=True)

# Read ADC value
value = adc.read()  # Read raw ADC value
voltage = adc.read_voltage()  # Read voltage
```

## Reading Raw ADC Values

```python
from pyBusPirateLite.ADC import ADC

def read_adc_raw() -> int:
    """Read raw ADC value.
    
    Returns:
        Raw ADC value (0-1023)
    """
    adc = ADC()
    return adc.read()
```

## Reading Voltage

```python
from pyBusPirateLite.ADC import ADC

def read_adc_voltage() -> float:
    """Read ADC voltage.
    
    Returns:
        Voltage in volts
    """
    adc = ADC()
    return adc.read_voltage()
```

## Using Context Manager

```python
from pyBusPirateLite.ADC import ADC

def measure_voltage() -> float:
    """Measure voltage using context manager."""
    with ADC() as adc:
        return adc.read_voltage()
```

## Error Handling Example

```python
from pyBusPirateLite.ADC import ADC
from pyBusPirateLite.exceptions import BusPirateError

def safe_adc_read() -> float:
    """Read ADC value with error handling.
    
    Returns:
        Voltage in volts
        
    Raises:
        BusPirateError: If reading fails
    """
    try:
        with ADC() as adc:
            return adc.read_voltage()
    except BusPirateError as e:
        print(f"ADC reading error: {e}")
        raise
```

## Common Use Cases

### Continuous Monitoring

```python
from pyBusPirateLite.ADC import ADC
import time

def monitor_voltage(duration: float = 60.0, interval: float = 1.0) -> list:
    """Monitor voltage for a specified duration.
    
    Args:
        duration: Total monitoring duration in seconds
        interval: Time between readings in seconds
        
    Returns:
        List of (timestamp, voltage) tuples
    """
    readings = []
    start_time = time.time()
    
    with ADC() as adc:
        while time.time() - start_time < duration:
            voltage = adc.read_voltage()
            timestamp = time.time() - start_time
            readings.append((timestamp, voltage))
            time.sleep(interval)
            
    return readings
```

### Voltage Threshold Detection

```python
from pyBusPirateLite.ADC import ADC
import time

def detect_threshold(threshold: float, 
                    above: bool = True,
                    timeout: float = 60.0) -> bool:
    """Detect when voltage crosses a threshold.
    
    Args:
        threshold: Voltage threshold in volts
        above: True to detect above threshold, False for below
        timeout: Maximum time to wait in seconds
        
    Returns:
        True if threshold was detected, False if timeout
    """
    start_time = time.time()
    
    with ADC() as adc:
        while time.time() - start_time < timeout:
            voltage = adc.read_voltage()
            if above and voltage > threshold:
                return True
            elif not above and voltage < threshold:
                return True
            time.sleep(0.1)
            
    return False
```

### Battery Monitoring

```python
from pyBusPirateLite.ADC import ADC
import time

class BatteryMonitor:
    def __init__(self, 
                 full_voltage: float = 4.2,
                 empty_voltage: float = 3.0,
                 check_interval: float = 60.0):
        """Initialize battery monitor.
        
        Args:
            full_voltage: Voltage of fully charged battery
            empty_voltage: Voltage of empty battery
            check_interval: Time between checks in seconds
        """
        self.full_voltage = full_voltage
        self.empty_voltage = empty_voltage
        self.check_interval = check_interval
        self.last_check = 0
        
    def get_battery_level(self) -> float:
        """Get current battery level.
        
        Returns:
            Battery level as percentage (0-100)
        """
        with ADC() as adc:
            voltage = adc.read_voltage()
            
        # Calculate percentage
        percentage = ((voltage - self.empty_voltage) / 
                     (self.full_voltage - self.empty_voltage)) * 100
        
        # Clamp to 0-100 range
        return max(0, min(100, percentage))
        
    def should_check(self) -> bool:
        """Check if it's time to check battery level.
        
        Returns:
            True if check interval has elapsed
        """
        current_time = time.time()
        if current_time - self.last_check >= self.check_interval:
            self.last_check = current_time
            return True
        return False
```

### Temperature Monitoring

```python
from pyBusPirateLite.ADC import ADC
import time

class TemperatureMonitor:
    def __init__(self, 
                 vcc: float = 3.3,
                 r1: float = 10000.0,  # 10k pull-up resistor
                 beta: float = 3950.0,  # Beta value for NTC thermistor
                 t0: float = 298.15,   # Reference temperature (25°C)
                 r0: float = 10000.0): # Resistance at T0
        """Initialize temperature monitor.
        
        Args:
            vcc: Supply voltage
            r1: Pull-up resistor value
            beta: Beta value for NTC thermistor
            t0: Reference temperature in Kelvin
            r0: Thermistor resistance at T0
        """
        self.vcc = vcc
        self.r1 = r1
        self.beta = beta
        self.t0 = t0
        self.r0 = r0
        
    def read_temperature(self) -> float:
        """Read temperature from NTC thermistor.
        
        Returns:
            Temperature in Celsius
        """
        with ADC() as adc:
            voltage = adc.read_voltage()
            
        # Calculate thermistor resistance
        r2 = self.r1 * (self.vcc - voltage) / voltage
        
        # Calculate temperature using beta equation
        temp_k = 1 / (1/self.t0 + (1/self.beta) * 
                     (r2/self.r0).log())
        
        # Convert to Celsius
        return temp_k - 273.15
        
    def monitor_temperature(self, 
                          duration: float = 60.0,
                          interval: float = 1.0) -> list:
        """Monitor temperature for a specified duration.
        
        Args:
            duration: Total monitoring duration in seconds
            interval: Time between readings in seconds
            
        Returns:
            List of (timestamp, temperature) tuples
        """
        readings = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            temp = self.read_temperature()
            timestamp = time.time() - start_time
            readings.append((timestamp, temp))
            time.sleep(interval)
            
        return readings
```

### Light Level Monitoring

```python
from pyBusPirateLite.ADC import ADC
import time

class LightSensor:
    def __init__(self, 
                 vcc: float = 3.3,
                 r1: float = 10000.0,  # 10k pull-up resistor
                 max_lux: float = 1000.0):  # Maximum light level
        """Initialize light sensor.
        
        Args:
            vcc: Supply voltage
            r1: Pull-up resistor value
            max_lux: Maximum light level in lux
        """
        self.vcc = vcc
        self.r1 = r1
        self.max_lux = max_lux
        
    def read_light_level(self) -> float:
        """Read light level from LDR.
        
        Returns:
            Light level in lux
        """
        with ADC() as adc:
            voltage = adc.read_voltage()
            
        # Calculate LDR resistance
        r2 = self.r1 * (self.vcc - voltage) / voltage
        
        # Convert resistance to lux (simplified linear model)
        # In practice, you would use the sensor's datasheet
        # to create a more accurate conversion
        lux = self.max_lux * (1 - r2 / (r2 + self.r1))
        
        return max(0, min(self.max_lux, lux))
        
    def monitor_light(self, 
                     duration: float = 60.0,
                     interval: float = 1.0) -> list:
        """Monitor light level for a specified duration.
        
        Args:
            duration: Total monitoring duration in seconds
            interval: Time between readings in seconds
            
        Returns:
            List of (timestamp, light_level) tuples
        """
        readings = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            lux = self.read_light_level()
            timestamp = time.time() - start_time
            readings.append((timestamp, lux))
            time.sleep(interval)
            
        return readings
``` 