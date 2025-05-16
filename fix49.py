from pal import DuPalBoard, PalType
from utils import bstr18, bcpl18

if __name__ == "__main__":
    pal = DuPalBoard(PalType.PAL16R4, "COM5")
    #   23   22   21   20   19   18   17   16
    # .----.----.----.----.----.----.----.----.
    # | xx | xx | xx | xx | xx | xx | 12 | 19 | Byte 2
    # '----'----'----'----'----'----'----'----'
    #
    #   15   14   13   12   11   10    9    8
    # .----.----.----.----.----.----.----.----.
    # | 13 | 14 | 15 | 16 | 17 | 18 | 11 |  9 | Byte 1
    # '----'----'----'----'----'----'----'----'
    #
    #    7    6    5    4    3    2    1    0
    # .----.----.----.----.----.----.----.----.
    # |  8 |  7 |  6 |  5 |  4 |  3 |  2 |  1 | Byte 0
    # '----'----'----'----'----'----'----'----'
    inputs = 0b_00_000001_0100001000
    print("inputs:      " + bstr18(inputs))
    outputs = pal.read_outputs(inputs, clock=False)
    outputs <<= 10
    print("outputs:     " + bstr18(outputs))
    # check states
    hi_z_mask = 0
    io_mask = 0b_11_111111_0000000000
    hi_z_test_pins = bcpl18(inputs ^ outputs) & io_mask
    print("test pins:   " + bstr18(hi_z_test_pins))
    if hi_z_test_pins:
        # print(f"HI-Z candidates: {bstr18(hi_z_test_pins)}")
        for i in range(10, 18):
            pin_to_test = 1 << i
            if hi_z_test_pins & pin_to_test:
                # print(f"Bit {i} is ON")
                bit_from_inputs = (inputs >> i) & 1
                new_inputs = (
                    inputs | pin_to_test
                    if not bit_from_inputs
                    else inputs & bcpl18(pin_to_test)
                )
                print(f"new inputs:  {bstr18(new_inputs)}", end="")
                new_outputs = pal.read_outputs(new_inputs) << 10
                print(f" -> {bstr18(new_outputs)}", end="")
                print(f" -> {bstr18(bcpl18(new_inputs ^ new_outputs) & pin_to_test)}")
                #hi_z_mask |= (new_outputs ^ outputs) & io_mask # BUG !!!!!!!!!!!!!!!!
                hi_z_mask |= bcpl18(new_inputs ^ new_outputs) & pin_to_test
                # reset
                assert outputs == pal.read_outputs(inputs) << 10
    # print(f"Final HI-Z mask: {bstr18(hi_z_mask)}")
    print(bstr18(outputs >> 10, hi_z_mask >> 10))