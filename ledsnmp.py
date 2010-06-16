#!/usr/bin/env python
from snmptraffic import snmpgetout
from ledsign import *
from time import sleep, time
from threading import Thread
import urllib2
from getpass import getpass
from urllib import urlencode

dataStore = {}
lastData = {}
OVERFLOW_VALUE = (2L**32L)-1L
sign = LEDSign('/dev/ttyUSB0')
passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
passwd = getpass("Enter password for SAGAPresenter: ")
passwd_mgr.add_password(None, "http://morbo:8001", "ledsnmp", passwd)
handler = urllib2.HTTPBasicAuthHandler(passwd_mgr)
opener = urllib2.build_opener(handler)

class FunctionThreader(Thread):
	def __init__(self, function, args=[], kwargs={}):
		Thread.__init__(self)
		self.function = function
		self.args = args
		self.kwargs = kwargs

	def run(self):
		self.function(*self.args, **self.kwargs)

def getSwitchData(ip, ports):
	global dataStore
	
	try:
		newData = snmpgetout(ip, 'public', '1.3.6.1.2.1.2.2.1.10', ports, 'Counter32')
		if not dataStore.has_key(ip):
			dataStore[ip] = {}
			for port in newData:
				dataStore[ip][port] = 0L
				
		for port in newData:
			if lastData.has_key(ip):
				# check if counters have overflowed, if so, compensate
				olddiff = newData[port] - lastData[ip][port]
				#print "  port %s: lastData = %s, new = %s, olddiff = %s" % (port, lastData[ip][port], newData[port], olddiff)
				if olddiff < 0:
					dataStore[ip][port] += (OVERFLOW_VALUE - lastData[ip][port]) + newData[port]
				else:
					dataStore[ip][port] += olddiff
			else:
				dataStore[ip][port] = long(newData[port])
			
		lastData[ip] = newData
	except:
		print "cannot get data from %s" % ip

def getSwitchTrafficMB(ip):
	global dataStore
	total = 0L
	for port in dataStore[ip]:
		total += dataStore[ip][port]

	total /= (1024L**2L)
	return total

iterations = 60
last_counter = 0L
sign.playlist((0,1))
while True:
	started = time()
	counter = 0L
	threads = []
	for x in range(2,5):
		ip = '10.7.0.%s' % x
		thread = FunctionThreader(getSwitchData, [ip, range(3,25)])
		threads.append(thread)
		thread.start()

	for thread in threads:
		thread.join()
	
	for x in range(2,5):
		ip = '10.7.0.%s' % x
		#try:
		#	getSwitchData(ip, range(3, 25))
		#except Exception:
		#	print "warning: couldn't get data on %s" % ip
		
		traffic = getSwitchTrafficMB(ip)
		print "total traffic on %s: %s MiB" % (ip, traffic)
		counter += traffic

	print ""
	#counter /= 1024L
	counter = long(counter) + 1616258L
	print "traffic: %s MiB" % counter
	speed = long((float(counter) - float(last_counter)) / (time() - started))
	print "speed: %s MiB/s" % speed
	sign.set_page(0, EFFECT_SCROLL_UP, 1, 1, EFFECT_SCROLL_UP, "%s MiB" % counter)
	sign.set_page(1, EFFECT_SCROLL_UP, 1, 1, EFFECT_SCROLL_UP, "%s MiB/s" % speed)
	if iterations == 1:
		opener.open("http://morbo:8001/marquee.commit.html?" + urlencode({'marqueeText': 'Network Traffic (D/E/G switches): %s MiB, %s MiB/s' % (counter, speed)}))
	if iterations >= 60:
		iterations = 0

	print ""
	print ""
	#print "total traffic %s MiB" % getSwitchTrafficMB('10.7.0.2')
	sleep(3)
	last_counter = counter
	iterations += 1
