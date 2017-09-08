import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import os
import random
from subprocess import DEVNULL, STDOUT, check_call
import json

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
		self.oldVolume = volume
		self.bass = bass
		self.treble = treble
		self.ledState = 'start'
		self.ledTimer = 0;
		self.leds = LedControl(self.volume, self.bass, self.treble)

	def run(self):
		print("Main thread begun")
		# Startup sequance
		self.leds.rainbow_leds()
		self.leds.wipe_led_strip()
		while True:
			newVolume = self.read_volume()
			if (newVolume < self.volume - 4) or (newVolume > self.volume + 4):
				#The volume knob has been changed so we change the volume through alsa.
				os.system("amixer set Master "+str(newVolume)+"%")
				self.ledState = 'volume change'
				self.oldVolume = self.volume # store old volume for leds
				self.volume = newVolume
				print("Volume set to "+str(self.volume))

			# LED state conditions
			if self.ledState == 'start':
				#No knobs have changed so we can set playing behavour
				self.leds.rainbow_leds()
				self.leds.wipe_led_strip()
				self.ledState = self.leds.check_next_state(self.ledTimer)
			elif self.ledState == 'playing':
				# Music is playing and so are LED's
				self.leds.playing_leds()
				self.ledState = self.leds.check_next_state(self.ledTimer)
			elif self.ledState == 'paused':
				# Music is paused so LED's are still
				self.leds.paused_leds()
				self.ledState = self.leds.check_next_state(self.ledTimer)
			elif self.ledState == 'volume change':
				if self.leds.get_first_change() == True:
					self.leds.wipe_led_strip()
					self.leds.set_first_change(False)
					self.leds.repaint_volume(self.volume)
				self.leds.volume_led(self.volume, self.oldVolume)
				self.ledTimer = int(time.time())
				self.ledState = self.leds.check_next_state(self.ledTimer)
			else:
				self.ledState = self.leds.check_next_state(self.ledTimer)

			# print(self.ledState)
			# Sleep timer
			time.sleep(0.1)

	def close(self):
		self.leds.wipe_led_strip()

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
	white = Color(255,255,255)
	black = Color(0,0,0)
	lastColorNumber = 0;
	global volume, bass, treble

	def __init__(self, volumeNumber, bassNumber, trebleNumber):
		self.volumeNumber = round(volume*34/100)
		self.bassNumber = round(bass*34/100)
		self.trebleNumber = round(treble*34/100)
		self.firstChange = True
		# Create NeoPixel object with appropriate configuration.
		self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
 	   	# Intialize the library (must be called once before other functions).
		self.strip.begin()

	def get_first_change(self):
		return self.firstChange

	def set_first_change(self, change):
		self.firstChange = change

	def repaint_volume(self, currentVolume):
		currentVolume = self.convert_led_number(currentVolume)
		i = 95
		while i > 95 - currentVolume:
			self.strip.setPixelColor(i, self.red)
			i -= 1
		self.strip.show()

	def volume_led(self, percent, currentVolume):
		newVolume = self.convert_led_number(percent)
		currentVolume = self.convert_led_number(currentVolume)

		if newVolume < currentVolume:
			#paint right pixels black
			newVolume = 34 - newVolume
			i = 61
			while i < 61 + newVolume:
				self.strip.setPixelColor(i, self.black)
				i += 1
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

	# Get a color from the color wheel. (not white or black)
	def wheel(self, pos):
		if pos < 85:
			return Color(pos*3,255-pos*3,0)
		elif pos < 170:
			pos -= 85
			return Color(255-pos*3,0,pos*3)
		else:
			pos -= 170
			return Color(0,pos*3,255-pos*3)

	def rainbow_leds(self):
		for j in range(256*5):
			for i in range(self.strip.numPixels()):
				self.strip.setPixelColor(i, self.wheel((int(i*256/self.strip.numPixels())+j) & 255))
			self.strip.show()

	def playing_leds(self):
		for i in range(self.strip.numPixels()):
			self.strip.setPixelColor(i, self.wheel(self.lastColorNumber))
		self.strip.show()
		if self.lastColorNumber == 255:
			self.lastColorNumber = 0
		else:
			self.lastColorNumber += 1

	def paused_leds(self):
		for i in range(self.strip.numPixels()):
			self.strip.setPixelColor(i, self.white)
		self.strip.show()

	def random_255(self):
		return random.randint(0, 255)

	def check_playing(self):
		result = str(check_call(['curl', '-d', '\'{"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_state"}\'', 'http://localhost:6680/mopidy/rpc'], stdout=DEVNULL))
		if 'paused' in result:
			print("Stopped")
			return False
		elif 'playing' in result:
			print("Playing")
			return True
		print(result)
		return False

	def check_next_state(self, setTime):
		if int(time.time())-5 < setTime:
			return 'null'
		if self.check_playing() == True:
			self.firstChange = True
			return 'playing'
		else:
			# firstChange set to true to prepare for next change
			self.firstChange = True
			return 'playing'

try:
	print("got to here")
	main = MainControl(volume, bass, treble)
	print("got to here")
	main.run()
	print("got to here")
except KeyboardInterrupt:
	main.close()
	print("Closing")
