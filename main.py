# Test file using ESP8266 with K-type temerature sensor (https://www.adafruit.com/product/270)
# 
# Breakout Board: https://www.adafruit.com/product/3263
# Chip Datasheet: https://cdn-learn.adafruit.com/assets/assets/000/035/948/original/MAX31856.pdf
# SPI Tutorial: https://learn.adafruit.com/micropython-hardware-spi-devices?view=all
import machine
import time
import max31856
from max31856 import MAX31856

spi = machine.SPI(1, baudrate=5000000, polarity=0, phase=1)
cs = machine.Pin(15, machine.Pin.OUT)
cs.on()
t = MAX31856(spi, cs)
while True:
    print('Temp: {} C (Junction: {} C)\n'.format(
        t.read_temp_c(),
        t.read_internal_temp_c(),
    ))
    time.sleep_ms(1000)
