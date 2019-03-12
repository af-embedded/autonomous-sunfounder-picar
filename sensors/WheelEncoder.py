import RPi.GPIO as GPIO
import math

class WheelEncoder:
	def __init__(self, pin, wheel_diameter_metres, ticks_per_revolution=192):
		self._ticks_per_revolution = ticks_per_revolution
		self._wheel_diameter = wheel_diameter_metres
		self._distance_per_tick = math.pi * self._wheel_diameter / self._ticks_per_revolution
		
		self.ticks = 0
		self.distance = 0.0
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(pin, GPIO.RISING, callback=_encoder_tick)
		
	def _encoder_tick(self):
		self.ticks += 1
		self.distance += self._distance_per_tick
			
	def get_ticks(self):
		return self.ticks
		
	def clear(self):
		self.ticks = 0
		self.distance = 0
		
	def get_distance(self):
		return self.distance
