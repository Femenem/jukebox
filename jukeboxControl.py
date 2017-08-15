import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

CLK  = 17
MISO = 27
MOSI = 6
CS   = 26
adc = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

while True:
    adc.read_adc(0)
    time.sleep(0.5)
