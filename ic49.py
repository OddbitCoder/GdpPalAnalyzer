from pal import Pal16R4Base


class IC49(Pal16R4Base):
    def __init__(self):
        super().__init__()
        # set initial state
        self.io19 = 1  # TODO
        self.io13 = 1  # TODO
        self.io12 = 1  # TODO
        self.ro16 = 1  # TODO
        self.ro17 = 0  # TODO
        self.ro15 = 1  # TODO
        self.ro14 = 0  # TODO
        # all outputs from registers are 1 before clock
        self.o14 = 1
        self.o15 = 1
        self.o16 = 1
        self.o17 = 1

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

        self.io12 = int(
            not (
                (
                    fio12
                    and fio19
                    and not fio13
                    and r16
                    and not i6
                    and not i5
                    and not i4
                    and i3
                )
                or (i5 and not i4 and not i3)
                or (
                    fio12
                    and not fio13
                    and r16
                    and fio18
                    and not i6
                    and not i4
                    and not i3
                )
                or (fio12 and not fio13 and r14 and r16 and not i2)
                or (fio12 and not fio13 and r16 and r17 and not i8 and not i5)
                or (fio12 and not fio13 and r16 and i8 and not i6 and not i5)
                or (fio12 and not fio13 and not r14 and r16 and i2)
                or (not fio19 and not fio13 and r16 and i4)
                or (not fio19 and not fio13 and r16 and i6)
                or (fio12 and not fio13 and not r17 and i5)
                or (fio12 and not fio13 and not r17 and i8)
                or (not fio13 and r16 and not fio18 and i4)
                or (not fio13 and r16 and not fio18 and i6)
                or (not fio19 and not fio13 and r16 and r17)
                or (not fio13 and r16 and not fio18 and i3)
                or (fio12 and not fio13 and r16 and not i7)
                or (r14 and not r15)
                or (not fio12 and fio13)
                or (not r16 and not r17)
                or (not fio12 and not fio18)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
            )
        )

        self.io19 = int(
            not (
                (not i6 and not i5 and not i4 and i3)
                or (
                    fio12
                    and not fio13
                    and r16
                    and fio18
                    and not i6
                    and not i4
                    and not i3
                )
                or (fio12 and not fio13 and r16 and i5 and not i4 and not i3)
                or (fio12 and not fio13 and r14 and r16 and not i2)
                or (fio12 and not fio13 and r16 and r17 and not i8 and not i5)
                or (fio12 and not fio13 and r16 and i8 and not i6 and not i5)
                or (fio12 and not fio13 and not r14 and r16 and i2)
                or (not fio19 and not fio13 and r16 and i4)
                or (not fio19 and not fio13 and r16 and i6)
                or (fio12 and not fio13 and not r17 and i5)
                or (fio12 and not fio13 and not r17 and i8)
                or (not fio13 and r16 and not fio18 and i4)
                or (not fio13 and r16 and not fio18 and i6)
                or (not fio19 and not fio13 and r16 and r17)
                or (not fio13 and r16 and not fio18 and i3)
                or (fio12 and not fio13 and r16 and not i7)
                or (r14 and not r15)
                or (not fio12 and fio13)
                or (not r16 and not r17)
                or (not fio12 and not fio18)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
            )
        )

        self.io13 = int(
            not (
                (
                    fio12
                    and fio19
                    and not fio13
                    and r16
                    and not i6
                    and not i5
                    and not i4
                    and i3
                )
                or (not r16 and i7)
                or (i5 and not i4 and not i3)
                or (
                    fio12
                    and not fio13
                    and r16
                    and fio18
                    and not i6
                    and not i4
                    and not i3
                )
                or (fio12 and not fio13 and r14 and r16 and not i2)
                or (fio12 and not fio13 and r16 and r17 and not i8 and not i5)
                or (fio12 and not fio13 and r16 and i8 and not i6 and not i5)
                or (fio12 and not fio13 and not r14 and r16 and i2)
                or (not fio19 and not fio13 and r16 and i4)
                or (not fio19 and not fio13 and r16 and i6)
                or (fio12 and not fio13 and not r17 and i5)
                or (fio12 and not fio13 and not r17 and i8)
                or (not fio13 and r16 and not fio18 and i4)
                or (not fio13 and r16 and not fio18 and i6)
                or (not fio19 and not fio13 and r16 and r17)
                or (not fio13 and r16 and not fio18 and i3)
                or (fio12 and not fio13 and r16 and not i7)
                or (r14 and not r15)
                or (not fio12 and fio13)
                or (not r16 and not r17)
                or (not fio12 and not fio18)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
            )
        )

        self.ro14 = int(
            not (
                (
                    fio12
                    and fio19
                    and not fio13
                    and r16
                    and not i6
                    and not i5
                    and not i4
                    and i3
                )
                or (
                    fio12
                    and not fio13
                    and r16
                    and fio18
                    and not i6
                    and not i4
                    and not i3
                )
                or (not i2)
                or (fio12 and not fio13 and r16 and i5 and not i4 and not i3)
                or (fio12 and not fio13 and r16 and r17 and not i8 and not i5)
                or (fio12 and not fio13 and r16 and i8 and not i6 and not i5)
                or (fio12 and not fio13 and not r14 and r16 and i2)
                or (not fio19 and not fio13 and r16 and i4)
                or (not fio19 and not fio13 and r16 and i6)
                or (fio12 and not fio13 and not r17 and i5)
                or (fio12 and not fio13 and not r17 and i8)
                or (not fio13 and r16 and not fio18 and i4)
                or (not fio13 and r16 and not fio18 and i6)
                or (not fio19 and not fio13 and r16 and r17)
                or (not fio13 and r16 and not fio18 and i3)
                or (fio12 and not fio13 and r16 and not i7)
                or (r14 and not r15)
                or (not fio12 and fio13)
                or (not r16 and not r17)
                or (not fio12 and not fio18)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
            )
        )

        self.ro15 = int(
            not (
                (
                    fio12
                    and fio19
                    and not fio13
                    and r16
                    and not i6
                    and not i5
                    and not i4
                    and i3
                )
                or (r14 and not i2)
                or (
                    fio12
                    and not fio13
                    and r16
                    and fio18
                    and not i6
                    and not i4
                    and not i3
                )
                or (fio12 and not fio13 and r16 and i5 and not i4 and not i3)
                or (fio12 and not fio13 and r16 and r17 and not i8 and not i5)
                or (fio12 and not fio13 and r16 and i8 and not i6 and not i5)
                or (fio12 and not fio13 and not r14 and r16 and i2)
                or (not fio19 and not fio13 and r16 and i4)
                or (not fio19 and not fio13 and r16 and i6)
                or (fio12 and not fio13 and not r17 and i5)
                or (fio12 and not fio13 and not r17 and i8)
                or (not fio13 and r16 and not fio18 and i4)
                or (not fio13 and r16 and not fio18 and i6)
                or (not fio19 and not fio13 and r16 and r17)
                or (not fio13 and r16 and not fio18 and i3)
                or (fio12 and not fio13 and r16 and not i7)
                or (r14 and not r15)
                or (not fio12 and fio13)
                or (not r16 and not r17)
                or (not fio12 and not fio18)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
            )
        )

        self.ro16 = int(
            not (
                (i8 and i7 and not i6 and not i5)
                or (
                    fio12
                    and fio19
                    and not fio13
                    and r16
                    and not i6
                    and not i5
                    and not i4
                    and i3
                )
                or (
                    fio12
                    and not fio13
                    and r16
                    and fio18
                    and not i6
                    and not i4
                    and not i3
                )
                or (fio12 and not fio13 and r16 and i5 and not i4 and not i3)
                or (fio12 and not fio13 and r14 and r16 and not i2)
                or (fio12 and not fio13 and r16 and r17 and not i8 and not i5)
                or (fio12 and not fio13 and not r14 and r16 and i2)
                or (not fio19 and not fio13 and r16 and i4)
                or (not fio19 and not fio13 and r16 and i6)
                or (fio12 and not fio13 and not r17 and i5)
                or (fio12 and not fio13 and not r17 and i8)
                or (not fio13 and r16 and not fio18 and i4)
                or (not fio13 and r16 and not fio18 and i6)
                or (not fio19 and not fio13 and r16 and r17)
                or (not fio13 and r16 and not fio18 and i3)
                or (fio12 and not fio13 and r16 and not i7)
                or (r14 and not r15)
                or (not fio12 and fio13)
                or (not r16 and not r17)
                or (not fio12 and not fio18)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
            )
        )

        self.ro17 = int(
            not (
                (not i8 and not i5)
                or (fio12 and not fio13 and r16 and i5 and not i4 and not i3)
                or (fio12 and not fio13 and r14 and r16 and not i2)
                or (fio12 and not fio13 and r16 and i8 and not i6 and not i5)
                or (fio12 and not fio13 and not r14 and r16 and i2)
                or (fio12 and not fio13 and not r17 and i5)
                or (fio12 and not fio13 and not r17 and i8)
                or (not fio13 and r16 and not fio18 and i4)
                or (not fio13 and r16 and not fio18 and i6)
                or (not fio19 and not fio13 and r16 and r17)
                or (not fio13 and r16 and not fio18 and i3)
                or (fio12 and not fio13 and r16 and not i7)
                or (r14 and not r15)
                or (not fio12 and fio13)
                or (not r16 and not r17)
                or (not fio12 and not fio18)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
            )
        )

        self.io18 = int(
            not (
                (not i6 and not i5 and not i4 and not i3)
                or (
                    fio12
                    and fio19
                    and not fio13
                    and r16
                    and not i6
                    and not i5
                    and not i4
                    and i3
                )
                or (fio12 and not fio13 and r16 and i5 and not i4 and not i3)
                or (fio12 and not fio13 and r14 and r16 and not i2)
                or (fio12 and not fio13 and r16 and r17 and not i8 and not i5)
                or (fio12 and not fio13 and r16 and i8 and not i6 and not i5)
                or (fio12 and not fio13 and not r14 and r16 and i2)
                or (not fio19 and not fio13 and r16 and i4)
                or (not fio19 and not fio13 and r16 and i6)
                or (fio12 and not fio13 and not r17 and i5)
                or (fio12 and not fio13 and not r17 and i8)
                or (not fio13 and r16 and not fio18 and i4)
                or (not fio13 and r16 and not fio18 and i6)
                or (not fio19 and not fio13 and r16 and r17)
                or (not fio13 and r16 and not fio18 and i3)
                or (fio12 and not fio13 and r16 and not i7)
                or (r14 and not r15)
                or (not fio12 and fio13)
                or (not r16 and not r17)
                or (not fio12 and not fio18)
                or (not fio12 and not fio19)
                or (not fio19 and not fio18)
            )
        )

        return self.outputs_as_byte
