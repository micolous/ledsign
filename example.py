from ledsign2 import *

sign = LEDSign('/dev/ttyUSB0')

sign.begin_message()
sign.set_clock()

sign.begin_file(1)
sign.add_run_mode(EFFECT_IMMEDIATE)

sign.add_text("This is a test")

sign.end_file()


sign.end_message()
