from analyzer import PalAnalyzer

analyzer = PalAnalyzer()

analyzer.read_from_file("./reads/ic49/ic49_full_read.json")

analyzer.export_table("./reads/ic49/ic49_tables.txt")
