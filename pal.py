from enum import Enum
from typing import Tuple

from dupal_client import DuPalClient
from butils import bstr18, binv18


class PalType(Enum):
    PAL10L8 = 1
    PAL16L8 = 2
    PAL16R4 = 3


class PalBase:
    def read_outputs(self, inputs: int, clock: bool = False) -> int:
        raise NotImplementedError

    def read_states(self, inputs: int, clock: bool = False) -> Tuple[int, int]:
        raise NotImplementedError


class DuPalBoard(PalBase):
    def __init__(self, port: str, delay: float = 0.01):
        self._client = DuPalClient(port=port, delay=delay)
        self._client.init_board()
        self._client.control_led(1, 1)  # currently we only support 20-pin PALs

    def read_outputs(self, inputs: int, clock: bool = False) -> int:
        self._client.write_status(inputs)
        if clock:
            self._client.write_status(inputs | 1)  # with clock bit
            self._client.write_status(inputs)  # no clock bit
        return self._client.read_status()

    def read_states(self, inputs: int, clock: bool = False) -> Tuple[int, int]:
        outputs = self.read_outputs(inputs, clock) << 10
        print(f"{bstr18(inputs)} -> {bstr18(outputs)}")
        # determine hi-z mask
        hi_z_mask = 0
        io_mask = 0b111111110000000000
        hi_z_test_pins = binv18(inputs ^ outputs) & io_mask
        if hi_z_test_pins:
            print(f"HI-Z candidates: {bstr18(hi_z_test_pins)}")
            for i in range(10, 18):
                if hi_z_test_pins & (1 << i):
                    print(f"Bit {i} is ON")
                    bit_from_inputs = (inputs >> i) & 1
                    new_inputs = (
                        inputs | (1 << i)
                        if not bit_from_inputs
                        else inputs & binv18(1 << i)
                    )
                    print(f"New inputs:  {bstr18(new_inputs)}")
                    new_outputs = self.read_outputs(new_inputs) << 10
                    print(f"New outputs: {bstr18(new_outputs)}")
                    hi_z_mask |= (new_outputs ^ outputs) & io_mask
                    # reset
                    assert outputs == self.read_outputs(inputs) << 10
        print(f"Final HI-Z mask: {bstr18(hi_z_mask)}")
        return outputs >> 10, hi_z_mask >> 10
