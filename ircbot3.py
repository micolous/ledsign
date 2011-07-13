import irclib, traceback
from ledsign2 import *
from urllib2 import urlopen

def get_winamp():
	# lol, you know passwords, so what?
	# you're not on this network so it doesn't matter.
	track_num = urlopen('http://192.168.1.51:4800/getlistpos?pass=123').read()
	track_num = long(track_num)
	
	track_title = urlopen('http://192.168.1.51:4800/getplaylisttitle?pass=123&a=%d' % track_num).read().replace('<br>', '')
	
	return track_title

def write_to_sign(msg):
	sign = LEDSign('/dev/ttyS0')
	sign.begin_message()
	sign.begin_file(1)
	sign.add_run_mode(EFFECT_IMMEDIATE)
	try:
		print msg
		sign.add_text(msg)
	except:
		print "exception caught trying to send '%s'" % msg
		traceback.print_exc()
		sign.add_text("exception caught")
	
	try:
		song = get_winamp()
		sign.end_frame()
		sign.add_text('         ' + song)
	except:
		print "error getting winamp httpq"
		
	sign.end_file()
	sign.end_message()

def handle_pubmsg(connection, event):
  nick = event.source().partition("!")[0]
  msg = event.arguments()[0]
  if '\x07' in msg:
    write_to_sign("%s is an idiot" % nick)
  else:
    write_to_sign("<%s> %s" % (nick, msg))

def handle_action(connection, event):
  nick = event.source().partition("!")[0]
  msg = event.arguments()[0]
  write_to_sign("* %s %s *" % (nick, msg))

def handle_join(connection, event):
  nick = event.source().partition("!")[0]
  write_to_sign("%s joined" % nick)
  
def handle_quit(connection, event):
  nick = event.source().partition("!")[0]
  msg = event.arguments()[0]
  write_to_sign("%s quit [%s]" % (nick, msg))


if __name__ == '__main__':
	irc = irclib.IRC()

	irc.add_global_handler('pubmsg', handle_pubmsg)
	irc.add_global_handler('join', handle_join)
	irc.add_global_handler('quit', handle_quit)
	irc.add_global_handler('action', handle_action)

	server = irc.server()
	server.connect("localhost", 6667, "signbot")
	server.join("#test")
	irc.process_forever()
