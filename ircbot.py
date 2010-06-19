import irclib, traceback
from ledsign2 import *

def write_to_sign(msg):
  sign = LEDSign('/dev/ttyUSB0')
  sign.begin_message()
  sign.begin_file(1)
  msgl = len(msg)
  msg = msg.replace("\x07","")
  if msgl > len(msg):
    # beep!
    sign.add_special(SOUND_BEEP_1)
  try:
    print msg
    sign.add_text(msg)
  except:
    print "exception caught trying to send '%s'" % msg
    traceback.print_exc()
    sign.add_text("exception caught")
  sign.end_file()
  sign.end_message()

def handle_pubmsg(connection, event):
  nick = event.source().partition("!")[0]
  msg = event.arguments()[0]
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
  

irc = irclib.IRC()

irc.add_global_handler('pubmsg', handle_pubmsg)
irc.add_global_handler('join', handle_join)
irc.add_global_handler('quit', handle_quit)
irc.add_global_handler('action', handle_action)

server = irc.server()
server.connect("irc.micolous.id.au", 6667, "signbot")
server.join("#streetgeek")
irc.process_forever()
