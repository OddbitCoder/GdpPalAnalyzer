import json
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
    outputs = pal.read_outputs()
    node = get_or_create_node(outputs)
    while True:
        # can we create outlink?
        if len(node.outlinks) < len(possible_inputs):
            inputs = possible_inputs[node.next_inputs_idx]
            pal.set_inputs(inputs)
            outputs = pal.read_outputs()
            node.outlinks.append((inputs, outputs))
            node.next_inputs_idx += 1
            nodes[outputs] = get_or_create_node(outputs)
            node = nodes[outputs]
        elif len(node.clock_outlinks) < len(possible_inputs):  # should we trigger clock?
            inputs = possible_inputs[node.next_clock_inputs_idx]
            pal.set_inputs(inputs)
            pal.clock()
            outputs = pal.read_outputs()
            node.clock_outlinks.append((inputs, outputs))
            node.next_clock_inputs_idx += 1
            nodes[outputs] = get_or_create_node(outputs)
            node = nodes[outputs]
        else:
            # can we walk to node that is not yet completely mapped out?
            start_node = node
            node, path = find_incomplete_node(start_node)
            assert not node or node.is_incomplete, "We found a complete node"
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


def save_to_file(file_name: str):
    data_json = json.dumps(nodes, default=lambda o: o.__dict__)
    # save to file
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(data_json)


def reset():
    global nodes, path_cache
    nodes = {}
    path_cache = {}


def _create_node(params: dict) -> Node:
    node = Node(params["outputs"])
    node.outlinks = [(inputs, outputs) for [inputs, outputs] in params["outlinks"]]
    node.clock_outlinks = [(inputs, outputs) for [inputs, outputs] in params["clock_outlinks"]]
    node.next_inputs_idx = params["next_inputs_idx"] if "next_inputs_idx" in params else 0
    node.next_clock_inputs_idx = params["next_clock_inputs_idx"] if "next_clock_inputs_idx" in params else 0
    return node


def read_from_file(file_name: str):
    global nodes
    with open(file_name, "r", encoding="utf-8") as file:
        data_json = file.read()
        _nodes = json.loads(data_json)
        nodes = {int(k): _create_node(v) for k, v in _nodes.items()}
        print(f"Loaded {len(nodes)} nodes from file")


def build_inverted_graph(nodes: dict[int, Node]) -> dict[int, Node]:
    inverted_nodes: dict[int, Node] = {}

    for node_id, node in nodes.items():
        if node_id not in inverted_nodes:
            inverted_nodes[node_id] = Node(outputs=node.outputs, outlinks=[], clock_outlinks=[])

    for node_id, node in nodes.items():
        for input_id, output_id in node.outlinks or []:
            inverted_nodes[output_id].outlinks.append((input_id, node_id))  # Reverse direction

        for input_id, output_id in node.clock_outlinks or []:
            inverted_nodes[output_id].clock_outlinks.append((input_id, node_id))  # Reverse direction

    return inverted_nodes


def create_table_entry(file, feedbacks: int, inputs: int, outputs: int):
    file.write(f"{inputs:08b}{feedbacks:08b} {outputs:08b}\n")



# def build_tables(file_name: str):
#     inverted_graph = build_inverted_graph(nodes)
#     for node in nodes.values():
#         for inputs_from_parent, parent_node_id in inverted_graph[node.outputs].outlinks:
#             parent_node = nodes[parent_node_id]
#             for inputs_to_child, child_node_id in node.outlinks:
#                 child_node = nodes[child_node_id]
#                 # we have a triple here: parent_node --inputs_from_parent--> node --inputs_to_child--> child_node
#                 # print(f"Processing triple {parent_node.outputs} --{inputs_from_parent}--> {node.outputs} --{inputs_to_child}--> {child_node.outputs}")
#                 # START STATE:
#                 # inputs: node.outputs, inputs_to_child
#                 # outputs: child_node.outputs (input into registers from parent_node.clock_outlinks)
#                 reg_inputs_list = [o for i, o in parent_node.clock_outlinks if inputs_from_parent == i]
#                 if not reg_inputs_list:
#                     print(f"WARNING: Cannot find clocked link from the parent node!")
#                 else:
#                     reg_inputs = reg_inputs_list[0] & 0b00011110
#                     create_table_entry(node.outputs, inputs_to_child, (child_node.outputs & 0b11100001) + reg_inputs)
#                 # END STATE:
#                 # inputs: child_node.outputs, inputs_to_child
#                 # outputs: child_node.outputs (input into registers from node.clock_outlinks)
#                 reg_inputs_list = [o for i, o in node.clock_outlinks if inputs_to_child == i]
#                 if not reg_inputs_list:
#                     print(f"WARNING: Cannot find clocked link to the child node!")
#                 else:
#                     reg_inputs = reg_inputs_list[0] & 0b00011110
#                     create_table_entry(child_node.outputs, inputs_to_child, (child_node.outputs & 0b11100001) + reg_inputs)


# (self.io18 << 0)
# | (self.o17 << 1)
# | (self.o16 << 2)
# | (self.o15 << 3)
# | (self.o14 << 4)
# | (self.io13 << 5)
# | (self.io19 << 6)
# | (self.io12 << 7)

# (self.i2 << 0)
# | (self.i3 << 1)
# | (self.i4 << 2)
# | (self.i5 << 3)
# | (self.i6 << 4)
# | (self.i7 << 5)
# | (self.i8 << 6)
# | (self.i9 << 7)

def build_tables(file_name: str):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("# PAL1R4\n")
        file.write(".i 16\n")
        file.write(".o 8\n")
        file.write(".ilb fio12 fio19 fio13 r14 r15 r16 r17 fio18 i9 i8 i7 i6 i5 i4 i3 i2\n")
        file.write(".ob io12 io19 io13 ir14 ir15 ir16 ir17 io18\n")
        file.write(".phase 00000000\n")
        for node in nodes.values():
            for inputs, child_node_id in node.outlinks:
                child_node = nodes[child_node_id]
                # here we have: node --inputs--> child_node
                if node.outputs == 236 and inputs == 232 and child_node.outputs == 77:
                    print("DEBUG")
                reg_inputs_list = [o for i, o in node.clock_outlinks if inputs == i]
                if not reg_inputs_list:
                    print(f"WARNING: Cannot find the clock outlink!")
                else:
                    clock_node = nodes[reg_inputs_list[0]]
                    reg_inputs = clock_node.outputs & 0b00011110
                    # START STATE:
                    # inputs: node.outputs feedbacks, inputs
                    # outputs: child_node.outputs (input into registers from node.clock_outlinks)
                    create_table_entry(file, node.outputs, inputs, (child_node.outputs & 0b11100001) + reg_inputs)
                    # END STATE:
                    # inputs: child_node.outputs feedbacks, inputs
                    # outputs: child_node.outputs (input into registers from node.clock_outlinks)
                    create_table_entry(file, child_node.outputs, inputs, (child_node.outputs & 0b11100001) + reg_inputs)
