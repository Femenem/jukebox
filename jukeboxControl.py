import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import os
import apa102

CLK  = 17
MISO = 27
MOSI = 6
CS   = 26
adc = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

volume = 50
bass = 50
treble = 50

def read_volume():
	number = adc.read_adc(1)
	number = round(number/10.24)
	return int(number)

def read_bass():
	number = adc.read_adc(0)
	number = round(number/10.24)
	return int(number)
	
def read_treble():
	number = adc.read_adc(2)
	number = round(number/10.24)
	return int(number)

def main():
	global volume, bass, treble
	while True:
		newVolume = read_volume()
		if (newVolume < volume - 1) or (newVolume > volume + 1):
			#The volume knob has been changed so we change the volume through alsa.
			os.system("amixer set Master "+str(newVolume)+"%")
			volume = newVolume
			print("Volume set to "+str(volume))
		
		
		
		#print("Volume: "+ str(read_volume()))
		#print("Bass: "+ str(read_bass()))
		#print("Treble: "+ str(read_treble()))
		#time.sleep(0.1)

main()
