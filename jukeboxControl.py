import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import os

from neopixel import *

# LED strip configuration:
LED_COUNT      = 144     # Number of LED pixels.
LED_PIN        = 13      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

# ADC configuration:
CLK  = 17	# Clock pin
MISO = 27	# MISO pin
MOSI = 6	# MOSI pin
CS   = 26	# CS pin
adc = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)	# Intialize the ADC

# Global music settings
volume = 50
bass = 50
treble = 50

class MainControl():
	global ledMain, adc
	def __init__(self, volume, bass, treble):
		self.volume = volume
		self.bass = bass
		self.treble = treble

	def run(self):
		print("Main thread begun")
		leds = LedControl(self.volume, self.bass, self.treble)
		while True:
			newVolume = self.read_volume()
			if (newVolume < self.volume - 3) or (newVolume > self.volume + 3):
				#The volume knob has been changed so we change the volume through alsa.
				os.system("amixer set Master "+str(newVolume)+"%")
				leds.volume_led(newVolume, self.volume)
				self.volume = newVolume
				print("Volume set to "+str(self.volume))
				time.sleep(0.1)

			#print("Volume: "+ str(read_volume()))
			#print("Bass: "+ str(read_bass()))
			#print("Treble: "+ str(read_treble()))

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

class LedControl():
	red = Color(255, 0, 0)
	green = Color(0, 255, 0)
	blue = Color(0, 0, 255)
	black = Color(0,0,0)
	global volume, bass, treble

	def __init__(self, volumeNumber, bassNumber, trebleNumber):
		self.volumeNumber = round(volume*34/100)
		self.bassNumber = round(bass*34/100)
		self.trebleNumber = round(treble*34/100)
		# Create NeoPixel object with appropriate configuration.
		self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
 	   	# Intialize the library (must be called once before other functions).
		self.strip.begin()

	def volume_led(self, percent, currentVolume):
		print("changing leds for volume")
		newVolume = self.convert_led_number(percent)
		currentVolume = self.convert_led_number(currentVolume)
		self.wipe_led_strip()
		if newVolume < currentVolume:
			#paint right pixels black
			i = 95
			while i > 95 - newVolume:
				self.strip.setPixelColor(i-newVolume, self.black)
				print(i)
				i -= 1
			self.strip.show()
			print("changing leds for volume black")
		else:
			#paint right pixels colour
			i = 95
			while i > 95 - newVolume:
				self.strip.setPixelColor(i, self.red)
				i -= 1
			self.strip.show()
			print("changing leds for volume red")

	def convert_led_number(self, percent):
		numOfLeds = 34
		return round(percent*numOfLeds/100)

	def wipe_led_strip(self):
		for i in range(self.strip.numPixels()):
			self.strip.setPixelColor(i, self.black)
		self.strip.show()

	def wipe_led_levels(self):
		i = 61
		while i < 95:
			self.strip.setPixelColor(i, self.black)
			i += 1
		self.strip.show()

try:
	print("got to here")
	main = MainControl(volume, bass, treble)
	print("got to here")
	main.run()
	print("got to here")
except KeyboardInterrupt:
	print "Closing"
