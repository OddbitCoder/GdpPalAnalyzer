from analyzer import PalAnalyzer
from pal import Pal16R4Base

analyzer = PalAnalyzer(Pal16R4Base(output_mask=0b1100))

analyzer.read_from_file("./reads/ic49/ic49_full_read_2.json")

analyzer.export_table("./reads/ic49/ic49_tables.txt")
