#!/usr/bin/env python
from cpower1200 import *
from argparse import ArgumentParser
from time import sleep
import requests
from json import dumps, loads
from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS
from twisted.python import log
import sys


class SagedClientProtocol(WebSocketClientProtocol):
	def onOpen(self):
		self.getLightingStates()
		
	def getLightingStates(self):
		self.sendMethod('get_light_states', self.toilet_ga)
	
	def sendMethod(self, cmd, *args):
		print 'sendMethod(%r, %r)' % (cmd, args)
		self.sendMessage(dumps(dict(cmd=cmd, args=args)))
		
	def onMessage(self, msg, binary):
		print 'onMessage:', msg
		# decode message
		msg = loads(msg)
		
		print 'onMessage json:', msg
		if msg['cmd'] == 'light_states':
			reactor.callLater(1, self.onLightStates, msg['args'][0])
		elif msg['cmd'] == 'lighting_group_on':
			if self.toilet_ga in msg['args'][1]:
				reactor.callLater(1, self.toiletOn)
		elif msg['cmd'] == 'lighting_group_off':
			if self.toilet_ga in msg['args'][1]:
				reactor.callLater(1, self.toiletOff)
	
	def onLightStates(self, states):
		# states has keys of unicodes, so convert sensor GA to unicode
		utga = unicode(self.toilet_ga)
		
		if utga in states:
			# handle toilet ga
			if states[utga] == 0.0:
				# current state is off
				self.toiletOff()
			else:
				self.toiletOn()
		
	def toiletOn(self):
		print "TOILET SIGN OCCUPIED"
		self.sign.send_text(0, self.sign.format_text('#OccupyToilet', RED, 0))
	
	def toiletOff(self):
		print "UNOCCUPIED"
		self.sign.send_clock(0, calendar=CALENDAR_GREGORIAN, multiline=False, display_year=False, display_hour=False, display_minute=False, display_second=False)
		
		

def xbmc_api_request(server, method, auth=None, **kwargs):
	p = dict(jsonrpc='2.0', method=method, id=1)
	if len(kwargs) > 0:
		p['params'] = kwargs
	
	r = requests.post(server + '/jsonrpc', auth=auth, data=dumps(p), headers={'Content-Type': 'application/json'}, timeout=3)
	result = r.json()
	# TODO: implement error handler
	
	return result
	

def get_xbmc_current_playing(server, auth=None):
	active_players = xbmc_api_request(server, 'Player.GetActivePlayers', auth)['result']
	
	for player in active_players:
		if str(player['type']) not in ('video', 'audio'):
			continue
			
		# is a video or audio player, get info
		player_info = xbmc_api_request(server, 'Player.GetItem', auth, playerid=player['playerid'], properties=['title', 'artist'])
		
		return player_info['result']['item']['label']

def loop(xbmc_uri, auth, s, last_playing=None, use_reactor=False):
	print 'loop(%r, %r, %r, %r, %r)' % (xbmc_uri, auth, s, last_playing, use_reactor)
	try:
		playing = get_xbmc_current_playing(xbmc_uri, auth).encode('ascii', 'ignore')
	except:
		print 'error getting xbmc data'
		playing = None
	
	#print repr(playing)
	#print repr(last_playing)
	#print 
	
	if playing != last_playing:
		if playing == None:
			playing_f = s.format_text('', RED, 0)
		else:
			playing_f = s.format_text(playing, GREEN, 0)
			
		s.send_text(2, playing_f, speed=15)
	s.set_clock()
	
	#s.send_text(0, s.format_text('LOO', RED, 0))
	
	last_playing = playing
	sleep(3.)
	if use_reactor:
		reactor.callInThread(loop, xbmc_uri, auth, s, last_playing, True)
		

def main(serial_port, xbmc_uri, xbmc_un, xbmc_pw, saged_uri=None, toilet_ga=None):
	print 'main(%r, %r, %r, %r, %r, %r)' % (serial_port, xbmc_uri, xbmc_un, xbmc_pw, saged_uri, toilet_ga)
	if not isinstance(serial_port, CPower1200):
		s = CPower1200(serial_port)
		s.send_window(
			dict(x=0 , y=0, h=8, w=32), # window 0: top left: time
			dict(x=32, y=0, h=8, w=32), # window 1: top right: date
			dict(x=0 , y=8, h=8, w=64)  # window 2: bottom: nowplaying
		)
		s.send_clock(0, calendar=CALENDAR_GREGORIAN, multiline=False, display_year=False, display_hour=False, display_minute=False, display_second=False)
		s.send_clock(1, calendar=CALENDAR_GREGORIAN, multiline=False, display_year=False, display_month=False, display_day=False, display_second=False)
	else:
		s = serial_port
	
	if saged_uri != None:
		factory = WebSocketClientFactory(saged_uri, debug=True)
		factory.protocol = SagedClientProtocol
		factory.protocol.toilet_ga = toilet_ga # unicode(toilet_ga)
		factory.protocol.sign = s
		#factory.setProtocolOptions(allowHixie76=True)
		#reactor.callLater(1, main, s, xbmc_uri, xbmc_un, xbmc_pw)
		connectWS(factory)
		#reactor.run()

	if xbmc_un != None and xbmc_pw != None:
		auth = (xbmc_un, xbmc_pw)
	else:
		auth = None
	
	last_playing = False
	
	if saged_uri == None:
		while 1:
			loop()
	else:
		reactor.callInThread(loop, xbmc_uri, auth, s, last_playing, True)
		reactor.run()


if __name__ == '__main__':
	parser = ArgumentParser()
	
	parser.add_argument('-s', '--serial-port',
		dest='serial_port',
		default='/dev/ttyUSB0',
		help='Serial port where the CPower1200 unit is attached [default: %(default)s]'
	)
	
	parser.add_argument('-x', '--xbmc-uri',
		dest='xbmc_uri',
		help='XBMC URI in form: http://192.168.1.3:8080',
		required=True
	)
	
	parser.add_argument('-u', '--xbmc-username',
		dest='xbmc_un',
		help='XBMC username',
		default=None
	)
	
	parser.add_argument('-p', '--xbmc-password',
		dest='xbmc_pw',
		help='XBMC password',
		default=None
	)
	
	parser.add_argument('-S', '--saged-uri',
		dest='saged_uri',
		help='URI where saged is running, eg: ws://server:8080/saged'
	)
	
	parser.add_argument('-T', '--toilet_ga',
		dest='toilet_ga',
		type=int,
		default=25,
		help='Toilet sensor group address [default: %(default)s]'
	)
	
	options = parser.parse_args()
	log.startLogging(sys.stdout)
	
	main(options.serial_port, options.xbmc_uri, options.xbmc_un, options.xbmc_pw, options.saged_uri, options.toilet_ga)
