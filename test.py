from analyzer_ext import PalRAnalyzerExt

path = "C:\\Work\\PalAnalyzer\\reads"

PalRAnalyzerExt.check_states(
    f"{path}\\ic49\\ic49_ext.json", f"{path}\\ic49\\ic49_ext_reduced.json"
)
