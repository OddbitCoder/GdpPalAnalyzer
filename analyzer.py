import json
from dataclasses import dataclass
from typing import Optional, Callable
from collections import deque

from pal import Pal16R4Base


@dataclass
class Node:
    outputs: int

    # each outlink is a tuple of (inputs, outputs)
    # outlink_index are in fact inputs of the next node
    outlinks: list[(int, int)] = None
    next_inputs_idx = 0

    clock_outlinks: list[(int, int)] = None
    next_clock_inputs_idx = 0


class PalAnalyzer:
    def __init__(self):
        self._possible_inputs: list[int] = []
        self._nodes: dict[int, Node] = {}
        self._path_cache: dict[int, tuple[Node, list[int]]] = {}

    def _is_incomplete(self, node: Node) -> bool:
        num_inputs = len(self._possible_inputs)
        return len(node.outlinks) < num_inputs or len(node.clock_outlinks) < num_inputs

    def _set_possible_inputs(self, set_zero_mask: int, set_one_mask: int):
        self._possible_inputs = []
        for num in range(256):
            if (num & set_zero_mask == 0) and (num | set_one_mask == num):
                self._possible_inputs.append(num)

    def _get_or_create_node(self, outputs: int) -> Node:
        if outputs not in self._nodes:
            self._nodes[outputs] = Node(outputs, outlinks=[], clock_outlinks=[])
        return self._nodes[outputs]

    def _find_incomplete_node(
        self, start_node: Node
    ) -> tuple[Optional[Node], list[int]]:
        return self._find_path(start_node, self._is_incomplete)

    def find_path_between_nodes(
        self, start_node: Node, end_node: Node
    ) -> tuple[Optional[Node], list[int]]:
        return self._find_path(
            start_node, lambda node: node.outputs == end_node.outputs
        )

    def _find_path(
        self, start_node: Node, node_condition: Callable[[Node], bool]
    ) -> tuple[Optional[Node], list[int]]:
        # check cache
        if start_node.outputs in self._path_cache:
            (node, path) = self._path_cache[start_node.outputs]
            if node_condition(node):
                return node, path

        queue = deque([(start_node, [])])
        visited = set()

        while queue:
            node, path = queue.popleft()

            if node_condition(node):
                return node, path

            visited.add(node.outputs)

            for inputs, outputs in node.outlinks + [
                (-(inputs + 1), outputs) for inputs, outputs in node.clock_outlinks
            ]:
                child_node = self._nodes.get(outputs)
                if child_node and child_node.outputs not in visited:
                    queue.append((child_node, path + [inputs]))

        return None, []

    @staticmethod
    def _walk_to(pal: Pal16R4Base, path: list[int]):
        for inputs in path:
            if inputs < 0:
                pal.set_inputs(-inputs - 1)
                pal.clock()
            else:
                pal.set_inputs(inputs)

    def analyze(
        self, pal: Pal16R4Base, set_zero_mask: int = 0, set_one_mask: int = 0
    ) -> bool:
        self._set_possible_inputs(set_zero_mask, set_one_mask)
        outputs = pal.read_outputs()
        node = self._get_or_create_node(outputs)
        while True:
            # can we create outlink?
            if len(node.outlinks) < len(self._possible_inputs):
                inputs = self._possible_inputs[node.next_inputs_idx]
                pal.set_inputs(inputs)
                outputs = pal.read_outputs()
                node.outlinks.append((inputs, outputs))
                node.next_inputs_idx += 1
                self._nodes[outputs] = self._get_or_create_node(outputs)
                node = self._nodes[outputs]
            elif len(node.clock_outlinks) < len(
                self._possible_inputs
            ):  # should we trigger clock?
                inputs = self._possible_inputs[node.next_clock_inputs_idx]
                pal.set_inputs(inputs)
                pal.clock()
                outputs = pal.read_outputs()
                node.clock_outlinks.append((inputs, outputs))
                node.next_clock_inputs_idx += 1
                self._nodes[outputs] = self._get_or_create_node(outputs)
                node = self._nodes[outputs]
            else:
                # can we walk to node that is not yet completely mapped out?
                start_node = node
                node, path = self._find_incomplete_node(start_node)
                assert not node or self._is_incomplete(node), "We found a complete node"
                if node:
                    self._walk_to(pal, path)
                    self._path_cache[start_node.outputs] = (node, path)
                    assert self._is_incomplete(node), "We walked into a complete node"
                else:  # can't find any incomplete node
                    # do we have everything we need?
                    done = False
                    if all(
                        not self._is_incomplete(node) for node in self._nodes.values()
                    ):
                        print("We have everything we need.")
                        done = True
                    else:
                        print(
                            "We don't have everything we need, but we can't do anything more without power-cycling."
                        )
                    total_outlinks = 0
                    for node in self._nodes.values():
                        total_outlinks += len(node.outlinks) + len(node.clock_outlinks)
                    print(f"Total outlinks: {total_outlinks}")
                    return done

    def save_to_file(self, file_name: str):
        data_json = json.dumps(self._nodes, default=lambda o: o.__dict__)
        # save to file
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(data_json)

    @staticmethod
    def _create_node(params: dict) -> Node:
        node = Node(params["outputs"])
        node.outlinks = [(inputs, outputs) for [inputs, outputs] in params["outlinks"]]
        node.clock_outlinks = [
            (inputs, outputs) for [inputs, outputs] in params["clock_outlinks"]
        ]
        node.next_inputs_idx = (
            params["next_inputs_idx"] if "next_inputs_idx" in params else 0
        )
        node.next_clock_inputs_idx = (
            params["next_clock_inputs_idx"] if "next_clock_inputs_idx" in params else 0
        )
        return node

    def read_from_file(self, file_name: str):
        with open(file_name, "r", encoding="utf-8") as file:
            data_json = file.read()
            _nodes = json.loads(data_json)
            self._nodes = {int(k): self._create_node(v) for k, v in _nodes.items()}
            print(f"Loaded {len(_nodes)} nodes from file")

    @staticmethod
    def _create_table_entry(file, feedbacks: int, inputs: int, outputs: int):
        file.write(f"{feedbacks:08b}{inputs:08b} {outputs:08b}\n")

    def _get_child_node(self, node: Node, inputs: int, clock: bool = False):
        if clock:
            node_id = [o for i, o in node.clock_outlinks if inputs == i][0]
        else:
            node_id = [o for i, o in node.outlinks if inputs == i][0]
        return self._nodes[node_id]

    def export_table(self, file_name: str):
        tabu = {}
        with open(file_name, "w", encoding="utf-8") as file:
            file.write("# PAL1R4\n")
            file.write(".i 16\n")
            file.write(".o 8\n")
            file.write(
                ".ilb fio12 fio19 fio13 r14 r15 r16 r17 fio18 i9 i8 i7 i6 i5 i4 i3 i2\n"
            )
            file.write(".ob io12 io19 io13 ir14 ir15 ir16 ir17 io18\n")
            file.write(".phase 00000000\n")
            for node in self._nodes.values():
                for inputs, child_node_id in node.outlinks:
                    child_node = self._nodes[child_node_id]
                    # here we have: node --inputs--> child_node
                    clock_node = self._get_child_node(node, inputs, True)
                    # assertion 1: child_node --inputs--> child_node
                    should_be_child_node = self._get_child_node(child_node, inputs)
                    if should_be_child_node.outputs != child_node_id:
                        print("WARNING: Child node is not connected to itself!")
                        print(f"Node: {node.outputs}")
                        print(f"Child node: {child_node_id}")
                        print(f"Inputs: {inputs}")
                        print(f"Child node connects to: {should_be_child_node.outputs}")
                    # assertion 2: child_node --inputs+clock--> clock_node
                    should_be_clock_node = self._get_child_node(
                        child_node, inputs, True
                    )
                    if should_be_clock_node.outputs != clock_node.outputs:
                        print("WARNING: Child node is not connected to clock node!")
                        print(f"Node: {node.outputs}")
                        print(f"Child node: {child_node_id}")
                        print(f"Clock node: {clock_node.outputs}")
                        print(f"Inputs: {inputs}")
                        print(f"Child node connects to: {should_be_clock_node.outputs}")
                    reg_inputs = clock_node.outputs & 0b00011110
                    # CLOCK TRANSITION:
                    if node == child_node:
                        key = f"{((node.outputs & 0b11100001) + reg_inputs):08b}{inputs:08b}"
                        clock_node_child = self._get_child_node(
                            clock_node, inputs, True
                        )
                        outputs = (clock_node.outputs & 0b11100001) + (
                            clock_node_child.outputs & 0b00011110
                        )
                        if key in tabu:
                            if tabu[key] != outputs:
                                print(
                                    f"WARNING: Entry already exists but with different outputs: {key} -> {tabu[key]:08b} instead of {outputs:08b} [1]"
                                )
                        else:
                            self._create_table_entry(
                                file,
                                (node.outputs & 0b11100001) + reg_inputs,
                                inputs,
                                outputs,
                            )
                            tabu[key] = outputs
                    # NO-CLOCK TRANSITION START STATE:
                    # inputs: node.outputs feedbacks, inputs
                    # outputs: child_node.outputs (input into registers from node.clock_outlinks)
                    key = f"{node.outputs:08b}{inputs:08b}"
                    outputs = (child_node.outputs & 0b11100001) + reg_inputs
                    if key in tabu:
                        if tabu[key] != outputs:
                            print(
                                f"WARNING: Entry already exists but with different outputs: {key} -> {tabu[key]:08b} instead of {outputs:08b} [2]"
                            )
                    else:
                        self._create_table_entry(
                            file,
                            node.outputs,
                            inputs,
                            outputs,
                        )
                        tabu[key] = outputs
                    # NO-CLOCK TRANSITION END STATE:
                    # inputs: child_node.outputs feedbacks, inputs
                    # outputs: child_node.outputs (input into registers from node.clock_outlinks)
                    key = f"{child_node.outputs:08b}{inputs:08b}"
                    outputs = (child_node.outputs & 0b11100001) + reg_inputs
                    if key in tabu:
                        if tabu[key] != outputs:
                            print(
                                f"WARNING: Entry already exists but with different outputs: {key} -> {tabu[key]:08b} instead of {outputs:08b} [3]"
                            )
                    else:
                        self._create_table_entry(
                            file,
                            child_node.outputs,
                            inputs,
                            outputs,
                        )
                        tabu[key] = outputs
