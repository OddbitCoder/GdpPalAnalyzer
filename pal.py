import time
from typing import Optional

from dupal_client import DuPALClient


class Pal16R4Base:
    def __init__(self, output_mask: int = 0b1111):  # output mask: pins 19, 18, 13, 12
        self.output_mask = output_mask
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
    def io12_in(self):
        return self.output_mask & 1 == 0

    @property
    def io13_in(self):
        return self.output_mask & 2 == 0

    @property
    def io18_in(self):
        return self.output_mask & 4 == 0

    @property
    def io19_in(self):
        return self.output_mask & 8 == 0

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

    def set_inputs(self, val: int):
        self.i2 = (val >> 0) & 1
        self.i3 = (val >> 1) & 1
        self.i4 = (val >> 2) & 1
        self.i5 = (val >> 3) & 1
        self.i6 = (val >> 4) & 1
        self.i7 = (val >> 5) & 1
        self.i8 = (val >> 6) & 1
        self.i9 = (val >> 7) & 1
        if self.io12_in:
            self.io12 = (val >> 8) & 1
        if self.io13_in:
            self.io13 = (val >> 9) & 1
        if self.io18_in:
            self.io18 = (val >> 10) & 1
        if self.io19_in:
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
        if self.io12_in:
            inputs |= self.io12 << 8
        if self.io13_in:
            inputs |= self.io13 << 9
        if self.io18_in:
            inputs |= self.io18 << 10
        if self.io19_in:
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
        if not self.io12_in:
            outputs |= self.io12 << 7
        if not self.io13_in:
            outputs |= self.io13 << 5
        if not self.io18_in:
            outputs |= self.io18 << 0
        if not self.io19_in:
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


class Pal16R4DuPAL(Pal16R4Base):
    def __init__(self, port: str):
        super().__init__()
        self.client = DuPALClient(port=port)
        self._reset_board()
        self.client.send_command("x")
        self.client.receive_response()  # "DuPAL - 0.1.2"
        self.client.receive_response()  # empty line
        self.client.receive_response()  # "REMOTE_CONTROL_ENABLED"
        self.client.control_led(1, 1)
        self.read_outputs()

    def _reset_board(self):
        serial = self.client.serial
        if serial.is_open:
            serial.dtr = True
            time.sleep(1)
            serial.dtr = False

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
        if self.io12_in:
            inputs |= 1 << 17
        if self.io13_in:
            inputs |= 1 << 15
        if self.io18_in:
            inputs |= 1 << 10
        if self.io19_in:
            inputs |= 1 << 16
        return val

    def set_inputs(self, val: int):
        super().set_inputs(val)
        self.client.write_status(self._dupal_inputs(val))

    def read_outputs(self) -> int:
        val = self.client.read_status()
        self.io18 = (val >> 0) & 1 if not self.io18_in else 0
        self.o17 = (val >> 1) & 1
        self.o16 = (val >> 2) & 1
        self.o15 = (val >> 3) & 1
        self.o14 = (val >> 4) & 1
        self.io13 = (val >> 5) & 1 if not self.io13_in else 0
        self.io19 = (val >> 6) & 1 if not self.io19_in else 0
        self.io12 = (val >> 7) & 1 if not self.io12_in else 0
        return self.outputs_as_byte

    def clock(self) -> int:
        inputs = self.inputs_as_byte
        self.client.write_status(self._dupal_inputs(inputs) | 1)  # with clock bit
        self.client.write_status(self._dupal_inputs(inputs))  # no clock bit
        return self.outputs_as_byte
