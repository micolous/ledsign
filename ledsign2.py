#!/usr/bin/env python
"""
Driver for the Bestlink Optoelectronics M500N-7X80RG2
Copyright 2010 Michael Farrell <http://micolous.id.au/>

Requires pyserial library in order to interface.


This library is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import serial, string
from datetime import datetime, time
from struct import pack

# Both open and close effects
# cycle through all effects
EFFECT_CYCLIC = 1
EFFECT_IMMEDIATE = 2
EFFECT_SCROLL_LEFT = 3
EFFECT_SCROLL_RIGHT = 4
EFFECT_SPLIT_OPEN = 5
EFFECT_SPLIT_CLOSE = 6
EFFECT_WIPE_OUT = 7
EFFECT_WIPE_LEFT = 8
EFFECT_WIPE_RIGHT = 9
EFFECT_WIPE_IN = 10
EFFECT_SCROLL_UP = 11
EFFECT_SCROLL_DOWN = 12
EFFECT_SPLIT_INTERLACED = 13
EFFECT_WIPE_INTERLACED = 14
EFFECT_WIPE_UP = 15
EFFECT_WIPE_DOWN = 16
EFFECT_WIPE_LINE = 17
EFFECT_EXPLODE = 18
EFFECT_PACMAN = 19
EFFECT_FALLING_LINES = 20
EFFECT_SHOOT = 21
EFFECT_BLINK = 22
EFFECT_DISSOLVE = 23
EFFECT_SLIDE_LETTERS = 24

SYMBOL_STARBURST = '\x60'
SYMBOL_SNAKE = '\x61'
SYMBOL_UMBRELLA = '\x62'
SYMBOL_CLOCK = '\x63'
SYMBOL_TELEPHONE = '\x64'
SYMBOL_GLASSES = '\x65'
SYMBOL_TAP = '\x66'
SYMBOL_ROCKET = '\x67'
SYMBOL_CRAB = '\x68'
SYMBOL_KEY = '\x69'
SYMBOL_SHIRT = '\x6A'
SYMBOL_HELECOPTER = '\x6B'
SYMBOL_CAR = '\x6C'
SYMBOL_TANK = '\x6D'
SYMBOL_HOUSE = '\x6E'
SYMBOL_LANTERN = '\x6F'
SYMBOL_TREES = '\x70'
SYMBOL_DUCK = '\x71'
SYMBOL_SCOOTER = '\x72'
SYMBOL_BIKE = '\x73'
SYMBOL_CROWN = '\x74'
SYMBOL_BUTTERFLY = '\x75'
SYMBOL_RIGHT = '\x76'
SYMBOL_LEFT = '\x77'
SYMBOL_DOWN_LEFT = '\x78'
SYMBOL_UP_LEFT = '\x79'
SYMBOL_CUP = '\x7A'
SYMBOL_CHAIR = '\x7B'
SYMBOL_SHOE = '\x7C'
SYMBOL_MARTINI = '\x7D'

SPECIAL_TIME = '\x80'
SPECIAL_DATE = '\x81'

# requires the larger version of the sign to display properly
# still exists in the small version.
ANIMATION_MERRY_XMAS = '\x90'
ANIMATION_HAPPY_NEW_YEAR = '\x91'
ANIMATION_4TH_JULY = '\x92'
ANIMATION_HAPPY_EASTER = '\x93'
ANIMATION_HAPPY_HALLOWEEN = '\x94'
ANIMATION_DONT_DRINK_DRIVE = '\x95'
ANIMATION_NO_SMOKING = '\x96'
ANIMATION_WELCOME = '\x97'
# extra undocumented copy of the graphics here, \x98 - \x9F

FONT_5x5 = '\xA0'
FONT_10x5 = '\xA1'
FONT_5x7 = '\xA2'
FONT_10x7 = '\xA3'
FONT_8x7 = '\xA4'
FONT_16x7 = '\xA5'
FONT_SMALL_FONTS = '\xA6'
# broken extra fonts
FONT_3x7 = '\xAC'

COLOUR_BRIGHT_RED = '\xB0'
COLOUR_DIM_RED = '\xB1'
# additional colours for M500N-7X80RG2 (Red/Green 2-LED version)
# thanks to Martin Hill <martin at eshock.com>
COLOUR_AMBER = '\xB2'
COLOUR_YELLOW = '\xB3'
COLOUR_DIM_ORANGE = '\xB4'
COLOUR_BRIGHT_ORANGE = '\xB5'
COLOUR_DIM_GREEN = '\xB6'
COLOUR_BRIGHT_GREEN = '\xB7'
COLOUR_RAINBOW1 = '\xB8'
COLOUR_RAINBOW2 = '\xBA'
COLOUR_RAINBOW3 = '\xBB'
COLOUR_RAINBOW4 = '\xBC'
COLOUR_RAINBOW5 = '\xBD'
COLOUR_RAINBOW6 = '\xBE'
COLOUR_RAINBOW7 = '\xBF'

# fastest speed is 1, slowest is 8
SPEED_1 = '\xC0'
SPEED_2 = '\xC1'
SPEED_3 = '\xC2'
SPEED_4 = '\xC3'
SPEED_5 = '\xC4'
SPEED_6 = '\xC5'
SPEED_7 = '\xC6'
SPEED_8 = '\xC7'

# fastest pause time is 1, slowest is 8
PAUSE_1 = '\xC8'
PAUSE_2 = '\xC9'
PAUSE_3 = '\xCA'
PAUSE_4 = '\xCB'
PAUSE_5 = '\xCC'
PAUSE_6 = '\xCD'
PAUSE_7 = '\xCE'
PAUSE_8 = '\xCF'

GRAPHIC_CUSTOM_1 =  '\xD0'
GRAPHIC_CUSTOM_2 =  '\xD1'
GRAPHIC_CUSTOM_3 =  '\xD2'
GRAPHIC_CUSTOM_4 =  '\xD3'
GRAPHIC_CUSTOM_5 =  '\xD4'
GRAPHIC_CUSTOM_6 =  '\xD5'
GRAPHIC_CUSTOM_7 =  '\xD6'
GRAPHIC_CUSTOM_8 =  '\xD7'
GRAPHIC_TRAINS =    '\xD8'
GRAPHIC_CARS =      '\xD9'
GRAPHIC_TEACUPS =   '\xDA'
GRAPHIC_TELEPHONE = '\xDB'
GRAPHIC_BEACH =     '\xDC'
GRAPHIC_SHIP =      '\xDD'
#GRAPHIC_ =         '\xDE' # not sure what this is supposed to be
GRAPHIC_MOUSE =     '\xDF'

SOUND_BEEP_3 = '\xE0'
SOUND_BEEP_5 = '\xE1'
SOUND_BEEP_1 = '\xE2'

class LEDSign:
	"""Implementation of the XC0193 protocol"""
	def __init__(self, port):
		self.s = serial.Serial(port, 2400)
		self.file_id = None
		self.message_open = False
		print "opening %s" % self.s.portstr

	def write(self, msg):
		self.s.write("%s\xFF" % (msg,))

	def begin_message(self, sign=range(1,129), reset=False):
		"""Begins a message for a sign.  defaults to all signs."""
		if self.message_open:
			raise Exception, "A message is already open"
			
		for x in sign:
			if x < 1 or x > 128:
				raise Exception, "cannot send to sign ID outside of range 1-128, you sent to sign %s" % x
				
		# this is a special thing, doesn't have the \xFF terminator
		# start programming the sign, do not reset memory
		self.s.write("\x00\xFF\xFF")
		if reset:
			self.s.write("\x01")
		else:
			self.s.write("\x00")
		
		# data is for sign list
		self.s.write("\x0B")
		for x in sign:
			self.s.write(chr(x))
		self.s.write('\xFF')
		
		
		self.message_open = True
	
	def add_run_mode(self, mode=1):
		if mode < 0 or mode > 24:
			raise Exception, "run mode must be 0-24"
		
		self.s.write(chr(mode))
		
	def add_text(self, msg):
		msg = str(msg)
		for x in msg:
			y = ord(x)
			if y < 32 or y > 237:
				raise Exception, "You shouldn't be using the character %s (#%s)." % (x, ord(x))
		self.s.write(msg)
	
	def add_special(self, special):
		self.s.write("\xEF" + special)
	
	def end_frame(self):
		self.s.write('\xff')
		
	
	def end_message(self):
		if not self.message_open:
			raise Exception, "A message isn't open"
		# this is a special thing, doesn't have the \xFF terminator
		self.s.write("\x00")
		self.message_open = False


	def set_clock(self, n = datetime.now(), hour24=True):
		if self.file_id != None:
			raise Exception, "Cannot set clock while a file is open"
		if hour24:
			hour24 = "\x00"
		else:
			hour24 = "\x01"
		self.write(("\x08%s%s" + ("%02d"*6)) % (pack("!B", n.isoweekday()%7), hour24, n.year%100, n.month, n.day, n.hour, n.minute, n.second))
		
	def begin_file(self, file_id):
		if self.file_id != None:
			raise Exception, "A file, %s, is already open" % self.file_id
		file_id = int(file_id)
		if file_id < 0 or file_id > 99:
			raise Exception, "file_id must be between 0 and 99."
			
		self.s.write("\x01%02d" % file_id)
		self.file_id = file_id
	
	def end_file(self):
		if self.file_id == None:
			raise Exception, "No file is open"
		self.write("\xFF")
		self.file_id = None
	
	
		
		

	def display_page(self, pageid):
		pass
	
	def playlist(self, page_order):
		pass
		
