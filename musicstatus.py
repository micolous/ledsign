from ledsign import *
import socket, time

sign = LEDSign('/dev/ttyUSB0')
HOST = 'x.dhcp.streetgeek.lan'
PORT = 8080
data = ""

while True:
  # get song data
  print "get song"
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    data = sock.recv(1024)
    sock.close()
  except:
    pass
  
  # send to sign!
  print "send to sign; '%s'" % data
  #for d in data:
  #  print "%X" % ord(d),
  #sign.begin_textlines()
  sign.set_page(0, EFFECT_SCROLL_LEFT, 1, 0, EFFECT_SCROLL_LEFT, data)
  #sign.end_textlines()
  
  print "sleeping for 5s"
  time.sleep(5)
