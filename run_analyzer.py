from analyzer import PalAnalyzer
from pal import Pal16R4DuPAL

analyzer = PalAnalyzer()

pal = Pal16R4DuPAL("COM4")

analyzer.analyze(pal)

analyzer.save_to_file("./reads/ic49/ic49_full_read_2.json")
