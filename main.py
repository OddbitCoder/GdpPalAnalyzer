from enum import Enum

from analyzer import PalRAnalyzer, PalLAnalyzer
from pal import DuPalBoard, IC49, IC24, IC22, IC7, IC12, PalType

class Mode(Enum):
    # 10L8
    READ_IC24 = 1
    CONVERT_IC24 = 2
    VALIDATE_IC24 = 3
    # 16L8
    READ_IC22 = 4
    CONVERT_IC22 = 5
    VALIDATE_IC22 = 6
    # 16L8 + HI-Z
    READ_IC7 = 7
    CONVERT_IC7 = 8
    VALIDATE_IC7 = 9
    # 16R4
    READ_IC12 = 10
    CONVERT_IC12 = 11
    VALIDATE_IC12 = 12
    # 16R4 + HI-Z
    READ_IC49 = 13
    CONVERT_IC49 = 14
    VALIDATE_IC49 = 15

port = "COM3"
delay = 0.001
mode = Mode.VALIDATE_IC49
path = "C:\\Work\\PalAnalyzer\\reads"

if __name__ == "__main__":
    if mode == Mode.READ_IC24:
        dupal_board = DuPalBoard(PalType.PAL10L8, port, delay)
        analyzer = PalLAnalyzer(dupal_board)
        analyzer.analyze(
            f"{path}\\ic24\\ic24.txt",
            f"{path}\\ic24\\ic24_stdout.txt",
        )

    if mode == Mode.CONVERT_IC24:
        PalLAnalyzer.convert_file(
            f"{path}\\ic24\\ic24.txt",
            f"{path}\\ic24\\ic24.tbl",
            pal_type=PalType.PAL10L8
        )

    if mode == Mode.VALIDATE_IC24:
        ic24 = IC24()
        analyzer = PalLAnalyzer(ic24)
        analyzer.analyze(
            f"{path}\\ic24\\ic24_simulated.txt",
            f"{path}\\ic24\\ic24_simulated_stdout.txt"
        )

    if mode == Mode.READ_IC22:
        dupal_board = DuPalBoard(PalType.PAL16L8, port, delay)
        analyzer = PalLAnalyzer(dupal_board)
        analyzer.analyze(
            f"{path}\\ic22\\ic22.txt",
            f"{path}\\ic22\\ic22_stdout.txt",
        )

    if mode == Mode.CONVERT_IC22:
        PalLAnalyzer.convert_file(
            f"{path}\\ic22\\ic22.txt",
            f"{path}\\ic22\\ic22.tbl",
            pal_type=PalType.PAL16L8
        )

    if mode == Mode.VALIDATE_IC22:
        ic22 = IC22()
        analyzer = PalLAnalyzer(ic22)
        analyzer.analyze(
            f"{path}\\ic22\\ic22_simulated.txt",
            f"{path}\\ic22\\ic22_simulated_stdout.txt"
        )

    if mode == Mode.READ_IC7:
        dupal_board = DuPalBoard(PalType.PAL16L8, port, delay)
        analyzer = PalLAnalyzer(dupal_board)
        analyzer.analyze(
            f"{path}\\ic7\\ic7.txt",
            f"{path}\\ic7\\ic7_stdout.txt",
        )

    if mode == Mode.CONVERT_IC7:
        PalLAnalyzer.convert_file(
            f"{path}\\ic7\\ic7.txt",
            f"{path}\\ic7\\ic7.tbl",
            pal_type=PalType.PAL16L8
        )

    if mode == Mode.VALIDATE_IC7:
        ic7 = IC7()
        analyzer = PalLAnalyzer(ic7)
        analyzer.analyze(
            f"{path}\\ic7\\ic7_simulated.txt",
            f"{path}\\ic7\\ic7_simulated_stdout.txt"
        )

    if mode == Mode.READ_IC12:
        dupal_board = DuPalBoard(PalType.PAL16R4, port, delay)
        analyzer = PalRAnalyzer(dupal_board)
        analyzer.analyze(f"{path}\\ic12\\ic12.json")

    if mode == Mode.CONVERT_IC12:
        PalRAnalyzer.convert_file(
            f"{path}\\ic12\\ic12.json",
            f"{path}\\ic12\\ic12.tbl",
            inputs_mask="000FFFF00IIIIIIII0",
            outputs_mask="OOOQQQQO0000000000"
        )

    if mode == Mode.VALIDATE_IC12:
        ic12 = IC12()
        ic12.read_outputs(0, clock=True)
        analyzer = PalRAnalyzer(ic12)
        analyzer.analyze(f"{path}\\ic12\\ic12_simulated.json")

    if mode == Mode.READ_IC49:
        dupal_board = DuPalBoard(PalType.PAL16R4, port, delay)
        analyzer = PalRAnalyzer(dupal_board)
        analyzer.analyze(f"{path}\\ic49\\ic49.json")

    if mode == Mode.CONVERT_IC49:
        PalRAnalyzer.convert_file(
            f"{path}\\ic49\\ic49.json",
            f"{path}\\ic49\\ic49.tbl",
            inputs_mask="F0FFFFF00IIIIIIII0" # pins 12 and 13 are inputs
        )

    if mode == Mode.VALIDATE_IC49:
        ic49 = IC49()
        ic49.read_outputs(0, clock=True)
        analyzer = PalRAnalyzer(ic49)
        analyzer.analyze(f"{path}\\ic49\\ic49_simulated.json")
