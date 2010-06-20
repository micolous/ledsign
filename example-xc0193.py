from ledsign2 import *

# Open a connection to the sign.  you'll need to change the device node
# here if you're not using a USB-Serial converter.  If you have an
# actual serial port, use /dev/ttyS0 instead for COM1.  If you're on Windows,
# use "COM1" or whatever the port's name is.  You can also set it to a
# numeric value starting at 0 (ie: open the first serial port).
#
sign = LEDSign('/dev/ttyUSB0')

# Begin talking to the sign.  By default, it will be sent to all signs, and
# not do a factory reset on the sign.
#
# You could also set it to send to specific sign by supplying a tuple
# parameter 'sign' (eg:  sign=(1, 2) to send to signs 1 and 2.
#
# A sign will blank out while it is being programmed.
sign.begin_message()

# Set the device's clock to the computer's time.  You can also use the
# parameter 'n' to set it to an arbitrary time (in a datetime.datetime object).
#
# The hour24 parameter indicates whether to use 24 hour time.
# Defaults to True.
sign.set_clock()

# Begin data for file 1.  File numbers are between 1 and 99.
# While you are writing a file, you can only add data to that file.  Some
# special commands (like setting the clock) are not available while a file
# is being sent.
sign.begin_file(1)

# A file structure consists of a run mode (optionally), followed by some text.
# You can also end a "frame" and add another run mode and add some more text.
# So you could have it go:
#
#  1) Add Run mode EFFECT_IMMEDIATE
#  2) Add Special  SPEED_8
#  3) Add Special  SPECIAL_TIME
#  4) End frame
#  5) Add Run mode EFFECT_SCROLL_LEFT
#  6) Add Text     "Sunny, 24C"
#
# This would make the sign display the time for a few seconds, then "Sunny,
# 24C".  In reality you would make it get the weather from another data
# source though.

# Make the text display immediately
sign.add_run_mode(EFFECT_IMMEDIATE)

# Add the text
sign.add_text("This is a test")

# End of file.
sign.end_file()

# End message to the signs.  The file will then be "played".
sign.end_message()
