#!/usr/bin/env python
"""
Driver for the NewSign/Y5207 protocol
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
from datetime import datetime

# Both open and close effects
EFFECT_IMMEDIATE = 'FA'
EFFECT_XOPEN = 'FB'
EFFECT_CURTAIN_UP = 'FC'
EFFECT_CURTAIN_DOWN = 'FD'
EFFECT_SCROLL_LEFT = 'FE'
EFFECT_SCROLL_RIGHT = 'FF'
EFFECT_VOPEN = 'FG'
EFFECT_VCLOSE = 'FH'
EFFECT_SCROLL_UP = 'FI'
EFFECT_SCROLL_DOWN = 'FJ'
EFFECT_HOLD = 'FK'

# Only opening effect
EFFECT_SNOW = 'FL'
EFFECT_TWINKLE = 'FM'
EFFECT_BLOCKMOVE = 'FN'
EFFECT_RANDOM = 'FP'

OPEN_EFFECTS = (
	EFFECT_IMMEDIATE,
	EFFECT_XOPEN,
	EFFECT_CURTAIN_UP,
	EFFECT_CURTAIN_DOWN,
	EFFECT_SCROLL_LEFT,
	EFFECT_SCROLL_RIGHT,
	EFFECT_VOPEN,
	EFFECT_VCLOSE,
	EFFECT_SCROLL_UP,
	EFFECT_SCROLL_DOWN,
	EFFECT_HOLD,

	EFFECT_SNOW,
	EFFECT_TWINKLE,
	EFFECT_BLOCKMOVE,
	EFFECT_RANDOM
)

CLOSING_EFFECTS = (
	EFFECT_IMMEDIATE,
	EFFECT_XOPEN,
	EFFECT_CURTAIN_UP,
	EFFECT_CURTAIN_DOWN,
	EFFECT_SCROLL_LEFT,
	EFFECT_SCROLL_RIGHT,
	EFFECT_VOPEN,
	EFFECT_VCLOSE,
	EFFECT_SCROLL_UP,
	EFFECT_SCROLL_DOWN,
	EFFECT_HOLD
)

MOVESPEED_MIN = 0
MOVESPEED_MAX = 3

DISPLAYTIME_MIN = 0
DISPLAYTIME_MAX = 25


class LEDSign:
	"""Implementation of the NewSign / Y5207 protocol"""
	def __init__(self, port, signid = "00"):
		self.s = serial.Serial(port)
		self.signid = signid
		print "opening %s" % self.s.portstr

	def write(self, msg):
		self.s.write("<ID%s>%s" % (self.signid, msg))
		checksum = 0
		for c in msg:
			checksum = (checksum ^ ord(c)) % 256

		self.s.write("%02X<E>" % checksum)

	def begin_textlines(self):
		self.write("<BE>")

	def end_textlines(self):
		self.write("<BF>")

	def set_brightness(self, level):
		assert level >= 0.25, "brightness must be at least 0.25"
		assert level <= 1.00, "brightness must be less than 1.0"

		level = int(level * 4)

		if level == 1: # 25%
			self.write("<BD>")
		elif level == 2: # 50%
			self.write("<BC>")
		elif level == 3:
			self.write("<BB>")
		elif level == 4:
			self.write("<BA>")

	def set_clock(self, n = None):
		if n == None:
			n = datetime.now()
		self.write(("<SC>" + ("%02d"*7)) % (n.year%100, n.isoweekday(), n.month, n.day, n.hour, n.minute, n.second))

	def __validate_pageid(self, pageid):
		if isinstance(pageid,int):
			pageid = chr(ord('A')+pageid)
	
		pageid = str(pageid).upper()
		if len(pageid) != 1:
			raise Exception, "pageid is not one character"
		if ord(pageid) < ord("A") or ord(pageid) > ord("Z"):
			raise Exception, "pageid must be a letter between A and Z, or a number between 0 and 25"

		return pageid

	def set_page(self, pageid, openeffect, movespeed, displaytime, closingeffect, msg):
		pageid = self.__validate_pageid(pageid)
			
		openeffect = openeffect.upper()
		if openeffect not in OPEN_EFFECTS:
			raise Exception, "not a valid opening effect"

		movespeed = int(movespeed)
		if movespeed < MOVESPEED_MIN or movespeed > MOVESPEED_MAX:
			raise Exception, "move speed is outside of bounds"

		displaytime = int(displaytime)
		if displaytime < DISPLAYTIME_MIN or displaytime > DISPLAYTIME_MAX:
			raise Exception, "display time is outside of bounds"

		closingeffect = closingeffect.upper()
		if closingeffect not in CLOSING_EFFECTS:
			raise Exception, "not a valid closing effect"

		if movespeed == 0:
			movespeed = "q"
		elif movespeed == 1:
			movespeed = "a"
		elif movespeed == 2:
			movespeed = "Q"
		elif movespeed == 3:
			movespeed = "A"
		else:
			raise Exception, "invalid movespeed"

		displaytime = chr(displaytime + ord('A'))

		msg = msg.replace("\n", "").replace("\r", "")
		
		self.write("<L1><P%s><%s><M%s><W%s><%s>%s" % (pageid, openeffect, movespeed, displaytime, closingeffect, msg))

	def display_page(self, pageid):
		pageid = self.__validate_pageid(pageid)

		self.write("<RP>P%s" % pageid)
	
	def playlist(self, page_order):
		page_order_clean = ['']
		for p in page_order:
			page_order_clean.append(self.__validate_pageid(p))
		page_order = ''.join(page_order_clean)

		self.write("<TA>00010100009912302359" + page_order)
		
