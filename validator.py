import random
import sys
from enum import Enum

from pal import IC49, DuPalBoard, PalType, PalBase, IC12
from utils import bstr8


class Mode(Enum):
    COMPARE_IC12 = 1
    COMPARE_IC49 = 2


port = "COM4"
delay = 0.001
path = "C:\\Work\\PalAnalyzer\\reads"
mode = Mode.COMPARE_IC12

if __name__ == "__main__":
    ic: PalBase
    if mode == Mode.COMPARE_IC49:
        ic = IC49()
    elif mode == Mode.COMPARE_IC12:
        ic = IC12()
    else:
        raise Exception("Invalid mode")
    dupal_board = DuPalBoard(PalType.PAL16R4, port, delay)
    # test
    while True:
        random_inputs = random.randint(0, 2**17 - 1) << 1
        random_inputs &= 0b111000010111111110
        fire_clock = random.choice([True, False])
        print(f"inputs: {random_inputs:018b}")
        print(f"clock:  {fire_clock}")
        outputs_sim, mask_sim = ic.read_states(random_inputs, fire_clock)
        outputs_real, mask_real = dupal_board.read_states(random_inputs, fire_clock)
        print(f"outputs sim:  {bstr8(outputs_sim, mask_sim)}")
        print(f"outputs real: {bstr8(outputs_real, mask_sim)}")
        assert bstr8(outputs_sim, mask_sim) == bstr8(outputs_real, mask_sim)
