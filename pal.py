from enum import Enum
from typing import Tuple

from dupal_client import DuPalClient
from utils import bstr18, bcpl18


class PalType(Enum):
    PAL10L8 = 1
    PAL16L8 = 2
    PAL16R4 = 3


class PalBase:
    def read_outputs(self, inputs: int, clock: bool = False) -> int:
        raise NotImplementedError

    def read_states(self, inputs: int, clock: bool = False) -> Tuple[int, int]:
        raise NotImplementedError

    def force_state(self, state: int):
        raise NotImplementedError

    @property
    def type(self) -> PalType:
        raise NotImplementedError


class IC49(PalBase):
    def __init__(self):
        self.fq14 = 1
        self.fq15 = 1
        self.fq16 = 1
        self.fq17 = 1

    def force_state(self, state: int):
        self.fq14 = (state >> 3) & 1
        self.fq15 = (state >> 2) & 1
        self.fq16 = (state >> 1) & 1
        self.fq17 = (state >> 0) & 1

    def read_outputs(self, inputs: int, clock: bool = False) -> int:
        outputs, _ = self.read_states(inputs, clock)
        return outputs

    def read_states(self, inputs: int, clock: bool = False) -> Tuple[int, int]:
        f12, _, f13, _, _, _, _, f18, _, i9, i8, i7, i6, i5, i4, i3, i2, _ = list(
            map(int, bstr18(inputs).replace("_", ""))
        )
        q14 = int((not self.fq15) or f12)
        q15 = f12
        q16 = i3
        q17 = i2
        if clock:
            self.fq14, self.fq15, self.fq16, self.fq17 = q14, q15, q16, q17
        o19 = int((i4 and i3) or (self.fq16 and not i4))
        o18 = int(
            (not i7 and not i5 and not i4)
            or (not i8 and i5 and not i4)
            or (not i6 and i4)
        )
        z18 = int((i9 and not i4))
        outputs_str = "".join(
            map(
                str,
                [
                    f12,  # always HI-Z
                    o19,
                    f13,  # always HI-Z
                    self.fq14,
                    self.fq15,
                    self.fq16,
                    self.fq17,
                    o18 if not z18 else f18,
                ],
            )
        )
        hi_z_str = "".join(map(str, [1, 0, 1, 0, 0, 0, 0, z18]))
        return int(outputs_str, 2), int(hi_z_str, 2)


class IC12(PalBase):
    def __init__(self):
        self.fq14 = 1
        self.fq15 = 1
        self.fq16 = 1
        self.fq17 = 1

    def force_state(self, state: int):
        self.fq14 = (state >> 3) & 1
        self.fq15 = (state >> 2) & 1
        self.fq16 = (state >> 1) & 1
        self.fq17 = (state >> 0) & 1

    def read_outputs(self, inputs: int, clock: bool = False) -> int:
        outputs, _ = self.read_states(inputs, clock)
        return outputs

    def read_states(self, inputs: int, clock: bool = False) -> Tuple[int, int]:
        _, _, _, _, _, _, _, _, _, i9, i8, i7, i6, i5, i4, i3, i2, _ = list(
            map(int, bstr18(inputs).replace("_", ""))
        )
        q14 = i2
        q15 = int((not self.fq14) or i2)
        q16 = int(
            (not i8 and not i5 and not i3)
            or (not i7 and not i5)
            or (not i8 and i3)
            or i6
            or i5
        )
        q17 = int((i8 and not i5 and not i3) or (i8 and i3) or i5)
        if clock:
            self.fq14, self.fq15, self.fq16, self.fq17 = q14, q15, q16, q17
        o12 = int(
            (i8 and not i5 and not i3)
            or (not i8 and not i5 and not i3)
            or (i8 and i3)
            or (not i8 and i3)
            or i4
        )
        o19 = int(
            (i8 and not i5 and not i3)
            or (not i8 and not i5 and not i3)
            or i6
            or i4
            or i5
        )
        o13 = int(
            (not i7 and i4)
            or (self.fq16 and i4)
            or (not i7 and i3)
            or (self.fq16 and i3)
            or (self.fq16 and not i5)
            or (not i7 and not i5)
        )
        o18 = int((i8 and i3) or (not i8 and i3) or i6 or i4 or i5)
        outputs_str = "".join(
            map(
                str,
                [
                    o12,
                    o19,
                    o13,
                    self.fq14,
                    self.fq15,
                    self.fq16,
                    self.fq17,
                    o18,
                ],
            )
        )
        return int(outputs_str, 2), 0

    @property
    def type(self) -> PalType:
        return PalType.PAL16R4


class IC7(PalBase):
    def read_outputs(self, inputs: int, clock: bool = False) -> int:
        outputs, _ = self.read_states(inputs, clock)
        return outputs

    def read_states(self, inputs: int, clock: bool = False) -> Tuple[int, int]:
        _, f19, _, _, _, _, _, f18, i11, i9, i8, i7, i6, i5, i4, i3, i2, i1 = list(
            map(int, bstr18(inputs).replace("_", ""))
        )
        # HI-Z
        z12 = 0
        z19 = int((not i9 and not i6 and i1) or (not i9 and not i8 and not i7))
        z13 = 0
        z14 = 0
        z15 = 0
        z16 = 0
        z17 = 0
        z18 = int(
            (i8 and i6) or (i8 and not i1) or (i7 and i6) or (i7 and not i1) or i9
        )
        # outputs
        o12 = int(
            (i5 and not i4 and i3)
            or (i5 and not i4 and not i3)
            or (i5 and i4)
            or (not i7)
            or (i7 and not i1)
            or i9
        )
        o19 = int((i7 and i6) or (not i7) or (i7 and not i1) or i9)
        o13 = int(
            (i8 and i6) or (i8 and not i1) or (i7 and i6) or (i7 and not i1) or i9
        )
        o14 = int((i5 and not i4 and i3) or (i5 and i4) or (not i1) or (not i5) or i9)
        o15 = int(
            (i5 and not i4 and not i3)
            or (i5 and i4)
            or (not i5)
            or (not i7)
            or (i7 and not i1)
            or i9
        )
        o16 = int(
            (i5 and not i4 and i3)
            or (i5 and not i4 and not i3)
            or (not i5)
            or (not i7)
            or (i7 and not i1)
            or i9
        )
        o17 = int((i7 and i2))
        o18 = 0
        outputs_str = "".join(
            map(
                str,
                [
                    o12,
                    o19 if not z19 else f19,
                    o13,
                    o14,
                    o15,
                    o16,
                    o17,
                    o18 if not z18 else f18,
                ],
            )
        )
        hi_z_str = "".join(map(str, [z12, z19, z13, z14, z15, z16, z17, z18]))
        return int(outputs_str, 2), int(hi_z_str, 2)

    @property
    def type(self) -> PalType:
        return PalType.PAL16L8


class IC22(PalBase):
    def read_outputs(self, inputs: int, clock: bool = False) -> int:
        _, _, _, _, _, _, _, _, i11, i9, i8, i7, i6, i5, i4, i3, i2, i1 = list(
            map(int, bstr18(inputs).replace("_", ""))
        )
        o12 = int(i2 or i3)
        o19 = int(i9 or not i11)
        o13 = int((not i3 and i1) or (i2 and i1))
        o14 = int(i3 or not i6)
        o15 = int(not i5 or not i6)
        o16 = int(i1 or not i11)
        o17 = int(i11 and i3 and not i2)
        o18 = int((i8 and i6) or (i7 and not i6))
        outputs_str = "".join(map(str, [o12, o19, o13, o14, o15, o16, o17, o18]))
        return int(outputs_str, 2)

    def read_states(self, inputs: int, clock: bool = False) -> Tuple[int, int]:
        outputs = self.read_outputs(inputs)
        return outputs, 0

    @property
    def type(self) -> PalType:
        return PalType.PAL16L8


class IC24(PalBase):
    def read_outputs(self, inputs: int, clock: bool = False) -> int:
        _, _, _, _, _, _, _, _, i11, i9, i8, i7, i6, i5, i4, i3, i2, i1 = list(
            map(int, bstr18(inputs).replace("_", ""))
        )
        o12 = int(not i2 or not i1)
        o19 = 1  # int(i1 or not i1)
        o13 = int(not i2 or i1)
        o14 = int(not i1)
        o15 = int(not i4 and not i3)
        o16 = int((i6 and not i5) or i7)
        o17 = 1  # int(i1 or not i1)
        o18 = 1  # int(i1 or not i1)
        outputs_str = "".join(map(str, [o12, o19, o13, o14, o15, o16, o17, o18]))
        return int(outputs_str, 2)

    def read_states(self, inputs: int, clock: bool = False) -> Tuple[int, int]:
        outputs = self.read_outputs(inputs)
        return outputs, 0

    @property
    def type(self) -> PalType:
        return PalType.PAL10L8


class DuPalBoard(PalBase):
    def __init__(self, pal_type: PalType, port: str, delay: float = 0.01):
        self._pal_type = pal_type
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
        # print(f"{bstr18(inputs)} -> {bstr18(outputs)}")
        # determine hi-z mask
        hi_z_mask = 0
        io_mask = 0b111111110000000000
        hi_z_test_pins = bcpl18(inputs ^ outputs) & io_mask
        if hi_z_test_pins:
            # print(f"HI-Z candidates: {bstr18(hi_z_test_pins)}")
            for i in range(10, 18):
                if hi_z_test_pins & (1 << i):
                    # print(f"Bit {i} is ON")
                    bit_from_inputs = (inputs >> i) & 1
                    new_inputs = (
                        inputs | (1 << i)
                        if not bit_from_inputs
                        else inputs & bcpl18(1 << i)
                    )
                    # print(f"New inputs:  {bstr18(new_inputs)}")
                    new_outputs = self.read_outputs(new_inputs) << 10
                    # print(f"New outputs: {bstr18(new_outputs)}")
                    hi_z_mask |= (new_outputs ^ outputs) & io_mask
                    # reset
                    assert outputs == self.read_outputs(inputs) << 10
        # print(f"Final HI-Z mask: {bstr18(hi_z_mask)}")
        return outputs >> 10, hi_z_mask >> 10

    @property
    def type(self) -> PalType:
        return self._pal_type
