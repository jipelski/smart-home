# The MIT License (MIT)
#
# Copyright (c) 2024 Claudiu Florin Jipa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from machine import Pin, SoftI2C
from time import sleep
from bme680 import BME680_I2C
from ble import BLEPeripheral
 
def initialize_bme680():
    """Initialize the BME688 sensor over I2C and return the sensor object."""
    i2c = SoftI2C(scl=Pin(21), sda=Pin(20))
    bme = BME680_I2C(i2c=i2c, address=0x76)
    return bme
 
def read_bme680_sensor(bme):
    """Read temperature, humidity, pressure, and gas from the BME680 sensor.

    Args:
        bme: An instance of the BME680 sensor.

    Returns:
        A tuple containing temperature (C), humidity (%), pressure (hPa), and gas resistance (kOhms),
        or None if reading fails.
    """
    try:
        temperature_C = bme.temperature
        humidity = bme.humidity
        pressure = bme.pressure
        gas_KOhms = bme.gas / 1000
 
        return temperature_C, humidity, pressure, gas_KOhms
    except OSError as e:
        print('Failed to read BME680 sensor: {e}')
        return None
 
def main():
    """Main function to initialize sensors and start BLE communication."""
    rtc = machine.RTC()
    rtc.datetime((2024, 9, 29, 0, 19, 52, 0, 0)) # Manual temporal synchronization 
    bme = initialize_bme680()
    ble = BLEPeripheral()
    
    while True:
        sensor_data = read_bme680_sensor(bme)
        
        if sensor_data is not None:
            temperature_C, humidity, pressure, gas_KOhms = sensor_data
            current_time = rtc.datetime()
            
            ble.send_env_data(current_time, temperature_C, humidity, pressure, gas_KOhms)
        
        sleep(4)
 
if __name__ == "__main__":
    main()
