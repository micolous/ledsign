from ledsign2 import *

sign = LEDSign('/dev/ttyS0')

sign.begin_message()
sign.set_clock()

sign.begin_file(1)
sign.add_run_mode(EFFECT_IMMEDIATE)

sign.add_special(SPECIAL_TIME)

sign.end_file()


sign.end_message()
