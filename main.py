from analyzer import PalAnalyzer
from converter import Converter
from dupal import DuPalBoard
from pal import Pal16L8, Pal10L8, Pal16R4, Pal16R4IC49
import sys

print("%x" % sys.maxsize, sys.maxsize > 2**32)

# board = DuPalBoard(Pal16R4IC49(), port="COM4", delay=0.01)
# analyzer = PalAnalyzer(board)
# analyzer.analyze("C:\\Work\\pal_tester\\ic49_new.json")

# Converter.convert_to_table(
#     "C:\\Work\\pal_tester\\reads\\ic12\\ic12_new_code.json",
#     "C:\\Work\\pal_tester\\reads\\ic12\\ic12_new_code_2.tbl",
# )

# Exporter.export_table(
#     "C:\\Work\\pal_tester\\ic7_2.json", "C:\\Work\\pal_tester\\ic7_2.tbl"
# )

# import random
# import time
#
# from ic12 import IC12
# from pal import Pal16R4DuPAL
#
# pal_simulated = IC12()
# pal_real = Pal16R4DuPAL(port="COM5")
#
# # DuPAL for some reason fires a clock signal on start-up. We need do the same with the simulated PAL
# # in order to get a match at the beginning.
# pal_simulated.clock()
#
# while True:
#     if random.randint(0, 2) == 0:
#         inputs = "clock"
#     else:
#         inputs = random.randint(0, 255)
#     if inputs == "clock":
#         pal_real.clock()
#         pal_simulated.clock()
#         print("clock")
#     else:
#         pal_real.set_inputs(inputs)
#         pal_simulated.set_inputs(inputs)
#         print(f"inputs: {inputs}")
#
#     outputs_real = pal_real.read_outputs()
#     outputs_simulated = pal_simulated.read_outputs()
#
#     print("*** REAL:")
#     print(pal_real)
#     print("*** SIMULATED:")
#     print(pal_simulated)
#
#     if outputs_real != outputs_simulated:
#         print("*** OUTPUTS MISMATCH ***")
#         exit(-1)
#
#     time.sleep(1)
