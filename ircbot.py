import irclib
from ledsign2 import *

def write_to_sign(msg):
  sign = LEDSign('/dev/ttyS0')
  sign.begin_message()
  sign.begin_file(1)
  try:
    sign.add_text(msg)
  except:
    print "exception caught"
    sign.add_text("exception caught")
  sign.end_file()
  sign.end_message()

def handle_pubmsg(connection, event):
  nick = event.source().partition("!")[0]
  msg = event.arguments()[0]
  write_to_sign("<%s> %s" % (nick, msg))
  
def handle_join(connection, event):
  nick = event.source().partition("!")[0]
  write_to_sign("%s joined" % nick)
  
def handle_quit(connection, event):
  nick = event.source().partition("!")[0]
  write_to_sign("%s quit" % nick)
  

irc = irclib.IRC()

irc.add_global_handler('pubmsg', handle_pubmsg)
irc.add_global_handler('join', handle_join)
irc.add_global_handler('quit', handle_quit)
  

server = irc.server()
server.connect("marvin", 6667, "signbot")
server.join("#streetgeek")
irc.process_forever()
