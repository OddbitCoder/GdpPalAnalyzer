from analyzer import PalAnalyzer

analyzer = PalAnalyzer()

analyzer.read_from_file("./reads/ic12/ic12_full_read.json")

analyzer.export_table("./reads/ic12/ic12_tables.txt")
