from analyzer import PalAnalyzer
from converter import Converter
from dupal import DuPalBoard, DuPalBase
from node import Node
from pal import Pal16L8
import sys

# Sanity checks need to make sure that we are not dealing with a PAL configuration that we do not support.
# We need to check if any of the "pure" outputs is in HI-Z, and simply set the HI-Z mask.
# We need to check if any of the outputs with feedbacks (I/O) is in HI-Z and if yes, we need to make sure that
# it is not intended to act as an input.
def sanity_checks_ic7(dupal: DuPalBase, node: Node, inputs: int, outputs: int):
    print("Checking new state...")
    print(f"Inputs:  {inputs:08b}")
    print(f"Outputs: {outputs:018b}")
    # check if any of the outputs w/o feedbacks is in HI-Z state (this is not an issue, we just need to note it)
    # this can only be outputs that are now 0 (because they were set to 0) and pick up to 1 if we set them to 1
    mask = 0b11000000
    candidates = ~outputs & mask  # can only be outputs that are now 0 (because they were set to 0)
    if candidates:
        # can only be outputs that pick up to 1 if we set them to 1
        new_inputs = inputs | (candidates << 10)
        new_outputs = dupal.set_inputs(new_inputs)
        node.hi_z_mask = candidates & new_outputs
        if node.hi_z_mask:
            print(f"Found outputs in HI-Z: {node.hi_z_mask:08b}")
    # check if any of the outputs with feedbacks is in HI-Z state
    mask = ~mask  # 0b00111111
    candidates = ~outputs & mask  # can only be outputs that are now 0 (because they were set to 0)
    if candidates:
        single_io_list = [1 << i for i in range(candidates.bit_length()) if candidates & (1 << i)]
        for single_io in single_io_list:
            # pull this single I/O to 1
            new_inputs = inputs | (single_io << 10)
            new_outputs = dupal.set_inputs(new_inputs)
            hi_z_mask = candidates & new_outputs  # was that I/O pulled to 1?
            assert(outputs == new_outputs & ~hi_z_mask)  # is the rest still the same?
            if hi_z_mask:
                node.hi_z_mask |= hi_z_mask
                print(f"I/O {single_io:08b} is HI-Z")
            else:
                print(f"I/O {single_io:08b} is 0")

board = DuPalBoard(Pal16L8(), port="COM4", delay=0.01)
analyzer = PalAnalyzer(board, sanity_checks_ic7)
analyzer.analyze("C:\\Work\\PalAnalyzer\\new_reads\\ic7\\ic7.json")

# Converter.convert_to_table_16l8(
#     "C:\\Work\\PalAnalyzer\\new_reads\\ic22\\ic22.json",
#     "C:\\Work\\PalAnalyzer\\new_reads\\ic22\\ic22.tbl",
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
