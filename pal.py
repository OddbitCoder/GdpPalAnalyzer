from typing import Optional

from dupal_client import DuPALClient


class PalBase:
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

    def clock(self) -> int:
        raise NotImplementedError

    @property
    def input_count(self) -> int:
        raise NotImplementedError

    @property
    def output_count(self) -> int:
        raise NotImplementedError

    def get_inputs(self, idx: int) -> int:
        raise NotImplementedError


class DuPALBoard:
    def __init__(self, pal: PalBase, port: str):
        self._pal = pal
        self._client = DuPALClient(port=port)
        self._client.init_board()
        self._client.control_led(1, 1)  # currently we only support 20-pin PALs

    def set_inputs(self, inputs: int):
        self._pal.set_inputs(inputs)

    @property
    def inputs_as_byte(self) -> int:
        return self._pal.inputs_as_byte

    def read_outputs(self) -> int:
        outputs = self._client.read_status()
        self._pal.set_outputs(outputs)
        return self._pal.outputs_as_byte

    @property
    def outputs_as_byte(self) -> int:
        return self._pal.outputs_as_byte

    def clock(self) -> int:
        self._pal.clock()
        return self._pal.outputs_as_byte

    def analyze(self):
        print(f"Analyzing {self._pal.__class__.__name__}...")
        print(f"Inputs: {self._pal.input_count}")
        print(f"Outputs: {self._pal.output_count}")
        pal_10l8 = isinstance(self._pal, Pal10L8)
        pal_16l8 = isinstance(self._pal, Pal16L8)
        if pal_10l8 or pal_16l8:
            # run through all inputs
            for idx in range(2 ** self._pal.input_count):
                self.set_inputs(self._pal.get_inputs(idx))
                outputs = self.read_outputs()
                print(outputs)
        if pal_16l8:
            # try all possible "feedbacks"
            pass


class Pal16L8(PalBase):
    def __init__(self, output_mask: int = 0b111111):  # 0b111111 sets all I/O pins to outputs
        self._output_mask = output_mask
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
        # I/O
        self.io12: int = 0
        self.io13: int = 0
        self.io14: int = 0
        self.io15: int = 0
        self.io16: int = 0
        self.io17: int = 0
        self.io18: int = 0
        # outputs
        self.o19: int = 0
        self.o12: int = 0

    def is_input(self, pin: int) -> bool:
        return (self._output_mask >> (pin - 13)) & 1 == 0

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
        if self.is_input(13):
            self.io13 = (inputs >> 15) & 1
        if self.is_input(14):
            self.io14 = (inputs >> 14) & 1
        if self.is_input(15):
            self.io15 = (inputs >> 13) & 1
        if self.is_input(16):
            self.io16 = (inputs >> 12) & 1
        if self.is_input(17):
            self.io17 = (inputs >> 11) & 1
        if self.is_input(18):
            self.io18 = (inputs >> 10) & 1

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
        if self.is_input(13):
            inputs |= self.io13 << 15
        if self.is_input(14):
            inputs |= self.io14 << 14
        if self.is_input(15):
            inputs |= self.io15 << 13
        if self.is_input(16):
            inputs |= self.io16 << 12
        if self.is_input(17):
            inputs |= self.io17 << 11
        if self.is_input(18):
            inputs |= self.io18 << 10
        return inputs

    #    7    6    5    4    3    2    1    0
    # .----.----.----.----.----.----.----.----.
    # | 12 | 19 | 13 | 14 | 15 | 16 | 17 | 18 |
    # '----'----'----'----'----'----'----'----'
    def set_outputs(self, outputs: int):
        self.o12 = (outputs >> 7) & 1
        self.o19 = (outputs >> 6) & 1
        if not self.is_input(13):
            self.io13 = (outputs >> 5) & 1
        if not self.is_input(14):
            self.io14 = (outputs >> 4) & 1
        if not self.is_input(15):
            self.io15 = (outputs >> 3) & 1
        if not self.is_input(16):
            self.io16 = (outputs >> 2) & 1
        if not self.is_input(17):
            self.io17 = (outputs >> 1) & 1
        if not self.is_input(18):
            self.io18 = (outputs >> 0) & 1

    @property
    def outputs_as_byte(self) -> int:
        outputs = (
            (self.o12 << 7)
            | (self.o19 << 6)
        )
        if not self.is_input(13):
            outputs |= self.io13 << 5
        if not self.is_input(14):
            outputs |= self.io14 << 4
        if not self.is_input(15):
            outputs |= self.io15 << 3
        if not self.is_input(16):
            outputs |= self.io16 << 2
        if not self.is_input(17):
            outputs |= self.io17 << 1
        if not self.is_input(18):
            outputs |= self.io18 << 0
        return outputs

    def __str__(self):
        return (
            f"             +-----_-----+\n"
            f"     i1 ({self.i1}) -|1        20|- VCC\n"
            f"     i2 ({self.i2}) -|2        19|- o19  ({self.o19})\n"
            f"     i3 ({self.i3}) -|3        18|- io18 ({self.io18}){' <-' if self.is_input(18) else ''}\n"
            f"     i4 ({self.i4}) -|4        17|- io17 ({self.io17}){' <-' if self.is_input(17) else ''}\n"
            f"     i5 ({self.i5}) -|5  PAL   16|- io16 ({self.io16}){' <-' if self.is_input(16) else ''}\n"
            f"     i6 ({self.i6}) -|6  16L8  15|- io15 ({self.io15}){' <-' if self.is_input(15) else ''}\n"
            f"     i7 ({self.i7}) -|7        14|- io14 ({self.io14}){' <-' if self.is_input(14) else ''}\n"
            f"     i8 ({self.i8}) -|8        13|- io13 ({self.io13}){' <-' if self.is_input(13) else ''}\n"
            f"     i9 ({self.i9}) -|9        12|- o12  ({self.o12})\n"
            f"        GND -|10       11|- i11  ({self.i11})\n"
            f"             +-----------+\n\n"
            f"Inputs:  {self.inputs_as_byte}\n"
            f"Outputs: {self.outputs_as_byte}"
        )

    @property
    def input_count(self) -> int:
        return 10 + (6 - bin(self._output_mask).count("1"))

    @property
    def output_count(self) -> int:
        return 2 + bin(self._output_mask).count("1")

    def get_inputs(self, idx: int) -> int:
        return idx  # WARNME


class Pal10L8(Pal16L8):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return (
            f"             +-----_-----+\n"
            f"     i1 ({self.i1}) -|1        20|- VCC\n"
            f"     i2 ({self.i2}) -|2        19|- o19 ({self.o19})\n"
            f"     i3 ({self.i3}) -|3        18|- o18 ({self.io18})\n"
            f"     i4 ({self.i4}) -|4        17|- o17 ({self.io17})\n"
            f"     i5 ({self.i5}) -|5  PAL   16|- o16 ({self.io16})\n"
            f"     i6 ({self.i6}) -|6  10L8  15|- o15 ({self.io15})\n"
            f"     i7 ({self.i7}) -|7        14|- o14 ({self.io14})\n"
            f"     i8 ({self.i8}) -|8        13|- o13 ({self.io13})\n"
            f"     i9 ({self.i9}) -|9        12|- o12 ({self.o12})\n"
            f"        GND -|10       11|- i11 ({self.i11})\n"
            f"             +-----------+\n\n"
            f"Inputs:  {self.inputs_as_byte}\n"
            f"Outputs: {self.outputs_as_byte}"
        )


class Pal16R4Base:
    def __init__(self, output_mask: int = 0b1111):  # output mask: pins 19, 18, 13, 12
        self._output_mask = output_mask
        # input pins
        self.i2: int = 0
        self.i3: int = 0
        self.i4: int = 0
        self.i5: int = 0
        self.i6: int = 0
        self.i7: int = 0
        self.i8: int = 0
        self.i9: int = 0
        # registered outputs
        self.o14: int = 0
        self.o15: int = 0
        self.o16: int = 0
        self.o17: int = 0
        # I/O pins
        self.io12: int = 0
        self.io13: int = 0
        self.io18: int = 0
        self.io19: int = 0
        # inputs into registers
        self.ro14: Optional[int] = None
        self.ro15: Optional[int] = None
        self.ro16: Optional[int] = None
        self.ro17: Optional[int] = None

    @property
    def i12(self):
        return (self._output_mask & 1) == 0

    @property
    def i13(self):
        return (self._output_mask & 2) == 0

    @property
    def i18(self):
        return (self._output_mask & 4) == 0

    @property
    def i19(self):
        return (self._output_mask & 8) == 0

    @property
    def output_mask(self):
        return self._output_mask

    def set_inputs(self, val: int):
        self.i2 = (val >> 0) & 1
        self.i3 = (val >> 1) & 1
        self.i4 = (val >> 2) & 1
        self.i5 = (val >> 3) & 1
        self.i6 = (val >> 4) & 1
        self.i7 = (val >> 5) & 1
        self.i8 = (val >> 6) & 1
        self.i9 = (val >> 7) & 1
        if self.i12:
            self.io12 = (val >> 8) & 1
        if self.i13:
            self.io13 = (val >> 9) & 1
        if self.i18:
            self.io18 = (val >> 10) & 1
        if self.i19:
            self.io19 = (val >> 11) & 1

    @property
    def inputs_as_byte(self) -> int:
        inputs = (
            (self.i2 << 0)
            | (self.i3 << 1)
            | (self.i4 << 2)
            | (self.i5 << 3)
            | (self.i6 << 4)
            | (self.i7 << 5)
            | (self.i8 << 6)
            | (self.i9 << 7)
        )
        if self.i12:
            inputs |= self.io12 << 8
        if self.i13:
            inputs |= self.io13 << 9
        if self.i18:
            inputs |= self.io18 << 10
        if self.i19:
            inputs |= self.io19 << 11
        return inputs

    @property
    def outputs_as_byte(self) -> int:
        outputs = (
            (self.o17 << 1)
            | (self.o16 << 2)
            | (self.o15 << 3)
            | (self.o14 << 4)
        )
        if not self.i12:
            outputs |= self.io12 << 7
        if not self.i13:
            outputs |= self.io13 << 5
        if not self.i18:
            outputs |= self.io18 << 0
        if not self.i19:
            outputs |= self.io19 << 6
        return outputs

    def read_outputs(self) -> int:
        raise NotImplementedError

    def clock(self) -> int:
        self.o17 = self.ro17
        self.o16 = self.ro16
        self.o15 = self.ro15
        self.o14 = self.ro14
        return self.outputs_as_byte

    def __str__(self):
        return (
            f"             +-----_-----+\n"
            f"        clk -|1        20|- vcc\n"
            f"     i2 ({self.i2}) -|2        19|- io19 ({self.io19}){' <-' if self.io19_in else ''}\n"
            f"     i3 ({self.i3}) -|3        18|- io18 ({self.io18}){' <-' if self.io18_in else ''}\n"
            f"     i4 ({self.i4}) -|4        17|  ro17 ({self.ro17 if self.ro17 is not None else '?'}) - o17 ({self.o17})\n"
            f"     i5 ({self.i5}) -|5  PAL   16|  ro16 ({self.ro16 if self.ro16 is not None else '?'}) - o16 ({self.o16})\n"
            f"     i6 ({self.i6}) -|6  16R4  15|  ro15 ({self.ro15 if self.ro15 is not None else '?'}) - o15 ({self.o15})\n"
            f"     i7 ({self.i7}) -|7        14|  ro14 ({self.ro14 if self.ro14 is not None else '?'}) - o14 ({self.o14})\n"
            f"     i8 ({self.i8}) -|8        13|- io13 ({self.io13}){' <-' if self.io13_in else ''}\n"
            f"     i9 ({self.i9}) -|9        12|- io12 ({self.io12}){' <-' if self.io12_in else ''}\n"
            f"        gnd -|10       11|- oe\n"
            f"             +-----------+\n"
        )


class Pal16R4DuPAL(Pal16R4Base):
    def __init__(self, port: str, output_mask: int = 0b1111):
        super().__init__(output_mask=output_mask)
        self.client = DuPALClient(port=port)
        self.client.init_board()
        self.client.control_led(1, 1)
        self.read_outputs()

    #   31   30   29   28   27   26   25   24
    # .----.----.----.----.----.----.----.----.
    # | xx | xx | xx | xx | xx | xx | xx | xx | Byte 3
    # '----'----'----'----'----'----'----'----'
    #
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
    def _dupal_inputs(self, inputs):
        val = inputs << 1
        if self.i12:
            inputs |= 1 << 17
        if self.i13:
            inputs |= 1 << 15
        if self.i18:
            inputs |= 1 << 10
        if self.i19:
            inputs |= 1 << 16
        return val

    def set_inputs(self, val: int):
        super().set_inputs(val)
        self.client.write_status(self._dupal_inputs(val))

    def read_outputs(self) -> int:
        val = self.client.read_status()
        self.io18 = ((val >> 0) & 1) if not self.i18 else 0
        self.o17 = (val >> 1) & 1
        self.o16 = (val >> 2) & 1
        self.o15 = (val >> 3) & 1
        self.o14 = (val >> 4) & 1
        self.io13 = ((val >> 5) & 1) if not self.i13 else 0
        self.io19 = ((val >> 6) & 1) if not self.i19 else 0
        self.io12 = ((val >> 7) & 1) if not self.i12 else 0
        return self.outputs_as_byte

    def clock(self) -> int:
        inputs = self.inputs_as_byte
        self.client.write_status(self._dupal_inputs(inputs) | 1)  # with clock bit
        self.client.write_status(self._dupal_inputs(inputs))  # no clock bit
        return self.outputs_as_byte
