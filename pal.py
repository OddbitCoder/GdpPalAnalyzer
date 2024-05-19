import time
from typing import Optional

from dupal_client import DuPALClient


class Pal16R4Base:
    def __init__(self):
        self.i2: int = 0
        self.i3: int = 0
        self.i4: int = 0
        self.i5: int = 0
        self.i6: int = 0
        self.i7: int = 0
        self.i8: int = 0
        self.i9: int = 0
        self.io12: int = 0
        self.io13: int = 0
        self.o14: int = 0
        self.o15: int = 0
        self.o16: int = 0
        self.o17: int = 0
        self.io18: int = 0
        self.io19: int = 0

        # registers
        self.ro14: int = 0
        self.ro15: int = 0
        self.ro16: int = 0
        self.ro17: int = 0

    def __str__(self):
        return (
            f"            +-----U-----+\n"
            f"        clk |1        20| vcc\n"
            f"     i2 ({self.i2}) |2        19| io19 ({self.io19})\n"
            f"     i3 ({self.i3}) |3        18| io18 ({self.io18})\n"
            f"     i4 ({self.i4}) |4        17| ro17 ({self.ro17}) --(D)-- o17 ({self.o17})\n"
            f"     i5 ({self.i5}) |5  PAL   16| ro16 ({self.ro16}) --(D)-- o16 ({self.o16})\n"
            f"     i6 ({self.i6}) |6  16R4  15| ro15 ({self.ro15}) --(D)-- o15 ({self.o15})\n"
            f"     i7 ({self.i7}) |7        14| ro14 ({self.ro14}) --(D)-- o14 ({self.o14})\n"
            f"     i8 ({self.i8}) |8        13| io13 ({self.io13})\n"
            f"     i9 ({self.i9}) |9        12| io12 ({self.io12})\n"
            f"        gnd |10       11| oe\n"
            f"            +-----------+\n"
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

    def read_outputs(self):
        raise NotImplementedError

    def clock(self):
        self.o17 = self.ro17
        self.o16 = self.ro16
        self.o15 = self.ro15
        self.o14 = self.ro14


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
        self._outputs = 0

    def _reset_board(self):
        serial = self.client.serial
        if serial.is_open:
            serial.dtr = True
            time.sleep(1)
            serial.dtr = False

    def set_inputs(self, val: int):
        super().set_inputs(val)
        self.client.write_status(val << 1)

    def read_outputs(self):
        val = self.client.read_status()
        self.io18 = (val >> 0) & 1
        self.o17 = (val >> 1) & 1
        self.o16 = (val >> 2) & 1
        self.o15 = (val >> 3) & 1
        self.o14 = (val >> 4) & 1
        self.io13 = (val >> 5) & 1
        self.io19 = (val >> 6) & 1
        self.io12 = (val >> 7) & 1

    def clock(self):
        inputs = self.inputs_as_byte
        self.client.write_status((inputs << 1) | 1)  # with clock bit
        self.client.write_status(inputs << 1)  # no clock bit


class Pal16R4IC12(Pal16R4Base):
    def __init__(self):
        super().__init__()
        self.i2 = 0
        self.i3 = 0
        self.i4 = 0
        self.i5 = 0
        self.i6 = 0
        self.i7 = 0
        self.i8 = 0
        self.i9 = 0
        self.io12 = 1
        self.io13 = 1
        self.ro14 = 0
        self.ro15 = 1
        self.ro16 = 1
        self.ro17 = 0
        self.io18 = 0
        self.io19 = 1

        # registers
        self.o14 = 1
        self.o15 = 1
        self.o16 = 1
        self.o17 = 1

    def read_outputs(self, outputs: Optional[int] = None):
        i2 = self.i2
        i3 = self.i3
        i4 = self.i4
        i5 = self.i5
        i6 = self.i6
        i7 = self.i7
        i8 = self.i8
        i9 = self.i9
        fio18 = self.io18
        fio19 = self.io19
        fio12 = self.io12
        fio13 = self.io13
        psro17 = self.o17
        psro16 = self.o16
        psro15 = self.o15
        psro14 = self.o14

        if outputs is not None:
            print(f"given outputs: {outputs}")

            self.io18 = (outputs >> 0) & 1
            self.o17 = (outputs >> 1) & 1
            self.o16 = (outputs >> 2) & 1
            self.o15 = (outputs >> 3) & 1
            self.o14 = (outputs >> 4) & 1
            self.io13 = (outputs >> 5) & 1
            self.io19 = (outputs >> 6) & 1
            self.io12 = (outputs >> 7) & 1

            psro17 = self.o17
            psro16 = self.o16
            psro15 = self.o15
            psro14 = self.o14

        new_io18 = int(
            not (
                (not fio18 and not fio19)
                or (not fio18 and not fio12)
                or (fio13 and not fio12)
                or (not fio19 and not fio12)
                or (not psro17 and not psro16)
                or (not psro15 and psro14)
                or (not fio13 and fio12 and psro16)
                or (not i3 and not i4 and not i5 and not i6)
            )
        )

        new_io13 = int(
            not (
                (not fio18 and not fio19)
                or (not fio18 and not fio12)
                or (fio13 and not fio12)
                or (not fio19 and not fio12)
                or (not psro17 and not psro16)
                or (not psro15 and psro14)
                or (not fio13 and fio12 and psro16)
                or (not i3 and not i4 and i5)
                or (i7 and not psro16)
            )
        )

        new_io19 = int(
            not (
                (not fio18 and not fio19)
                or (not fio18 and not fio12)
                or (fio13 and not fio12)
                or (not fio19 and not fio12)
                or (not psro17 and not psro16)
                or (not psro15 and psro14)
                or (not fio13 and fio12 and psro16)
                or (i3 and not i4 and not i5 and not i6)
            )
        )

        new_io12 = int(
            not (
                (not fio18 and not fio19)
                or (not fio18 and not fio12)
                or (fio13 and not fio12)
                or (not fio19 and not fio12)
                or (not psro17 and not psro16)
                or (not psro15 and psro14)
                or (not fio13 and fio12 and psro16)
                or (not i3 and not i4 and i5)
            )
        )

        self.ro17 = int(
            not (
                (not i5 and not i8)
                or (i3 and not i4 and not i5 and not i6 and fio19)
                or (not i3 and not i4 and not i6 and fio18 and fio12)
                or (not i3 and not i4 and i5 and fio13)
                or (not i3 and not i4 and i5 and fio12)
                or (i7 and fio13 and not psro16)
                or (not fio13 and fio12 and psro16)
                or (not i7 and not fio13 and fio12)
                or (not psro15 and psro14)
                or (not psro17 and not psro16)
                or (i3 and not fio12)
                or (i4 and not fio12)
                or (i6 and not fio19)
                or (i6 and not fio18)
                or (not i5 and not fio12)
                or (i4 and not fio19)
                or (i4 and not fio18)
                or (not fio18 and not fio19)
                or (i5 and not fio19)
                or (i5 and not fio18)
            )
        )

        self.ro16 = int(
            not (
                (not i5 and not i6 and i7 and i8)
                or (i3 and not i4 and not i5 and not i6 and fio19)
                or (not i3 and not i4 and not i6 and fio18 and fio12)
                or (not i3 and not i4 and i5 and fio13)
                or (not i3 and not i4 and i5 and fio12)
                or (i7 and fio13 and not psro16)
                or (not fio13 and fio12 and psro16)
                or (not i7 and not fio13 and fio12)
                or (not psro15 and psro14)
                or (not psro17 and not psro16)
                or (i3 and not fio12)
                or (i4 and not fio12)
                or (i6 and not fio19)
                or (i6 and not fio18)
                or (not i5 and not fio12)
                or (i4 and not fio19)
                or (i4 and not fio18)
                or (not fio18 and not fio19)
                or (i5 and not fio19)
                or (i5 and not fio18)
            )
        )

        self.ro15 = int(
            not (
                (not i2 and psro14)
                or (i3 and not i4 and not i5 and not i6 and fio19)
                or (not i3 and not i4 and not i6 and fio18 and fio12)
                or (not i3 and not i4 and i5 and fio13)
                or (not i3 and not i4 and i5 and fio12)
                or (i7 and fio13 and not psro16)
                or (not fio13 and fio12 and psro16)
                or (not i7 and not fio13 and fio12)
                or (not psro15 and psro14)
                or (not psro17 and not psro16)
                or (i3 and not fio12)
                or (i4 and not fio12)
                or (i6 and not fio19)
                or (i6 and not fio18)
                or (not i5 and not fio12)
                or (i4 and not fio19)
                or (i4 and not fio18)
                or (not fio18 and not fio19)
                or (i5 and not fio19)
                or (i5 and not fio18)
            )
        )

        self.ro14 = int(
            not (
                (i3 and not i4 and not i5 and not i6 and fio19)
                or (not i3 and not i4 and not i6 and fio18 and fio12)
                or (not i2)
                or (not i3 and not i4 and i5 and fio13)
                or (not i3 and not i4 and i5 and fio12)
                or (i7 and fio13 and not psro16)
                or (not fio13 and fio12 and psro16)
                or (not i7 and not fio13 and fio12)
                or (not psro15 and psro14)
                or (not psro17 and not psro16)
                or (i3 and not fio12)
                or (i4 and not fio12)
                or (i6 and not fio19)
                or (i6 and not fio18)
                or (not i5 and not fio12)
                or (i4 and not fio19)
                or (i4 and not fio18)
                or (not fio18 and not fio19)
                or (i5 and not fio19)
                or (i5 and not fio18)
            )
        )

        if outputs:
            print(f"io19 {self.io19} : {new_io19}")
            print(f"io18 {self.io18} : {new_io18}")
            print(f"io13 {self.io13} : {new_io13}")
            print(f"io12 {self.io12} : {new_io12}")
            print(
                f"{i2}{i3}{i4}{i5}{i6}{i7}{i8}{i9}{fio18}{fio13}{fio19}{fio12}{psro17}{psro16}{psro15}{psro14}"
            )
        else:
            self.io18 = new_io18
            self.io13 = new_io13
            self.io19 = new_io19
            self.io12 = new_io12
