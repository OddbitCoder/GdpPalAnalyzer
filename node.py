from dataclasses import dataclass


@dataclass
class Node:
    outputs: int

    # each outlink is a tuple of (inputs, outputs)
    # next_inputs_idx are next inputs to be evaluated
    outlinks: list[(int, int)] = None
    next_inputs_idx = 0

    clock_outlinks: list[(int, int)] = None
    next_clock_inputs_idx = 0
