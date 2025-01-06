import sys
from queue import Queue
from pal import DuPalBoard, PalBase

from butils import bstr18, bcomb
from pal import PalType

from analyzer import PalAnalyzer


def run_analyzer(
    pal: PalBase,
    pal_type: PalType,
    output_filename: str,
    stdout_filename: str = None,
):
    # set I/O mask
    io_mask = (
        0b00_111111_0000000000
        if pal_type == PalType.PAL16L8
        else 0b00_000000_0000000000
    )
    with open(output_filename, "w") as output_file:
        # redirect stdout to the file
        if stdout_filename:
            stdout_file = open(stdout_filename, "w")
            sys.stdout = stdout_file
        inputs_set = set()
        inputs_queue = Queue()
        for i in range(2**10):
            inputs_queue.put(i)
            inputs_set.add(i)
        while not inputs_queue.empty():
            inputs = inputs_queue.get()
            outputs, hi_z_mask = pal.read_states(inputs)
            hi_z_mask <<= 10
            outputs <<= 10
            for io_inputs in bcomb(hi_z_mask & io_mask):
                new_inputs = inputs ^ io_inputs
                print(f"Candidate for new inputs: {bstr18(new_inputs)}")
                if new_inputs not in inputs_set:
                    print("Enqueuing.")
                    inputs_set.add(new_inputs)
                    inputs_queue.put(new_inputs)
            # output final mapping
            print(f"Final mapping: {bstr18(inputs)} -> {bstr18(outputs, hi_z_mask)}")
            output_file.write(f"{bstr18(inputs)} -> {bstr18(outputs, hi_z_mask)}\n")
        # restore stdout
        if stdout_filename:
            stdout_file.close()
            sys.stdout = sys.__stdout__


def convert_file(
    filename,
    out_filename,
    pal_type: PalType,
    inputs_mask=None,  # I - input, F - feedback, 0 - ignore
    outputs_mask=None,  # O - output, T - tri-state, 0 - ignore
):
    # set masks
    inputs_mask = inputs_mask or "00_000000_IIIIIIIIII"
    outputs_mask = outputs_mask or (
        "TT_TTTTTT_0000000000"
        if pal_type == PalType.PAL16L8
        else "OO_OOOOOO_0000000000"
    )
    # set output file header
    inputs_count = inputs_mask.count("F") + inputs_mask.count("I")
    outputs_count = outputs_mask.count("O") + 2 * outputs_mask.count("T")
    input_names = [
        "",
        "",
        "",
        "f13",
        "f14",
        "f15",
        "f16",
        "f17",
        "f18",
        "",
        "i11",
        "i9",
        "i8",
        "i7",
        "i6",
        "i5",
        "i4",
        "i3",
        "i2",
        "i1",
    ]
    output_names = ["o12", "o19", "", "io13", "io14", "io15", "io16", "io17", "io18"]
    output_names_tri_state = [
        "z12",
        "z19",
        "",
        "z13",
        "z14",
        "z15",
        "z16",
        "z17",
        "z18",
    ]
    inputs_header = [
        f" {input_name}" if input_char in ["I", "F"] else ""
        for input_char, input_name in zip(inputs_mask, input_names)
    ]
    outputs_header = [
        f" {output_name}" if output_char in ["O", "T"] else ""
        for output_char, output_name in zip(outputs_mask, output_names)
    ] + [
        f" {output_name}" if output_char == "T" else ""
        for output_char, output_name in zip(outputs_mask, output_names_tri_state)
    ]
    header = f""".i {inputs_count}
.o {outputs_count}
.ilb{"".join(inputs_header)}
.ob{"".join(outputs_header)}
.phase {"0" * outputs_count}
"""
    rows = {}
    with open(out_filename, "w") as out_file:
        out_file.write(header + "\n")
        with open(filename, "r") as file:
            for line in file:
                inputs, outputs = line.strip().split(" -> ")
                result = []  # Collect output characters here
                for _, (input_char, output_char, input_mask) in enumerate(
                    zip(inputs, outputs, inputs_mask)
                ):
                    if input_mask == "_":
                        continue  # Skip positions where the mask is "_"
                    if input_mask == "I":
                        result.append(input_char)  # Write the character from inputs
                    elif input_mask == "F":
                        if output_char == "Z":
                            result.append(input_char)  # Write character from inputs
                        else:
                            result.append(output_char)  # Write character from outputs
                row_left = "".join(result)
                result = []
                for _, (input_char, output_char, output_mask) in enumerate(
                    zip(inputs, outputs, outputs_mask)
                ):
                    if output_mask == "_":
                        continue
                    if output_mask == "O" or output_mask == "T":
                        result.append("-" if output_char == "Z" else output_char)
                # result.append(" tri-state: ")
                for _, (input_char, output_char, output_mask) in enumerate(
                    zip(inputs, outputs, outputs_mask)
                ):
                    if output_mask == "_":
                        continue
                    if output_mask == "T":
                        result.append("1" if output_char == "Z" else "0")
                row_right = "".join(result)
                if row_left in rows:
                    assert rows[row_left] == row_right  # Must be the same
                else:
                    rows.update({row_left: row_right})
                    out_file.write(f"{row_left} {row_right}\n")
            # Add missing combinations
            for i in range(2**inputs_count):
                inputs = format(i, f"0{inputs_count}b")
                if inputs not in rows:
                    out_file.write(inputs + " " + ("-" * outputs_count) + "\n")


if __name__ == "__main__":
    dupal_board = DuPalBoard(port="COM4", delay=0.001)
    # analyzer = PalAnalyzer(dupal_board)
    # analyzer.analyze("C:\\Work\\PalAnalyzer\\new_reads\\ic12\\ic12_3.json")
    run_analyzer(
        dupal_board,
        PalType.PAL16L8,
        f"C:\\Work\\PalAnalyzer\\new_reads\\ic7_full\\ic7_full_8.txt",
        f"C:\\Work\\PalAnalyzer\\new_reads\\ic7_full\\ic7_full_stdout_8.txt",
    )
    # convert_file(
    #     "C:\\Work\\PalAnalyzer\\new_reads\\ic7\\ic7.txt",
    #     "C:\\Work\\PalAnalyzer\\new_reads\\ic7\\ic7.tbl",
    #     PalType.PAL16L8,
    # )
    # convert_file(
    #     "C:\\Work\\PalAnalyzer\\new_reads\\ic7_full\\ic7_full.txt",
    #     "C:\\Work\\PalAnalyzer\\new_reads\\ic7_full\\ic7_full.tbl",
    #     PalType.PAL16L8,
    # )
    # convert_file(
    #     "C:\\Work\\PalAnalyzer\\new_reads\\ic22\\ic22.txt",
    #     "C:\\Work\\PalAnalyzer\\new_reads\\ic22\\ic22.tbl",
    #     PalType.PAL16L8,
    # )
    # convert_file(
    #     "C:\\Work\\PalAnalyzer\\new_reads\\ic24\\ic24.txt",
    #     "C:\\Work\\PalAnalyzer\\new_reads\\ic24\\ic24.tbl",
    #     PalType.PAL10L8,
    # )
