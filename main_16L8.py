import sys
from queue import Queue
from dupal import DuPalBoard
from pal import Pal16L8

def bstr(number: int, hi_z_mask: int = 0):
    binary_str = f"{number:018b}"
    mask_str = f"{hi_z_mask:018b}"
    result_str = "".join("Z" if mask_str[i] == "1" else binary_str[i] for i in range(18))
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

def analyze(dupal_board: DuPalBoard, inputs: int, inputs_queue: Queue, inputs_set: set,
            out_mask: int = 0b11_000000_0000000000,
            io_mask: int  = 0b00_111111_0000000000) -> (int, int):
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
                new_inputs = new_inputs | (1 << i) if not bit_from_inputs else new_inputs & bc(1 << i)
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

def run_analyzer():
    ic_name = "ic24"
    # 10L8
    out_mask = 0b11_111111_0000000000
    io_mask  = 0b00_000000_0000000000
    # 16L8
    #out_mask = 0b11_000000_0000000000
    #io_mask  = 0b00_111111_0000000000
    with open(f"C:\\Work\\PalAnalyzer\\new_reads\\{ic_name}\\{ic_name}.txt", "w") as output_file:
        with open(f"C:\\Work\\PalAnalyzer\\new_reads\\{ic_name}\\{ic_name}_stdout.txt", "w") as stdout_file:
            # redirect stdout to the file
            sys.stdout = stdout_file
            dupal_board = DuPalBoard(Pal16L8(), port="COM4", delay=0.01)
            inputs_set = set()
            inputs_queue = Queue()
            for i in range(2 ** 10):
                inputs_queue.put(i)
                inputs_set.add(i)
            while not inputs_queue.empty():
                inputs = inputs_queue.get()
                outputs, hi_z_mask = analyze(dupal_board, inputs, inputs_queue, inputs_set, out_mask, io_mask)
                output_file.write(f"{bstr(inputs)} -> {bstr(outputs, hi_z_mask)}\n")
            # restore stdout
            sys.stdout = sys.__stdout__

def load_file(filename):
    result = {}
    with open(filename, 'r') as file:
        for line in file:
            key_part, value_part = line.strip().split(" -> ")
            key = int(key_part.replace("_", ""), 2)
            binary_value = value_part.replace("Z", "0")  # Replace 'Z' with '0'
            mask = "".join("1" if char == "Z" else "0" for char in value_part)  # Create mask where 'Z' is
            value = (
                int(binary_value.replace("_", ""), 2),  # First part as integer
                int(mask.replace("_", ""), 2)  # Mask as integer
            )
            result[key] = value
    return result

if __name__ == "__main__":
    # run_analyzer()
    file_dict = load_file("C:\\Work\\PalAnalyzer\\new_reads\\ic24\\ic24.txt")
    all_inputs = binary_combinations(0b00_000000_1111111111)
    for inputs in all_inputs:
        print(bstr(inputs))
        assert inputs in file_dict
    print(file_dict)

