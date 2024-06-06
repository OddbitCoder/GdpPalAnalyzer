from ic12 import IC12
from pal import Pal16R4Base

pal = IC12()
pal2 = Pal16R4Base()

print(pal2)

print(pal)

pal.set_inputs(90)
# pal.clock()
pal.read_outputs()
pal.set_inputs(229)
pal.read_outputs()

print(pal)
