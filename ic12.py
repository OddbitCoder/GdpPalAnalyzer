from pal import Pal16R4Base


class IC12(Pal16R4Base):
    def __init__(self):
        super().__init__()
        # set initial state
        self.io19 = 1
        self.io13 = 1
        self.io12 = 1
        self.ro16 = 1
        self.ro17 = 0
        self.ro15 = 1
        self.ro14 = 0
        # all outputs from registers are 1 before clock
        self.o14 = 1
        self.o15 = 1
        self.o16 = 1
        self.o17 = 1

        self.prev_outputs = self.outputs_as_byte

    def read_outputs(self) -> int:
        i2 = self.i2
        i3 = self.i3
        i4 = self.i4
        i5 = self.i5
        i6 = self.i6
        i7 = self.i7
        i8 = self.i8
        i9 = self.i9
        fio12 = self.io12
        fio13 = self.io13
        fio18 = self.io18
        fio19 = self.io19
        r14 = self.o14
        r15 = self.o15
        r16 = self.o16
        r17 = self.o17

        self.prev_outputs = self.outputs_as_byte

        self.io12 = int(
            not (
                (i5 and not i4 and not i3)
                or (fio12 and not fio13 and r16)
                or (not fio12 and fio13)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
                or (not fio12 and not fio18)
                or (not r16 and not r17)
                or (r14 and not r15)
            )
        )

        self.io19 = int(
            not (
                (not i6 and not i5 and not i4 and i3)
                or (fio12 and not fio13 and r16)
                or (not fio12 and fio13)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
                or (not fio12 and not fio18)
                or (not r16 and not r17)
                or (r14 and not r15)
            )
        )

        self.io13 = int(
            not (
                (i5 and not i4 and not i3)
                or (not r16 and i7)
                or (fio12 and not fio13 and r16)
                or (not fio12 and fio13)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
                or (not fio12 and not fio18)
                or (not r16 and not r17)
                or (r14 and not r15)
            )
        )

        self.ro14 = int(
            not (
                (not i2)
                or (fio12 and not fio13 and r16)
                or (not fio12 and fio13)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
                or (not fio12 and not fio18)
                or (not r16 and not r17)
                or (r14 and not r15)
            )
        )

        self.ro15 = int(
            not (
                (not fio13 and not r15 and not r17 and i9 and i8 and i4 and not i2)
                or (not fio13 and not r15 and not r17 and i9 and i8 and i3 and not i2)
                or (not fio13 and not r15 and not r17 and i9 and i7 and i4 and not i2)
                or (not fio13 and not r15 and not r17 and i9 and i7 and i3 and not i2)
                or (
                    not fio13
                    and not r15
                    and not r17
                    and i9
                    and i8
                    and not i5
                    and not i2
                )
                or (
                    not fio13
                    and not r15
                    and not r17
                    and i9
                    and i7
                    and not i5
                    and not i2
                )
                or (not r15 and not r17 and not fio18 and i6 and not i2)
                or (not r15 and not r17 and not fio18 and i5 and not i2)
                or (not r15 and not r17 and not fio18 and i4 and not i2)
                or (not r15 and not r17 and not fio18 and i3 and not i2)
                or (r14 and not i2)
                or (fio12 and not fio13 and r16)
                or (not fio12 and fio13)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
                or (not fio12 and not fio18)
                or (not r16 and not r17)
                or (r14 and not r15)
            )
        )

        self.ro16 = int(
            not (
                (i8 and i7 and not i6 and not i5)
                or (fio12 and not fio13 and r16)
                or (not fio12 and fio13)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
                or (not fio12 and not fio18)
                or (not r16 and not r17)
                or (r14 and not r15)
            )
        )

        self.ro17 = int(
            not (
                (not i8 and not i5)
                or (fio12 and not fio13 and r16)
                or (not fio12 and fio13)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
                or (not fio12 and not fio18)
                or (not r16 and not r17)
                or (r14 and not r15)
            )
        )

        self.io18 = int(
            not (
                (not i6 and not i5 and not i4 and not i3)
                or (fio12 and not fio13 and r16)
                or (not fio12 and fio13)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
                or (not fio12 and not fio18)
                or (not r16 and not r17)
                or (r14 and not r15)
            )
        )

        return self.outputs_as_byte

    def __str__(self):
        _str = super().__str__()
        outputs = f"{self.outputs_as_byte:08b}"
        _str += f"{self.prev_outputs:08b}{self.inputs_as_byte:08b} -> {outputs[:3]}({outputs[3:7]}){outputs[7:]}\n"
        return _str
