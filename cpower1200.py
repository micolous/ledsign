#!/usr/bin/env python
"""
Driver for the C-Power 1200 
Copyright 2010-2012 Michael Farrell <http://micolous.id.au/>

Requires pyserial library in order to interface, and PIL to encode images.

Current windows binaries for PIL are available from here: http://www.lfd.uci.edu/~gohlke/pythonlibs/

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
from time import sleep
from warnings import warn
from cStringIO import StringIO
	

CC_DIVISION = 1
CC_TEXT = 2
CC_IMAGE = 3
CC_STATIC_TEXT = 4
CC_CLOCK = 5
CC_EXIT = 6
CC_SAVE = 7
CC_PLAY_SINGLE = 8
CC_PLAY_DOUBLE = 9
CC_SET_VARIABLE = 10
CC_PLAY_SET_VARIABLE = 11
CC_GLOBAL_DISPLAY_ZONE = 12
CC_PUSH_SET_VARIABLE = 13
CC_SET_TIMER = 14

EFFECT_NONE = 0
EFFECT_OPEN_LEFT = 1
EFFECT_OPEN_RIGHT = 2
EFFECT_OPEN_HORIZ = 3
EFFECT_OPEN_VERT = 4
EFFECT_SHUTTER = 5
EFFECT_MOVE_LEFT = 6
EFFECT_MOVE_RIGHT = 7
EFFECT_MOVE_UP = 8
EFFECT_MOVE_DOWN = 9
EFFECT_SCROLL_UP = 10
EFFECT_SCROLL_LEFT = 11
EFFECT_SCROLL_RIGHT = 12

ALIGN_LEFT = 0
ALIGN_CENTRE = ALIGN_CENTER = 1
ALIGN_RIGHT = 2

# colours
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
PURPLE = 5
CYAN = 6
WHITE = 7

PACKET_TYPE = 0x68
CARD_TYPE = 0x32
PROTOCOL_CODE = 0x7B
CLOCK_PROTOCOL_CODE = 0x47

IMAGE_GIF = 1
IMAGE_GIF_REF = 2
IMAGE_PKG_REF = 3
IMAGE_SIMPLE = 4

SAVE_SAVE = 0
SAVE_RESET = 1

CALENDAR_GREGORIAN = 0
CALENDAR_LUNAR = 1
CALENDAR_CHINESE = 2
CALENDAR_LUNAR_SOLAR = 3

TIMER_INIT = 1
TIMER_RESET = 2
TIMER_START = 3
TIMER_PAUSE = 4
TIMER_SAVE = 5

ZONE_TEXT = 1
ZONE_GIF = 2
ZONE_HINT_TEXT = 6
ZONE_TIMER = 7

class CPowerZone(object):
	# all CPowerZones are subclasses of this.
	
	def serialise(self):
		raise NotImplementedException, '.serialise has not been implemented!'
	

class CPowerTextZone(CPowerZone):
	
	def __init__(self, x, y, w, h, start_var, end_var, stay, font_size, font_invert, font_colour, align):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		
		self.start_var = start_var
		
		self.end_var = end_var
		
		self.stay = stay
		
		self.font_size = font_size
		self.font_invert = font_invert
		self.font_colour = font_colour
		self.align = align
		self.validate()
		
	def validate(self):
		assert 1 <= self.start_var <= 100, 'start_var out of range 1 .. 100'
		assert 1 <= self.end_var <= 100, 'end_var out of range 1 .. 100'

	def serialise(self):
		self.validate()
		
		font = 0
		font |= self.font_size & 0x07
		font |= 0x08 if self.font_invert else 0
		font |= (self.font_colour & 0x07) << 4
		
		packet = struct.pack('<BHHHHBBHBB', self.x, self.y, self.w, self.h, self.start_var, self.end_var, self.stay, font, align)
		
		return packet

		
class CPowerTimerZone(CPowerZone):
	def __init__(self, x, y, w, h, font, show_millis):
		self.x = x


class CPower1200(object):
	"""Implementation of the C-Power 1200 protocol"""
	
	def __init__(self, port, queue=False):
		self.s = serial.Serial(port, 115200)
		self.file_id = None
		self.message_open = False
		#print "opening %s" % self.s.portstr
		self.queue = bool(queue)
		self._queued_packets = []
	
	def begin_queue(self):
		self.queue = True
		self._queued_packets = []
		
	def flush_queue(self, unit_id=0xFF, confirmation=False):
		if not self.queue:
			raise AttributeError, "Cannot flush queue as it is not running in queue mode!"
		
		# FIXME: Queuing does not work correctly.
		
		# grab the current queue and clear it out.
		queued_packets = list(self._queued_packets)
		self._queued_packets = []
		
		# start processing commands.
		
		for i, packet_data in enumerate(queued_packets):
			body = pack('<BBBBBHBB', 
				PACKET_TYPE, CARD_TYPE, unit_id,
				PROTOCOL_CODE, confirmation, len(packet_data),
				i, # packet number
				len(queued_packets) - 1) # total packets - 1
			body += packet_data
			checksum = self.checksum(body)
			msg = "\xA5%s\xAE" % self._escape_data(body + checksum)
			#print repr(msg)
			self.s.write(msg)
			self.s.flush()
		
	
	def _write(self, packet_data, unit_id=0xFF, confirmation=False, protocol_code=PROTOCOL_CODE):
		# start code    A5
		# packet type   68
		# card type     32
		# card ID       XX   or FF == all units
		# protocol code 7B    (or 47 for clock??)
		# confirmation  00 / 01
		# packet length XX XX (uint16 le)
		# packet number XX (uint8)
		# total packets XX (uint8)
		# packet data
		# packet checksum (uint16 le)
		#     sum of each byte from "packet type" to "packet data" content
		
		if len(packet_data) > 0xFFFF:
			raise ValueError, 'Packet too long, packet fragmentation not yet implemented!'
		
		if not (0 <= unit_id <= 255):
			raise ValueError, 'Unit ID out of range (0 - 255)'
		
		if self.queue:
			self._queued_packets.append(packet_data)
			return
			
		confirmation = 0x01 if confirmation else 0x00
		body = pack('<BBBBB', 
			PACKET_TYPE, CARD_TYPE, unit_id,
			protocol_code, confirmation)
		
		if protocol_code == PROTOCOL_CODE:
			# clock packets don't use this.
			body += pack('<HBB',
				len(packet_data),
				0, # packet number
				0) # total packets - 1
		elif protocol_code == CLOCK_PROTOCOL_CODE:
			body += pack('<B',
				0) # 0 == from PC, 1 == from sign
		
		body += packet_data
		checksum = self.checksum(body)
		msg = self._escape_data(body + checksum)
		
		#print '%r' % msg
		#for c in msg:
		#	print '%02x' % ord(c),
		#print ''
		self.s.write("\xA5%s\xAE" % (msg,))
		
		# before another message can be sent, you need to wait a moment
		self.s.flush()
		sleep(.1)
	
	def set_clock(self, new_clock=None):
		# if not specified, value is assumed to be "now"
		# not documented officially!!
		
		if new_clock == None:
			new_clock = datetime.now()
			
		packet = pack('>BBBBBBBB',
			new_clock.second,
			new_clock.minute,
			new_clock.hour,
			new_clock.isoweekday() % 7,
			new_clock.day,
			new_clock.month,
			new_clock.year - 2000,
			0) # unknown
			
		self._write(packet, protocol_code=CLOCK_PROTOCOL_CODE)
		
		
	
	def _escape_data(self, input):
		return input.replace('\xAA', '\xAA\x0A').replace('\xAE', '\xAA\0x0E').replace('\xA5', '\xAA\x05')
		
	def checksum(self, input):
		s = 0
		for c in input:
			s += ord(c)
		
		s &= 0xFFFF
		return pack('<H', s)
		
	def format_text(self, text='', colour=WHITE, size=0):
		"Generate formatted text"
		if not 0x00 < colour < 0x10:
			raise ValueError, "invalid colour"
		
		if not 0x00 <= size <= 0x0F:
			# TODO: Implement this as a transition from a pixel font size
			raise ValueError, "invalid size code"
		
		# colours appear to be as follows:
		#  bit 1: red
		#  bit 2: green (only on green-supporting sign)
		#  bit 3: blue  (only on full-colour sign)
		
		# the "colour / size" code has the high 4 bits as the colour,
		# and the low 4 bits as the size.
		colour_size = chr( (colour << 4) ^ size )
		
		o = ''
		for c in text.encode('ascii'):
			o += colour_size + '\0' + c
		
		return o
		
	def send_text(self, window, formatted_text, effect=EFFECT_SCROLL_LEFT, alignment=ALIGN_LEFT, speed=30, stay_time=2):
		if not 0 <= window <= 7:
			raise ValueError, "invalid window (must be 0 - 7)"
		
		# BIG ENDIAN
		packet = pack('>BBBBBH', CC_TEXT, window, effect, alignment, speed, stay_time) + formatted_text + '\0\0\0'
		
		self._write(packet)
	
	def send_static_text(self, window, text, x=0, y=0, width=64, height=16, speed=30, stay_time=2, alignment=ALIGN_LEFT, font_size=1, red=0, green=0, blue=0):
		if not 0 <= window <= 7:
			raise ValueError, "invalid window (must be 0 - 7)"
			
		# BIG ENDIAN
		packet = pack('>BBBBHHHHBBBB',
			CC_STATIC_TEXT, window,
			1, # simple text data
			alignment, x, y, width, height,
			font_size, red, green, blue) + text + '\0'
		
		# TODO: fix this.
		s._write(packet)
			
			
			
	
	def send_window(self, *windows):
		# TODO: protocol supports sending multiple window definition at once.
		# Make a way to expose this in the API.
		
		# arguments are dicts with the following keys:
		#     x: x-position of window
		#     y: y-position of window
		#     w: width of window
		#     h: height of window
		#
		# arguments are indicated in pixels.
		
		# HERE BE DRAGONS: This function call is BIG ENDIAN.
		# All the others are LITTLE ENDIAN.  Beware.
		packet = pack('>BB', CC_DIVISION, len(windows))
		for window in windows:
			packet += pack('>HHHH', window['x'], window['y'], window['w'], window['h'])
		
		self._write(packet)
	
	def send_image(self, window, image, speed=30, stay_time=2, x=0, y=0):
		"Sends an image to the sign.  Should be a PIL Image object."
		if not 0 <= window <= 7:
			raise ValueError, "invalid window (must be 0 - 7)"
			
		ibuf = StringIO()
		image.convert('I')
		
		# image.save accepts a file-like object. (undocumented)
		image.save(ibuf, 'gif')
		
		# This value is big endian
		packet = pack('>BBBBHBHH',
			CC_IMAGE, window, 
			0, # mode 0 == draw
			speed, stay_time, IMAGE_GIF,
			x, y) + ibuf.getvalue()
		
		# FIXME: doesn't work.
		self._write(packet)
	
	def send_clock(self, window, stay_time=0, calendar=CALENDAR_GREGORIAN, hour_24=True, year_4=True, multiline=True, display_year=True, display_month=True, display_day=True, display_hour=True, display_minute=True, display_second=True, display_week=False, display_pointer=False, font_size=0, red=255, green=255, blue=255, text=''):
		# (so many parameters)
		
		# pack in the format
		format = 0
		format |= 1 if hour_24 else 0
		format |= 2 if not year_4 else 0
		format |= 4 if multiline else 0
		
		format |= 8
		#format |= 16
		#format |= 32
		format |= 128
		
		# pack the display content
		content = 0
		content |= 1 if display_year else 0
		content |= 2 if display_month else 0
		content |= 4 if display_day else 0
		content |= 8 if display_hour else 0
		content |= 16 if display_minute else 0
		content |= 32 if display_second else 0
		content |= 64 if display_week else 0
		content |= 128 if display_pointer else 0
		
		# validate font size
		if not (0 <= font_size <= 7):
			raise ValueError, "font size out of range (0 - 7)"
			
		if not 0 <= window <= 7:
			raise ValueError, "invalid window (must be 0 - 7)"
			
		# This function call is BIG ENDIAN
		packet = pack('>BBHBBBBBBB',
			CC_CLOCK, window, stay_time, calendar,
			format, content, font_size, red, green, blue) + text + '\0'
		
		self._write(packet)
			
	def _set_timer(self, action, property, value, timers=0xFF):
		packet = pack('>BBBBI', CC_SET_TIMER, timers, action, property, value)
		self._write(packet)
	
	def initialise_timer(self, value=0, countdown=False, run_immediate=True, timers=0xFF):
		prop = 0
		prop |= 1 if countdown else 0
		prop |= 2 if run_immediate else 0
		
		# other properties unsupported by this lib, documentation is poor.
		self._set_timer(TIMER_INIT, prop, value, timers)
		
	def reset_timer(self, use_new=False, value=0, run_immediate=True, timers=0xFF):
		prop = 0
		prop |= 1 if use_new else 0
		prop |= 2 if run_immediate else 0
		
		if not use_new:
			# using old value, clear supplied value
			value = 0
		
		self._set_timer(TIMER_RESET, prop, value, timers)
		
	def start_timer(self, timers=0xFF):
		self._set_timer(TIMER_START, 0, 0, timers)
	
	def pause_timer(self, timers=0xFF):
		self._set_timer(TIMER_PAUSE, 0, 0, timers)
	
	def save_timer(self, timers=0xFF):
		self._set_timer(TIMER_SAVE, 0, 0, timers)
		
	def global_display_zone(self, zones):
		pass
	
	#def show_clock
	def save(self):
		packet = pack('>BBH', CC_SAVE, SAVE_SAVE, 0)
		self._write(packet)
	
	def reset(self):
		packet = pack('>BBH', CC_SAVE, SAVE_RESET, 0)
		self._write(packet)
	
	def exit_show(self):
		packet = pack('<B', CC_EXIT)
		self._write(packet)
		
	def close(self):
		self.s.close()

if __name__ == '__main__':
	from sys import argv
	#import Image
	
	s = CPower1200(argv[1])
	#s.begin_queue()
	#s.reset()
	#s.exit_show()
	
	s.set_clock()

	# define two windows, one at the top and one at the bottom.
	s.send_window(dict(x=0, y=0, h=16, w=64))#, dict(x=0, y=8, h=8, w=64))
	
	#s.send_window(1, 0, 8, 64, 8)
	#txt = s.format_text('Hello', RED, 0) + s.format_text(' World!', GREEN, 0)
	#s.send_text(0, txt)
	#s.send_static_text(0, 'Hello World!')
	#img = Image.open('test.png')
	#s.send_image(0, img)
	
	s.send_clock(0, calendar=CALENDAR_GREGORIAN, multiline=True)
	
	#s.exit_show()
	#s.flush_queue()
	s.save()
	
