#!/usr/bin/env python
"""
RSS Reader for C-Power 1200 
Copyright 2010-2012 Michael Farrell <http://micolous.id.au/>

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

from cpower1200 import *
import feedparser
from sys import argv

FEED = 'http://news.google.com.au/news?pz=1&cf=all&ned=au&hl=en&output=rss'

d = feedparser.parse(FEED)
s = CPower1200(argv[1])

# Define one window at the top of the screen, and one in the lower part of the screen
s.send_window(dict(x=0, y=0, h=8, w=64), dict(x=0, y=8, h=8, w=64))

header = s.format_text(d.feed.title, RED, 0)
articles = ''

for i, article in enumerate(d.entries[:4]):
	print "entry %d: %s" % (i, article.title)
	colour = YELLOW if i % 2 == 0 else GREEN
	articles += s.format_text(article.title + ' ', colour)

# send to sign
#s.send_text(0, header, effect=EFFECT_NONE)
s.send_clock(0, display_year=False, display_month=False, display_day=False, display_hour=True, display_minute=True, display_second=True, multiline=False, red=255,green=0,blue=0)
s.send_text(1, articles, speed=10)
