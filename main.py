import sys
from enum import Enum
from queue import Queue
from dupal import DuPalBoard, DuPalBase
from pal import Pal16L8, Pal10L8, Pal16R4

from analyzer import PalAnalyzer


class PalType(Enum):
    PAL10L8 = 1
    PAL16L8 = 2
    PAL16R4 = 3


def bstr(number: int, hi_z_mask: int = 0):
    binary_str = f"{number:018b}"
    mask_str = f"{hi_z_mask:018b}"
    result_str = "".join(
        "Z" if mask_str[i] == "1" else binary_str[i] for i in range(18)
    )
    return f"{result_str[:2]}_{result_str[2:8]}_{result_str[8:]}"


def bc(number):
    bit_length = 18
    mask = (1 << bit_length) - 1
    return number ^ mask


def binary_combinations(number):
    # Get positions of all "1" bits in the binary representation of the number
    ones_positions = [i for i in range(number.bit_length()) if number & (1 << i)]
    # Generate all subsets of these positions
    from itertools import combinations

    combinations_list = []
    for r in range(len(ones_positions) + 1):
        combinations_list.extend(combinations(ones_positions, r))
    # Generate numbers for each subset
    results = []
    for subset in combinations_list:
        new_number = number
        for pos in subset:
            new_number &= bc(1 << pos)  # Set the bit at position "pos" to 0
        results.append(new_number)
    return sorted(results)


def analyze_state(
    dupal_board: DuPalBase,
    inputs: int,
    inputs_queue: Queue,
    inputs_set: set,
    out_mask: int,
    io_mask: int,
) -> (int, int):
    # fetch outputs
    outputs = dupal_board.set_inputs(inputs) << 10
    print(f"{bstr(inputs)} -> {bstr(outputs)}")
    # check tri-state pins
    # check output pins
    hi_z_mask = 0
    if out_mask:
        new_inputs = out_mask | inputs
        new_outputs = dupal_board.set_inputs(new_inputs) << 10
        print(f"new inputs:  {bstr(new_inputs)}")
        print(f"new outputs: {bstr(new_outputs)}")
        hi_z_mask = bc(outputs) & new_outputs & out_mask
        if hi_z_mask:
            print(f"Outputs HI-Z mask: {bstr(hi_z_mask)}")
        # reset
        assert outputs == dupal_board.set_inputs(inputs) << 10
    # check I/O pins
    # only the pins that do not change can be in HI-Z
    hi_z_candidates = bc(inputs ^ outputs) & io_mask
    print(f"I/O HI-Z candidates: {bstr(hi_z_candidates)}")
    if hi_z_candidates:
        for i in range(10, 16):
            if hi_z_candidates & (1 << i):
                print(f"Bit {i} is ON")
                bit_from_inputs = (inputs >> i) & 1
                new_inputs = inputs
                new_inputs = (
                    new_inputs | (1 << i)
                    if not bit_from_inputs
                    else new_inputs & bc(1 << i)
                )
                print(f"New inputs:  {bstr(new_inputs)}")
                new_outputs = dupal_board.set_inputs(new_inputs) << 10
                print(f"New outputs: {bstr(new_outputs)}")
                hi_z = (new_outputs ^ outputs) & io_mask
                if hi_z:
                    hi_z_mask |= hi_z
                    print(f"HI-Z mask updated: {bstr(hi_z_mask)}")
                # reset
                assert outputs == dupal_board.set_inputs(inputs) << 10
    print(f"Final HI-Z mask: {bstr(hi_z_mask)}")
    # compute new inputs that should be tested
    for io_combination in binary_combinations(hi_z_mask & io_mask):
        new_inputs = inputs ^ io_combination
        print(f"Candidate for new inputs: {bstr(new_inputs)}")
        if new_inputs not in inputs_set:
            print("Enqueuing.")
            inputs_set.add(new_inputs)
            inputs_queue.put(new_inputs)
    # output final mapping
    print(f"Final mapping: {bstr(inputs)} -> {bstr(outputs, hi_z_mask)}")
    return outputs, hi_z_mask


def run_analyzer(
    dupal_board: DuPalBase,
    pal_type: PalType,
    output_filename: str,
    stdout_filename: str = None,
):
    # set masks
    out_mask = (
        0b11_000000_0000000000
        if pal_type == PalType.PAL16L8
        else 0b11_111111_0000000000
    )
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
            outputs, hi_z_mask = analyze_state(
                dupal_board, inputs, inputs_queue, inputs_set, out_mask, io_mask
            )
            output_file.write(f"{bstr(inputs)} -> {bstr(outputs, hi_z_mask)}\n")
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
    dupal_board = DuPalBoard(Pal16R4(), port="COM4", delay=0.001)
    analyzer = PalAnalyzer(dupal_board)
    analyzer.analyze("C:\\Work\\PalAnalyzer\\new_reads\\ic12\\ic12_2.json")
    # run_analyzer(
    #     dupal_board,
    #     PalType.PAL16L8,
    #     f"C:\\Work\\PalAnalyzer\\new_reads\\ic7_full\\ic7_full_7.txt",
    #     f"C:\\Work\\PalAnalyzer\\new_reads\\ic7_full\\ic7_full_stdout_7.txt",
    # )
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
