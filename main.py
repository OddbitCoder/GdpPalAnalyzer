from analyzer import PalRAnalyzer, PalLAnalyzer
from pal import DuPalBoard, IC49, IC24, IC22, IC7, IC12, PalType

if __name__ == "__main__":
    # ic49 = IC49()
    # ic49.read_outputs(0, clock=True)
    # analyzer = PalRAnalyzer(ic49)
    # analyzer.analyze("C:\\Work\\PalAnalyzer\\reads\\ic49\\ic49_simulated.json")

    # analyzer = PalRAnalyzer(IC49())
    # analyzer._pal.read_outputs(0, True)
    # analyzer.analyze("C:\\Work\\PalAnalyzer\\reads\\ic49\\ic49_simulated.txt")

    dupal_board = DuPalBoard(PalType.PAL10L8, port="COM3", delay=0.001)
    analyzer = PalLAnalyzer(dupal_board)
    # # analyzer.analyze("C:\\Work\\PalAnalyzer\\reads\\ic49\\ic49_2.json")
    # PalRAnalyzer.convert_file(
    #     "C:\\Work\\PalAnalyzer\\reads\\ic12\\ic12.json",
    #     "C:\\Work\\PalAnalyzer\\reads\\ic12\\ic12.tbl",
    #     outputs_mask="OOOQQQQO0000000000",
    #     inputs_mask="000FFFF00IIIIIIII0",
    # )
    analyzer.analyze(
        f"C:\\Work\\PalAnalyzer\\reads\\ic24\\ic24_2.txt",
        f"C:\\Work\\PalAnalyzer\\reads\\ic24\\ic24_2_stdout.txt",
    )
    # PalLAnalyzer.convert_file(
    #     "C:\\Work\\PalAnalyzer\\reads\\ic7\\ic7.txt",
    #     "C:\\Work\\PalAnalyzer\\reads\\ic7\\ic7_hiz.tbl",
    #     PalType.PAL16L8,
    #     inputs_mask="FFFFFFFFIIIIIIIIII",
    #     outputs_mask="TTTTTTTT0000000000"
    # )
    # PalLAnalyzer.convert_file(
    #     "C:\\Work\\PalAnalyzer\\reads\\ic22\\ic22.txt",
    #     "C:\\Work\\PalAnalyzer\\reads\\ic22\\ic22_2.tbl",
    #     PalType.PAL16L8,
    # )
    # PalLAnalyzer.convert_file(
    #     "C:\\Work\\PalAnalyzer\\reads\\ic24\\ic24.txt",
    #     "C:\\Work\\PalAnalyzer\\reads\\ic24\\ic24_2.tbl",
    #     PalType.PAL10L8,
    # )
