from dataclasses import dataclass
from typing import Optional
from collections import deque

from pal import Pal16R4Base


possible_inputs: list[int] = []


@dataclass
class Node:
    inputs: int
    outputs: int

    internal_outputs: Optional[int] = None

    # each outlink is a tuple of (outlink_index, node_key)
    # outlink_index are in fact inputs of the next node
    outlinks: list[(int, int)] = None
    next_inputs_idx = 0

    clock_link: Optional[int] = None

    @property
    def node_key(self) -> int:
        return (self.inputs << 8) + self.outputs

    @property
    def is_incomplete(self) -> bool:
        return len(self.outlinks) < len(possible_inputs) or self.internal_outputs is None


CLOCK_PULSE = -1


nodes: dict[int, Node] = {}


def set_possible_inputs(set_zero_mask: int, set_one_mask: int):
    global possible_inputs
    possible_inputs = []
    for num in range(256):
        if (num & set_zero_mask == 0) and (num | set_one_mask == num):
            possible_inputs.append(num)


def create_node_key(inputs: int, outputs: int) -> int:
    return (inputs << 8) + outputs


def get_or_create_node(inputs: int, outputs: int) -> Node:
    node_key = create_node_key(inputs, outputs)
    if node_key not in nodes:
        nodes[node_key] = Node(inputs, outputs, outlinks=[])
    return nodes[node_key]


path_cache: dict[int, tuple[Node, list[int]]] = {}


def find_incomplete_node(start_node: Node) -> tuple[Optional[Node], list[int]]:
    # check cache
    if start_node.node_key in path_cache:
        (node, path) = path_cache[start_node.node_key]
        if node.is_incomplete:
            return node, path

    queue = deque([(start_node, [])])
    visited = set()

    while queue:
        node, path = queue.popleft()

        if node.is_incomplete:
            return node, path

        visited.add(node.node_key)

        for link, child_key in node.outlinks + (
            [(CLOCK_PULSE, node.clock_link)]
            if node.clock_link is not None
            else []
        ):
            child_node = nodes.get(child_key)
            if child_node and child_node.node_key not in visited:
                queue.append((child_node, path + [link]))

    return None, []


def walk_to(pal: Pal16R4Base, path: list[int]):
    for inputs in path:
        if inputs == CLOCK_PULSE:
            pal.clock()
        else:
            pal.set_inputs(inputs)


def analyze(pal: Pal16R4Base) -> bool:
    set_possible_inputs(0b00000000, 0b00100000)
    node = get_or_create_node(pal.inputs_as_byte, pal.outputs_as_byte)
    while True:
        # can we create outlink?
        if len(node.outlinks) < len(possible_inputs):
            inputs = possible_inputs[node.next_inputs_idx]
            pal.set_inputs(inputs)
            pal.read_outputs()
            outputs = pal.outputs_as_byte
            node_key = create_node_key(inputs, outputs)
            node.outlinks.append((inputs, node_key))
            node.next_inputs_idx += 1
            nodes[node_key] = get_or_create_node(inputs, outputs)
            node = nodes[node_key]
        elif node.internal_outputs is None:  # should we trigger clock?
            pal.clock()
            inputs = node.inputs
            pal.read_outputs()
            outputs = pal.outputs_as_byte
            node.internal_outputs = outputs & 0b00011110
            node_key = create_node_key(inputs, outputs)
            node.clock_link = node_key
            nodes[node_key] = get_or_create_node(inputs, outputs)
            node = nodes[node_key]
        else:
            # can we walk to node that is not yet completely mapped out?
            node, path = find_incomplete_node(node)
            if node:
                walk_to(pal, path)
                path_cache[node.node_key] = (node, path)
            else:  # can't find any incomplete node
                # do we have everything we need?
                if all(not node.is_incomplete for node in nodes.values()):
                    print("We have everything we need.")
                    return True
                else:
                    print(
                        "We don't have everything we need, but we can't do anything more without power-cycling."
                    )
                    total_outlinks = 0
                    for node in nodes.values():
                        total_outlinks += len(node.outlinks)
                        if node.internal_outputs is not None:
                            total_outlinks += 1
                    print(f"Total outlinks: {total_outlinks}")
                return False
