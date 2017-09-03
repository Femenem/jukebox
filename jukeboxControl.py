import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import os
import threading

from neopixel import *

# LED strip configuration:
LED_COUNT      = 144      # Number of LED pixels.
LED_PIN        = 13      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

CLK  = 17
MISO = 27
MOSI = 6
CS   = 26
adc = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

volume = 50
bass = 50
treble = 50

class MainControl(threading.Thread):
	global ledMain
	def __init__(self, volume, bass, treble):
		threading.Thread.__init__(self)
		self.volume = volume
		self.bass = bass
		self.treble = treble

	def run(self):
		print("Main thread begun")
		while True:
			newVolume = self.read_volume()
			if (newVolume < volume - 2) or (newVolume > volume + 2):
				#The volume knob has been changed so we change the volume through alsa.
				os.system("amixer set Master "+str(newVolume)+"%")
				volume = newVolume
				ledMain.volume_led(volume)

				print("Volume set to "+str(volume))

			#print("Volume: "+ str(read_volume()))
			#print("Bass: "+ str(read_bass()))
			#print("Treble: "+ str(read_treble()))
			time.sleep(0.1)

	def read_volume(self):
		number = adc.read_adc(1)
		number = round(number/10.24)
		return int(number)

	def read_bass(self):
		number = adc.read_adc(0)
		number = round(number/10.24)
		return int(number)

	def read_treble(self):
		number = adc.read_adc(2)
		number = round(number/10.24)
		return int(number)

class LedControl(threading.Thread):
	red = Color(255, 0, 0)
	green = Color(0, 255, 0)
	blue = Color(0, 0, 255)
	black = Color(0,0,0)
	global volume, bass, treble

	def __init__(self, volumeNumber, bassNumber, trebleNumber):
		threading.Thread.__init__(self)
		self.volumeNumber = round(volume*34/100)
		self.bassNumber = round(bass*34/100)
		self.trebleNumber = round(treble*34/100)
		# Create NeoPixel object with appropriate configuration.
		self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
 	   	# Intialize the library (must be called once before other functions).

	def run(self):
		print("Led thread begun")
		self.strip.begin()

	def volume_led(percent):
		newVolume = convert_led_number(percent)
		wipe_led_strip()
		if newVolume < self.volumeNumber:
			#paint right pixels black
			i = 61
			while i < i + newVolume:
				strip.setPixelColor(i, black)
				i += 1
			strip.show()
		else:
			#paint right pixels colour
			i = 61
			while i < i + newVolume:
				strip.setPixelColor(i, red)
				i += 1
			strip.show()

	def convert_led_number(percent):
		numOfLeds = 34
		return round(percent*numOfLeds/100)

	def wipe_led_strip(strip):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, black)
		strip.show()

	def wipe_led_levels(strip):
		i = 61
		while i < 95:
			strip.setPixelColor(i, black)
			i += 1
		strip.show()


print("got to here")
main = MainControl(volume, bass, treble)
ledMain = LedControl(volume, bass, treble)
print("got to here")
main.start()
ledMain.start()
print("got to here")
