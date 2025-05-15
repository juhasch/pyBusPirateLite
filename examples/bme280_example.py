from pyBusPirateLite.I2C import I2C

# BME280 I2C address (default)
I2C_ADDR = 0xec

# BME280 Registers
BME280_REG_ID = 0xD0
BME280_REG_CTRL_MEAS = 0xF4
BME280_REG_TEMP_MSB = 0xFA

# BME280 Temperature Calibration Registers (added)
BME280_REG_DIG_T1_LSB = 0x88 # unsigned short, little-endian
BME280_REG_DIG_T2_LSB = 0x8A # signed short, little-endian
BME280_REG_DIG_T3_LSB = 0x8C # signed short, little-endian
# MSB registers are LSB+1, e.g., BME280_REG_DIG_T1_MSB = 0x89

i2c = I2C()
i2c.speed = '400kHz' 
i2c.configure(power=True, pullup=True) # Enable power and pull-ups

i2c.start()
i2c.transfer([I2C_ADDR, BME280_REG_ID])
r = i2c.write_then_read(1, 1, [I2C_ADDR+1])
i2c.stop()

print(f'BME280 ID={hex(r[0])}')

# Read temperature calibration data (added section)
print("\nReading BME280 Temperature Calibration Coefficients...")
# dig_T1 (unsigned short)
i2c.start()
i2c.transfer([I2C_ADDR, BME280_REG_DIG_T1_LSB])
dig_T1_bytes = i2c.write_then_read(1, 2, [I2C_ADDR+1]) # Read 2 bytes (LSB, MSB)
i2c.stop()

# dig_T2 (signed short)
i2c.start()
i2c.transfer([I2C_ADDR, BME280_REG_DIG_T2_LSB])
dig_T2_bytes = i2c.write_then_read(1, 2, [I2C_ADDR+1]) # Read 2 bytes (LSB, MSB)
i2c.stop()

# dig_T3 (signed short)
i2c.start()
i2c.transfer([I2C_ADDR, BME280_REG_DIG_T3_LSB])
dig_T3_bytes = i2c.write_then_read(1, 2, [I2C_ADDR+1]) # Read 2 bytes (LSB, MSB)
i2c.stop()

dig_T1, dig_T2, dig_T3 = 0, 0, 0 # Initialize with default values

if (dig_T1_bytes and len(dig_T1_bytes) == 2 and
   dig_T2_bytes and len(dig_T2_bytes) == 2 and
   dig_T3_bytes and len(dig_T3_bytes) == 2):

    # LSB first, then MSB for little-endian
    dig_T1 = (dig_T1_bytes[1] << 8) | dig_T1_bytes[0] # u16

    dig_T2 = (dig_T2_bytes[1] << 8) | dig_T2_bytes[0] # s16
    if dig_T2 > 32767: dig_T2 -= 65536

    dig_T3 = (dig_T3_bytes[1] << 8) | dig_T3_bytes[0] # s16
    if dig_T3 > 32767: dig_T3 -= 65536

    print(f"dig_T1 (u16): {dig_T1}, dig_T2 (s16): {dig_T2}, dig_T3 (s16): {dig_T3}")
else:
    print("Error: Failed to read one or more temperature calibration coefficients.")
    print("Temperature calculation may be inaccurate. Ensure sensor is connected and I2C_ADDR is correct.")
    # Optionally, exit or use default calibration values if critical
    # For this example, we'll proceed with potentially zeroed calibration values.

print("\nConfiguring BME280 sensor (oversampling x1 for temp & press, normal mode)...")
# ctrl_meas (0xF4): temp os x1 (001), press os x1 (001), normal mode (11) -> 0b00100111 = 0x27
config_payload = [I2C_ADDR, BME280_REG_CTRL_MEAS, 0x27]
i2c.start()
i2c.transfer(config_payload)
i2c.stop()

print("\nAttempting to read Temperature data...")
# Write 1 byte (BME280_REG_TEMP_MSB) using i2c_addr_write, then read 3 bytes.
i2c.start()
i2c.transfer([I2C_ADDR, BME280_REG_TEMP_MSB])
temp_raw_bytes_list = i2c.write_then_read(1, 3, [I2C_ADDR+1])
i2c.stop()

if temp_raw_bytes_list and len(temp_raw_bytes_list) == 3:
    temp_msb = temp_raw_bytes_list[0]
    temp_lsb = temp_raw_bytes_list[1]
    temp_xlsb = temp_raw_bytes_list[2] # XLSB contains the 4 LSBs of temperature
    # Combine them into a raw temperature value
    # Formula from BME280 datasheet: (msb << 12) | (lsb << 4) | (xlsb >> 4)
    raw_temp = (temp_msb << 12) | (temp_lsb << 4) | (temp_xlsb >> 4)
    print(f"Raw temperature data: MSB={hex(temp_msb)}, LSB={hex(temp_lsb)}, XLSB={hex(temp_xlsb)}")
    print(f"Raw combined temperature value (adc_T): {raw_temp}")

    # Calculate temperature in Celsius using calibration data (added section)
    # Formula from BME280 datasheet (adc_T is raw_temp)
    if dig_T1 != 0 or dig_T2 != 0 or dig_T3 != 0: # Check if calibration data was read
        var1 = ((((raw_temp >> 3) - (dig_T1 << 1))) * dig_T2) >> 11
        var2 = (((((raw_temp >> 4) - dig_T1) * ((raw_temp >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
        t_fine = var1 + var2
        temperature_celsius = ((t_fine * 5 + 128) >> 8) / 100.0
        print(f"t_fine: {t_fine}")
        print(f"Calculated temperature: {temperature_celsius:.2f} °C")
    else:
        print("Skipping temperature calculation due to missing calibration data.")
        print("Note: Further calibration/compensation using trimming parameters is needed to get actual Celsius value.")
else:
    print(f"Error: Failed to read temperature data. Return: {temp_raw_bytes_list}")

i2c.configure(power=False, pullup=False)

