import time
from typing import Optional

from dupal_client import DuPALClient


class Pal16R4Base:
    def __init__(self):
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
        self.o14: int = 0
        self.o15: int = 0
        self.o16: int = 0
        self.o17: int = 0
        self.io18: int = 0
        self.io19: int = 0
        # inputs into registers
        self.ro14: Optional[int] = None
        self.ro15: Optional[int] = None
        self.ro16: Optional[int] = None
        self.ro17: Optional[int] = None

    def __str__(self):
        return (
            f"             +-----_-----+\n"
            f"        clk -|1        20|- vcc\n"
            f"     i2 ({self.i2}) -|2        19|- io19 ({self.io19})\n"
            f"     i3 ({self.i3}) -|3        18|- io18 ({self.io18})\n"
            f"     i4 ({self.i4}) -|4        17|  ro17 ({self.ro17 if self.ro17 is not None else '?'}) - o17 ({self.o17})\n"
            f"     i5 ({self.i5}) -|5  PAL   16|  ro16 ({self.ro16 if self.ro16 is not None else '?'}) - o16 ({self.o16})\n"
            f"     i6 ({self.i6}) -|6  16R4  15|  ro15 ({self.ro15 if self.ro15 is not None else '?'}) - o15 ({self.o15})\n"
            f"     i7 ({self.i7}) -|7        14|  ro14 ({self.ro14 if self.ro14 is not None else '?'}) - o14 ({self.o14})\n"
            f"     i8 ({self.i8}) -|8        13|- io13 ({self.io13})\n"
            f"     i9 ({self.i9}) -|9        12|- io12 ({self.io12})\n"
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

    def _reset_board(self):
        serial = self.client.serial
        if serial.is_open:
            serial.dtr = True
            time.sleep(1)
            serial.dtr = False

    def set_inputs(self, val: int):
        super().set_inputs(val)
        self.client.write_status(val << 1)

    def read_outputs(self) -> int:
        val = self.client.read_status()
        self.io18 = (val >> 0) & 1
        self.o17 = (val >> 1) & 1
        self.o16 = (val >> 2) & 1
        self.o15 = (val >> 3) & 1
        self.o14 = (val >> 4) & 1
        self.io13 = (val >> 5) & 1
        self.io19 = (val >> 6) & 1
        self.io12 = (val >> 7) & 1
        return self.outputs_as_byte

    def clock(self) -> int:
        inputs = self.inputs_as_byte
        self.client.write_status((inputs << 1) | 1)  # with clock bit
        self.client.write_status(inputs << 1)  # no clock bit
        return self.outputs_as_byte
