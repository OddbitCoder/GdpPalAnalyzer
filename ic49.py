from analyzer import PalRAnalyzer

path = "C:\\Work\\PalAnalyzer\\reads"

nodes = PalRAnalyzer.load_data(f"{path}\\ic49\\ic49.json")

def apply_inputs(pattern: str, inputs: str) -> str:
    if not pattern:
        return inputs
    combined = ""
    for p, i in zip(pattern, inputs):
        combined += p if p == i else "*"
    return combined

def test_pattern(pattern: str, inputs: str) -> bool:
    for p, i in zip(pattern, inputs):
        if p != "*" and p != i:
            return False
    return True

pattern = None

for state, node in nodes.items():
    for inputs, outputs in node.mappings.items():
        out = outputs.replace("_", "")
        inp = f"{inputs:018b}{out[3:-1]}{out[1:-6]}"
        if not out.endswith("Z"):
            print(f"{inp} -> {out}")
            pattern = apply_inputs(pattern, inp)
            print(pattern)

for state, node in nodes.items():
    for inputs, outputs in node.mappings.items():
        out = outputs.replace("_", "")
        inp = f"{inputs:018b}{out[3:-1]}{out[1:-6]}"
        if out.endswith("Z"):
            if test_pattern(pattern, inp):
                print(f"{inp} -> {out}")