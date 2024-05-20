from dataclasses import dataclass
from typing import Optional
from collections import deque

from pal import Pal16R4Base


possible_inputs: list[int] = []
nodes: dict[int, "Node"] = {}
path_cache: dict[int, tuple["Node", list[int]]] = {}


@dataclass
class Node:
    outputs: int

    # each outlink is a tuple of (inputs, outputs)
    # outlink_index are in fact inputs of the next node
    outlinks: list[(int, int)] = None
    next_inputs_idx = 0

    clock_outlinks: list[(int, int)] = None
    next_clock_inputs_idx = 0

    @property
    def is_incomplete(self) -> bool:
        num_inputs = len(possible_inputs)
        return len(self.outlinks) < num_inputs or len(self.clock_outlinks) < num_inputs


def set_possible_inputs(set_zero_mask: int, set_one_mask: int):
    global possible_inputs
    possible_inputs = []
    for num in range(256):
        if (num & set_zero_mask == 0) and (num | set_one_mask == num):
            possible_inputs.append(num)


def get_or_create_node(outputs: int) -> Node:
    if outputs not in nodes:
        nodes[outputs] = Node(outputs, outlinks=[], clock_outlinks=[])
    return nodes[outputs]


def find_incomplete_node(start_node: Node) -> tuple[Optional[Node], list[int]]:
    # check cache
    if start_node.outputs in path_cache:
        (node, path) = path_cache[start_node.outputs]
        if node.is_incomplete:
            return node, path

    queue = deque([(start_node, [])])
    visited = set()

    while queue:
        node, path = queue.popleft()

        if node.is_incomplete:
            return node, path

        visited.add(node.outputs)

        for inputs, outputs in node.outlinks + [(-inputs, outputs) for inputs, outputs in node.clock_outlinks]:
            child_node = nodes.get(outputs)
            if child_node and child_node.outputs not in visited:
                queue.append((child_node, path + [inputs]))

    return None, []


def walk_to(pal: Pal16R4Base, path: list[int]):
    for inputs in path:
        if inputs < 0:
            pal.set_inputs(-inputs)
            pal.clock()
        else:
            pal.set_inputs(inputs)


def analyze(pal: Pal16R4Base, set_zero_mask: int = 0, set_one_mask: int = 0) -> bool:
    set_possible_inputs(set_zero_mask, set_one_mask)
    node = get_or_create_node(pal.outputs_as_byte)
    while True:
        # can we create outlink?
        if len(node.outlinks) < len(possible_inputs):
            inputs = possible_inputs[node.next_inputs_idx]
            pal.set_inputs(inputs)
            outputs = pal.read_outputs()
            # outputs = pal.outputs_as_byte
            # assert outputs == _outputs, "Outputs don't match"
            node.outlinks.append((inputs, outputs))
            node.next_inputs_idx += 1
            nodes[outputs] = get_or_create_node(outputs)
            node = nodes[outputs]
        elif len(node.clock_outlinks) < len(possible_inputs):  # should we trigger clock?
            inputs = possible_inputs[node.next_clock_inputs_idx]
            pal.set_inputs(inputs)
            pal.clock()
            outputs = pal.read_outputs()
            # outputs = pal.outputs_as_byte
            # assert outputs == _outputs, "Outputs don't match"
            # we need to record registers here
            node.clock_outlinks.append((inputs, outputs))
            node.next_clock_inputs_idx += 1
            nodes[outputs] = get_or_create_node(outputs)
            node = nodes[outputs]
        else:
            # can we walk to node that is not yet completely mapped out?
            start_node = node
            node, path = find_incomplete_node(start_node)
            assert not node or node.is_incomplete, "We retrieved a complete node from cache"
            if node:
                walk_to(pal, path)
                path_cache[start_node.outputs] = (node, path)
                assert node.is_incomplete, "We walked into a complete node"
            else:  # can't find any incomplete node
                # do we have everything we need?
                done = False
                if all(not node.is_incomplete for node in nodes.values()):
                    print("We have everything we need.")
                    done = True
                else:
                    print(
                        "We don't have everything we need, but we can't do anything more without power-cycling."
                    )
                total_outlinks = 0
                for node in nodes.values():
                    total_outlinks += len(node.outlinks) + len(node.clock_outlinks)
                print(f"Total outlinks: {total_outlinks}")
                return done
