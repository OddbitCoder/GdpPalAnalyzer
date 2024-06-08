import random
import time

from ic12 import IC12
from pal import Pal16R4DuPAL

pal_simulated = IC12()
# pal_real = Pal16R4DuPAL(port="COM5")

while True:
    # we ask user to enter inputs manually
    # inputs = input("Enter inputs: ")
    # set inputs to "clock" with 1/3 probability
    if random.randint(0, 2) == 0:
        inputs = "clock"
    else:
        inputs = random.randint(0, 255)
        inputs |= 0b10000000
    # if 'clock' is entered, we trigger clock
    if inputs == "clock":
        # pal_real.clock()
        pal_simulated.clock()
        print("clock")
    else:
        inputs = int(inputs)
        # pal_real.set_inputs(inputs)
        pal_simulated.set_inputs(inputs)
        print(f"inputs: {inputs}")

    # pal_real.read_outputs()
    pal_simulated.read_outputs()

    print("*** REAL:")
    # print(pal_real)
    print("*** SIMULATED:")
    print(pal_simulated)

    time.sleep(0.1)

# from ic12 import IC12
#
# pal = IC12()
#
# print(pal)
#
# pal.set_inputs(90)
# pal.read_outputs()
# pal.set_inputs(229)
# pal.read_outputs()
#
# print(pal)
