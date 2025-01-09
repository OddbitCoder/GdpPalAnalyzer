from analyzer import PalRAnalyzer
from pal import DuPalBoard


if __name__ == "__main__":
    # dupal_board = DuPalBoard(PalType.PAL16L8, port="COM4", delay=0.001)
    # analyzer = PalRAnalyzer(dupal_board)
    # analyzer.analyze("C:\\Work\\PalAnalyzer\\reads\\ic49\\ic49_2.json")
    PalRAnalyzer.convert_file(
        "C:\\Work\\PalAnalyzer\\reads\\ic49\\ic49.json",
        "C:\\Work\\PalAnalyzer\\reads\\ic49\\ic49.tbl",
    )
    # run_analyzer(
    #     dupal_board,
    #     f"C:\\Work\\PalAnalyzer\\reads\\ic7_full\\ic7_full_8.txt",
    #     f"C:\\Work\\PalAnalyzer\\reads\\ic7_full\\ic7_full_stdout_8.txt",
    # )
    # convert_file(
    #     "C:\\Work\\PalAnalyzer\\reads\\ic7\\ic7.txt",
    #     "C:\\Work\\PalAnalyzer\\reads\\ic7\\ic7.tbl",
    #     PalType.PAL16L8,
    # )
    # convert_file(
    #     "C:\\Work\\PalAnalyzer\\reads\\ic7_full\\ic7_full.txt",
    #     "C:\\Work\\PalAnalyzer\\reads\\ic7_full\\ic7_full.tbl",
    #     PalType.PAL16L8,
    # )
    # convert_file(
    #     "C:\\Work\\PalAnalyzer\\reads\\ic22\\ic22.txt",
    #     "C:\\Work\\PalAnalyzer\\reads\\ic22\\ic22.tbl",
    #     PalType.PAL16L8,
    # )
    # convert_file(
    #     "C:\\Work\\PalAnalyzer\\reads\\ic24\\ic24.txt",
    #     "C:\\Work\\PalAnalyzer\\reads\\ic24\\ic24.tbl",
    #     PalType.PAL10L8,
    # )
