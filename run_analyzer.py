from analyzer import PalAnalyzer
from pal import Pal16R4DuPAL

analyzer = PalAnalyzer(Pal16R4DuPAL("COM4", output_mask=0b1100))

analyzer.analyze()

analyzer.save_to_file("./reads/ic49/ic49_full_read_3.json")
