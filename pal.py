from typing import Optional


class PalBase:
    def __init__(self, inputs_range: int):
        self._inputs_range = inputs_range

    def set_inputs(self, inputs: int):
        raise NotImplementedError

    @property
    def inputs_as_byte(self) -> int:
        raise NotImplementedError

    def set_outputs(self, outputs: int):
        raise NotImplementedError

    @property
    def outputs_as_byte(self) -> int:
        raise NotImplementedError

    def set_register_inputs(self, outputs: Optional[int]):
        raise NotImplementedError

    @staticmethod
    def map_inputs(
        inputs: int, clock_bit: bool = False, pull_tristate_outputs: bool = False
    ) -> int:
        raise NotImplementedError

    @property
    def inputs_range(self):
        return self._inputs_range


class Pal16L8(PalBase):
    def __init__(self):
        super().__init__(inputs_range=2**10)
        self._pal_type = "16L8"
        # input pins
        self.i1: int = 0
        self.i2: int = 0
        self.i3: int = 0
        self.i4: int = 0
        self.i5: int = 0
        self.i6: int = 0
        self.i7: int = 0
        self.i8: int = 0
        self.i9: int = 0
        self.i11: int = 0
        # according to the schematic, the following can all be 3-state outputs
        # I/O
        self.io13: int = 0
        self.io14: int = 0
        self.io15: int = 0
        self.io16: int = 0
        self.io17: int = 0
        self.io18: int = 0
        # outputs
        self.o19: int = 0
        self.o12: int = 0

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
    def set_inputs(self, inputs: int):
        self.i1 = (inputs >> 0) & 1
        self.i2 = (inputs >> 1) & 1
        self.i3 = (inputs >> 2) & 1
        self.i4 = (inputs >> 3) & 1
        self.i5 = (inputs >> 4) & 1
        self.i6 = (inputs >> 5) & 1
        self.i7 = (inputs >> 6) & 1
        self.i8 = (inputs >> 7) & 1
        self.i9 = (inputs >> 8) & 1
        self.i11 = (inputs >> 9) & 1

    @staticmethod
    def map_inputs(
        inputs: int, clock_bit: bool = False, pull_tristate_outputs: bool = False
    ) -> int:
        return (
            inputs
            if not pull_tristate_outputs
            else (
                inputs
                | (1 << 10)
                | (1 << 11)
                | (1 << 12)
                | (1 << 13)
                | (1 << 14)
                | (1 << 15)
                | (1 << 16)
                | (1 << 17)
            )
        )

    @property
    def inputs_as_byte(self) -> int:
        inputs = (
            (self.i1 << 0)
            | (self.i2 << 1)
            | (self.i3 << 2)
            | (self.i4 << 3)
            | (self.i5 << 4)
            | (self.i6 << 5)
            | (self.i7 << 6)
            | (self.i8 << 7)
            | (self.i9 << 8)
            | (self.i11 << 9)
        )
        return inputs

    #    7    6    5    4    3    2    1    0
    # .----.----.----.----.----.----.----.----.
    # | 12 | 19 | 13 | 14 | 15 | 16 | 17 | 18 |
    # '----'----'----'----'----'----'----'----'
    def set_outputs(self, outputs: int):
        self.o12 = (outputs >> 7) & 1
        self.o19 = (outputs >> 6) & 1
        self.io13 = (outputs >> 5) & 1
        self.io14 = (outputs >> 4) & 1
        self.io15 = (outputs >> 3) & 1
        self.io16 = (outputs >> 2) & 1
        self.io17 = (outputs >> 1) & 1
        self.io18 = (outputs >> 0) & 1

    @property
    def outputs_as_byte(self) -> int:
        return (
            (self.o12 << 7)
            | (self.o19 << 6)
            | (self.io13 << 5)
            | (self.io14 << 4)
            | (self.io15 << 3)
            | (self.io16 << 2)
            | (self.io17 << 1)
            | (self.io18 << 0)
        )

    def __str__(self):
        return (
            f"             +-----_-----+\n"
            f"     i1 ({self.i1}) -|1        20|- VCC\n"
            f"     i2 ({self.i2}) -|2        19|- o19  ({self.o19})\n"
            f"     i3 ({self.i3}) -|3        18|- io18 ({self.io18})\n"
            f"     i4 ({self.i4}) -|4        17|- io17 ({self.io17})\n"
            f"     i5 ({self.i5}) -|5  PAL   16|- io16 ({self.io16})\n"
            f"     i6 ({self.i6}) -|6  {self._pal_type}  15|- io15 ({self.io15})\n"
            f"     i7 ({self.i7}) -|7        14|- io14 ({self.io14})\n"
            f"     i8 ({self.i8}) -|8        13|- io13 ({self.io13})\n"
            f"     i9 ({self.i9}) -|9        12|- o12  ({self.o12})\n"
            f"        GND -|10       11|- i11  ({self.i11})\n"
            f"             +-----------+\n\n"
            f"Inputs:  {self.inputs_as_byte}\n"
            f"Outputs: {self.outputs_as_byte}"
        )


class Pal10L8(Pal16L8):
    # according to the schematic, this PAL does not have any 3-state outputs
    def __init__(self):
        super().__init__()
        self._pal_type = "10L8"


class Pal16R4(PalBase):
    def __init__(self):
        super().__init__(inputs_range=2**8)
        # input pins
        self.i2: int = 0
        self.i3: int = 0
        self.i4: int = 0
        self.i5: int = 0
        self.i6: int = 0
        self.i7: int = 0
        self.i8: int = 0
        self.i9: int = 0
        # output pins
        self.io12: int = 0
        self.io13: int = 0
        self.o14: int = 0  # tri-state
        self.o15: int = 0  # tri-state
        self.o16: int = 0  # tri-state
        self.o17: int = 0  # tri-state
        self.io18: int = 0
        self.io19: int = 0
        # inputs into registers
        self.r14: Optional[int] = None
        self.r15: Optional[int] = None
        self.r16: Optional[int] = None
        self.r17: Optional[int] = None

    #   23   22   21   20   19   18   17   16
    # .----.----.----.----.----.----.----.----.
    # | xx | xx | xx | xx | xx | xx | 12 | 19 | Byte 2
    # '----'----'----'----'----'----'----'----'
    #
    #   15   14   13   12   11   10    9    8
    # .----.----.----.----.----.----.----.----.
    # | 13 | 14 | 15 | 16 | 17 | 18 | 11 |  9 | Byte 1
    # '----'----'----'----'----'----'----'----'
    #                                         This is the clock bit
    #    7    6    5    4    3    2    1    0  /
    # .----.----.----.----.----.----.----.----.
    # |  8 |  7 |  6 |  5 |  4 |  3 |  2 |  1 | Byte 0
    # '----'----'----'----'----'----'----'----'
    def set_inputs(self, inputs: int):
        self.i2 = (inputs >> 0) & 1
        self.i3 = (inputs >> 1) & 1
        self.i4 = (inputs >> 2) & 1
        self.i5 = (inputs >> 3) & 1
        self.i6 = (inputs >> 4) & 1
        self.i7 = (inputs >> 5) & 1
        self.i8 = (inputs >> 6) & 1
        self.i9 = (inputs >> 7) & 1

    @property
    def inputs_as_byte(self) -> int:
        return (
            (self.i2 << 0)
            | (self.i3 << 1)
            | (self.i4 << 2)
            | (self.i5 << 3)
            | (self.i6 << 4)
            | (self.i7 << 5)
            | (self.i8 << 6)
            | (self.i9 << 7)
        )

    #    7    6    5    4    3    2    1    0
    # .----.----.----.----.----.----.----.----.
    # | 12 | 19 | 13 | 14 | 15 | 16 | 17 | 18 |
    # '----'----'----'----'----'----'----'----'
    def set_outputs(self, outputs: int):
        self.io12 = (outputs >> 7) & 1
        self.io19 = (outputs >> 6) & 1
        self.io13 = (outputs >> 5) & 1
        self.o14 = (outputs >> 4) & 1
        self.o15 = (outputs >> 3) & 1
        self.o16 = (outputs >> 2) & 1
        self.o17 = (outputs >> 1) & 1
        self.io18 = (outputs >> 0) & 1

    @property
    def outputs_as_byte(self) -> int:
        return (
            (self.io18 << 0)
            | (self.o17 << 1)
            | (self.o16 << 2)
            | (self.o15 << 3)
            | (self.o14 << 4)
            | (self.io13 << 5)
            | (self.io19 << 6)
            | (self.io12 << 7)
        )

    def __str__(self):
        return (
            f"             +-----_-----+\n"
            f"        CLK -|1        20|- VCC\n"
            f"     i2 ({self.i2}) -|2        19|- io19 ({self.io19})\n"
            f"     i3 ({self.i3}) -|3        18|- io18 ({self.io18})\n"
            f"     i4 ({self.i4}) -|4        17|  r17  ({self.r17 if self.r17 is not None else '?'}) - o17 ({self.o17})\n"
            f"     i5 ({self.i5}) -|5  PAL   16|  r16  ({self.r16 if self.r16 is not None else '?'}) - o16 ({self.o16})\n"
            f"     i6 ({self.i6}) -|6  16R4  15|  r15  ({self.r15 if self.r15 is not None else '?'}) - o15 ({self.o15})\n"
            f"     i7 ({self.i7}) -|7        14|  r14  ({self.r14 if self.r14 is not None else '?'}) - o14 ({self.o14})\n"
            f"     i8 ({self.i8}) -|8        13|- io13 ({self.io13})\n"
            f"     i9 ({self.i9}) -|9        12|- io12 ({self.io12})\n"
            f"        GND -|10       11|- OE\n"
            f"             +-----------+\n\n"
            f"Inputs:  {self.inputs_as_byte}\n"
            f"Outputs: {self.outputs_as_byte}"
        )

    @staticmethod
    def map_inputs(
        inputs: int, clock_bit: bool = False, pull_tristate_outputs: bool = False
    ) -> int:
        mapped_inputs = inputs << 1
        if pull_tristate_outputs:
            mapped_inputs |= (1 << 14) | (1 << 13) | (1 << 12) | (1 << 11)
        return mapped_inputs if not clock_bit else mapped_inputs | 1

    #    7    6    5    4    3    2    1    0
    # .----.----.----.----.----.----.----.----.
    # | 12 | 19 | 13 | 14 | 15 | 16 | 17 | 18 |
    # '----'----'----'----'----'----'----'----'
    def set_register_inputs(self, outputs: Optional[int]):
        if outputs is None:
            self.r14 = self.r15 = self.r16 = self.r17 = None
        else:
            self.r14 = (outputs >> 4) & 1
            self.r15 = (outputs >> 3) & 1
            self.r16 = (outputs >> 2) & 1
            self.r17 = (outputs >> 1) & 1


class Pal16R4IC49(Pal16R4):
    def __init__(self):
        super().__init__()
        self._inputs_range = 2**10

    # this is a 10-bit value (8 + 2 inputs)
    def set_inputs(self, inputs: int):
        super().set_inputs(inputs)
        # set pins 12 and 13
        self.io12 = (inputs >> 8) & 1
        self.io13 = (inputs >> 9) & 1

    @property
    def inputs_as_byte(self) -> int:
        inputs = super().inputs_as_byte
        inputs |= self.io12 << 8
        inputs |= self.io13 << 9
        return inputs

    def set_outputs(self, outputs: int):
        # self.io12 = (outputs >> 7) & 1  # input pin
        self.io19 = (outputs >> 6) & 1
        # self.io13 = (outputs >> 5) & 1  # input pin
        self.o14 = (outputs >> 4) & 1
        self.o15 = (outputs >> 3) & 1
        self.o16 = (outputs >> 2) & 1
        self.o17 = (outputs >> 1) & 1
        self.io18 = (outputs >> 0) & 1

    @property
    def outputs_as_byte(self) -> int:
        return (
            (self.io18 << 0)
            | (self.o17 << 1)
            | (self.o16 << 2)
            | (self.o15 << 3)
            | (self.o14 << 4)
            # | (self.io13 << 5)  # input pin
            | (self.io19 << 6)
            # | (self.io12 << 7)  # input pin
        )

    @staticmethod
    def map_inputs(
        inputs: int, clock_bit: bool = False, pull_tristate_outputs: bool = False
    ) -> int:
        i12 = (inputs >> 8) & 1
        i13 = (inputs >> 9) & 1
        mapped_inputs = (inputs & 0xFF) << 1
        mapped_inputs |= i12 << 17
        mapped_inputs |= i13 << 15
        if pull_tristate_outputs:
            mapped_inputs |= (1 << 14) | (1 << 13) | (1 << 12) | (1 << 11)
        return mapped_inputs if not clock_bit else mapped_inputs | 1
