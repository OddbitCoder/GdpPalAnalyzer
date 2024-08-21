from analyzer import PalAnalyzer
from pal import Pal16R4DuPAL

analyzer = PalAnalyzer()

pal = Pal16R4DuPAL("COM4")

analyzer.analyze(pal, output_mask=0b1100)

analyzer.save_to_file("./reads/ic49/ic49_full_read.json")
