from analyzer import PalAnalyzer
from pal import Pal16R4DuPAL

analyzer = PalAnalyzer()

pal = Pal16R4DuPAL("COM5")

analyzer.analyze(pal)

analyzer.save_to_file("./reads/ic12/ic12_full_read.json")
