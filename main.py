import random
import time

from analyzer import analyze
from pal import Pal16R4DuPAL, Pal16R4IC12

#
# pal = Pal16R4DuPAL(port="COM5")
# # open file for writing
# with open("C:\\Work\\pal_tester\\output.txt", "w") as file:
#     while True:
#         if random.randint(0, 3) == 0:
#             pal.clock()
#             file.write("Clock\n")
#         else:
#             inputs = random.randint(0, 255)
#             file.write(f"{str(inputs)}\n")
#             pal.set_inputs(inputs)
#         pal.read_outputs()
#         file.write(f"{str(pal._outputs)}\n")
#         print(pal)
#         time.sleep(0.1)
#         file.flush()

# pal = Pal16R4IC12()

# print(pal)

# with open("C:\\Work\\pal_tester\\output.txt", "r") as file:
#     lines = file.readlines()
#
# for inputs, outputs in zip(lines[0::2], lines[1::2]):
#     if inputs == "Clock\n":
#         pal.clock()
#         print("Clock")
#     else:
#         pal.set_inputs(int(inputs))
#         print(f"inputs: {int(inputs)}")
#     pal.read_outputs(outputs=int(outputs))
#     print(pal)

done = False
while not done:
    pal = Pal16R4IC12()
    print(pal)
    done = analyze(pal, set_one_mask=0b00000000)
