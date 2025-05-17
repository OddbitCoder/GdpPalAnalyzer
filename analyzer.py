import json
import sys
from collections import deque
from typing import Tuple, Callable, Optional

from node import Node
from pal import PalBase, PalType
from utils import AddOnceQueue, bcomb, bstr18, bstr8


class PalRAnalyzer:
    def __init__(self, pal: PalBase):
        self._pal = pal

    def _walk_to(self, path: list[int]):
        for inputs in path:
            self._pal.read_outputs(inputs, clock=True)

    @staticmethod
    def save_states_to_file(nodes: dict[int, Node], file_name: str):
        nodes_sorted = dict(sorted(nodes.items()))
        for node in nodes.values():
            node.mappings = dict(sorted(node.mappings.items()))
            node.outlinks = dict(sorted(node.outlinks.items()))
        data_json = json.dumps(
            nodes_sorted,
            default=lambda obj: None if isinstance(obj, AddOnceQueue) else obj.__dict__,
        )
        # save to file
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(data_json)

    @staticmethod
    def load_data(file_name: str) -> dict[int, Node]:
        with open(file_name, "r") as file:
            data = json.load(file)
        nodes = dict[int, Node]()
        for k, v in data.items():
            nodes[int(k)] = Node(
                mappings={int(kk): vv for kk, vv in v["mappings"].items()},
                outlinks={int(kk): vv for kk, vv in v["outlinks"].items()},
                state=v["state"],
                inputs=AddOnceQueue(),
            )
        return nodes

    def _get_or_create_node(
        self, nodes: dict[int, Node], state: int
    ) -> Tuple[Node, bool]:
        if state not in nodes:
            new_node = Node(state, outlinks={}, inputs=AddOnceQueue(), mappings={})
            inputs_queue = AddOnceQueue()
            for inputs in range(2**8):
                inputs_queue.add(inputs << 1)
            while not inputs_queue.empty:
                inputs = inputs_queue.dequeue()
                outputs, hi_z_mask = self._pal.read_states(inputs)
                io_mask = 0b_111_0000_1
                for io_inputs in bcomb(hi_z_mask & io_mask):
                    inputs_queue.add(inputs ^ (io_inputs << 10))
                # output final mapping
                print(f"New mapping: {bstr18(inputs)} -> {bstr8(outputs, hi_z_mask)}")
                new_node.mappings[inputs] = bstr8(outputs, hi_z_mask)
            for inputs in inputs_queue.set:
                new_node.inputs.add(inputs)
            nodes[state] = new_node
            return nodes[state], True
        return nodes[state], False

    @staticmethod
    def _find_path(
        path_cache: dict[int, Tuple[Node, list[int]]],
        nodes: dict[int, Node],
        start_node: Node,
        node_condition: Callable[[Node], bool],
    ) -> Tuple[Optional[Node], list[int]]:
        # check cache
        if start_node.state in path_cache:
            (node, path) = path_cache[start_node.state]
            if node_condition(node):
                return node, path
        queue: deque[Tuple[Node, list[int]]] = deque([(start_node, [])])
        visited: set[int] = set()
        while queue:
            node, path = queue.popleft()
            if node_condition(node):
                return node, path
            visited.add(node.state)
            for inputs, outputs in node.outlinks.items():
                child_node = nodes.get(outputs)
                if child_node and child_node.state not in visited:
                    queue.append((child_node, path + [inputs]))
        return None, []

    def analyze(self, output_file_name: str):
        nodes: dict[int, Node] = dict[int, Node]()
        path_cache: dict[int, Tuple[Node, list[int]]] = dict[
            int, Tuple[Node, list[int]]
        ]()
        outlinks_total = 0
        outlinks_done = 0
        outputs = self._pal.read_outputs(0, clock=True)
        state = outputs & 0b_000_1111_0
        node, _ = self._get_or_create_node(nodes, state)
        outlinks_total += node.inputs.count
        while True:
            # can we create outlink?
            if not node.inputs.empty:
                inputs = node.inputs.dequeue()
                outputs = self._pal.read_outputs(inputs, clock=True)
                state = outputs & 0b_000_1111_0
                node.outlinks[inputs] = state
                outlinks_done += 1
                child_node, node_created = self._get_or_create_node(nodes, state)
                outlinks_total += child_node.inputs.count if node_created else 0
                node = child_node
                print(f"{outlinks_done} / {outlinks_total} ({len(nodes)} states)")
            else:
                # can we walk to node that is not yet completely mapped out?
                start_node = node
                node, path = (
                    self._find_path(
                        path_cache,
                        nodes,
                        start_node,
                        lambda _node: not _node.inputs.empty,
                    )
                    if outlinks_done < outlinks_total
                    else (None, None)
                )
                assert not node or not node.inputs.empty, "We found a complete node"
                if node:
                    self._walk_to(path)
                    path_cache[start_node.state] = (node, path)
                else:  # can't find any incomplete node
                    # do we have everything we need?
                    if all(node.inputs.empty for node in nodes.values()):
                        print("We have everything we need.")
                    else:
                        print(
                            "We don't have everything we need, but we can't do anything more without power-cycling."
                        )
                    print(f"Total outlinks: {outlinks_total}")
                    self.save_states_to_file(nodes, output_file_name)
                    return

    # inputs:  f12 f19 f13 fq14 fq15 fq16 fq17 f18 - i9 i8 i7 i6 i5 i4 i3 i2 -
    #          F/0 F/0 F/0 F    F    F    F    F/0 0 I  I  I  I  I  I  I  I  0
    # outputs: io12 io19 io13 q14 q15 q16 q17 io18 - - - - - - - - - -
    #          T/O  T/O  T/O  Q   Q   Q   Q   T/O  0 0 0 0 0 0 0 0 0 0
    @staticmethod
    def convert_file(
        filename: str,
        output_filename: str,
        inputs_mask="FFFFFFFF0IIIIIIII0",
        outputs_mask="TTTQQQQT0000000000",
        inv_hi_z=False,
    ):
        inputs_count = inputs_mask.count("F") + inputs_mask.count("I")
        outputs_count = (
            outputs_mask.count("O")
            + 2 * outputs_mask.count("T")
            + outputs_mask.count("Q")
        )
        input_names = [
            "f12",
            "f19",
            "f13",
            "fq14",
            "fq15",
            "fq16",
            "fq17",
            "f18",
            "",
            "i9",
            "i8",
            "i7",
            "i6",
            "i5",
            "i4",
            "i3",
            "i2",
            "",
        ]
        output_names = ["io12", "io19", "io13", "q14", "q15", "q16", "q17", "io18"]
        output_names_tri_state = [
            "z12",
            "z19",
            "z13",
            "",
            "",
            "",
            "",
            "z18",
        ]
        inputs_header = [
            f" {input_name}" if input_char in ["I", "F"] else ""
            for input_char, input_name in zip(inputs_mask, input_names)
        ]
        outputs_header = [
            f" {output_name}" if output_char in ["O", "T", "Q"] else ""
            for output_char, output_name in zip(outputs_mask, output_names)
        ] + [
            f" {output_name}" if output_char == "T" else ""
            for output_char, output_name in zip(outputs_mask, output_names_tri_state)
        ]
        header = f""".i {inputs_count}
.o {outputs_count}
.ilb{"".join(inputs_header)}
.ob{"".join(outputs_header)}
.phase {"1" * outputs_count}
"""
        rows = {}
        with open(filename, "r") as file:
            data: dict[int, dict] = json.load(file)
        with open(output_filename, "w") as output_file:
            output_file.write(header + "\n")
            for _, state in data.items():
                for inputs, outputs in state["mappings"].items():
                    inputs_nrm = bstr18(int(inputs)).replace("_", "")
                    outputs_nrm = outputs.replace("_", "") + "0000000000"
                    register_inputs_nrm = (
                        bstr8(state["outlinks"][inputs]).replace("_", "") + "0000000000"
                    )
                    row_inputs = ""
                    for _, (input_char, output_char, input_mask) in enumerate(
                        zip(inputs_nrm, outputs_nrm, inputs_mask)
                    ):
                        if input_mask == "F":
                            row_inputs += (
                                input_char if output_char == "Z" else output_char
                            )
                        elif input_mask == "I":
                            row_inputs += input_char
                    row_outputs = ""
                    for _, (
                        input_char,
                        output_char,
                        register_char,
                        output_mask,
                    ) in enumerate(
                        zip(inputs_nrm, outputs_nrm, register_inputs_nrm, outputs_mask)
                    ):
                        if output_mask in ["O", "T"]:
                            row_outputs += "-" if output_char == "Z" else output_char
                        elif output_mask == "Q":
                            row_outputs += register_char
                    for _, (output_char, output_mask) in enumerate(
                        zip(outputs_nrm, outputs_mask)
                    ):
                        if output_mask == "T":
                            if not inv_hi_z:
                                row_outputs += "1" if output_char == "Z" else "0"
                            else:
                                row_outputs += "0" if output_char == "Z" else "1"
                    if row_inputs in rows:
                        assert rows[row_inputs] == row_outputs
                    else:
                        output_file.write(f"{row_inputs} {row_outputs}\n")
                        rows.update({row_inputs: row_outputs})
            # fill in the gaps
            for i in range(2**inputs_count):
                inputs = format(i, f"0{inputs_count}b")
                if inputs not in rows:
                    output_file.write(f"{inputs} {"-" * outputs_count}\n")


class PalLAnalyzer:
    def __init__(self, pal: PalBase):
        self._pal = pal

    def analyze(
        self,
        output_filename: str,
        stdout_filename: str = None,
    ):
        # set I/O mask
        io_mask = (
            0b00_111111_0000000000
            if self._pal.type == PalType.PAL16L8
            else 0b00_000000_0000000000
        )
        with open(output_filename, "w") as output_file:
            # redirect stdout to the file
            if stdout_filename:
                stdout_file = open(stdout_filename, "w")
                sys.stdout = stdout_file
            inputs_queue = AddOnceQueue()
            for i in range(2**10):
                inputs_queue.add(i)
            while not inputs_queue.empty:
                inputs = inputs_queue.dequeue()
                outputs, hi_z_mask = self._pal.read_states(inputs)
                hi_z_mask <<= 10
                outputs <<= 10
                for io_inputs in bcomb(hi_z_mask & io_mask):
                    new_inputs = inputs ^ io_inputs
                    print(f"Candidate for new inputs: {bstr18(new_inputs)}")
                    if new_inputs not in inputs_queue.set:
                        print("Enqueuing.")
                        inputs_queue.add(new_inputs)
                # output final mapping
                print(
                    f"Final mapping: {bstr18(inputs)} -> {bstr18(outputs, hi_z_mask)}"
                )
                output_file.write(f"{bstr18(inputs)} -> {bstr18(outputs, hi_z_mask)}\n")
            # restore stdout
            if stdout_filename:
                stdout_file.close()
                sys.stdout = sys.__stdout__

    @staticmethod
    def convert_file(
        filename: str,
        out_filename: str,
        pal_type: PalType,
        inputs_mask=None,  # I - input, F - feedback, 0 - ignore
        outputs_mask=None,  # O - output, T - tri-state, 0 - ignore
    ):
        # set masks
        inputs_mask = inputs_mask or "00000000IIIIIIIIII"
        outputs_mask = outputs_mask or (
            "TTTTTTTT0000000000"
            if pal_type == PalType.PAL16L8
            else "OOOOOOOO0000000000"
        )
        # set output file header
        inputs_count = inputs_mask.count("F") + inputs_mask.count("I")
        outputs_count = outputs_mask.count("O") + 2 * outputs_mask.count("T")
        io_prefix = "i" if pal_type == PalType.PAL16L8 else ""
        input_names = [
            "f12",
            "f19",
            "f13",
            "f14",
            "f15",
            "f16",
            "f17",
            "f18",
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
        output_names = [
            "o12",
            "o19",
            f"{io_prefix}o13",
            f"{io_prefix}o14",
            f"{io_prefix}o15",
            f"{io_prefix}o16",
            f"{io_prefix}o17",
            f"{io_prefix}o18",
        ]
        output_names_tri_state = [
            "z12",
            "z19",
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
.phase {"1" * outputs_count}
"""
        rows = {}
        with open(out_filename, "w") as output_file:
            output_file.write(header + "\n")
            with open(filename, "r") as file:
                for line in file:
                    inputs, outputs = line.strip().split(" -> ")
                    inputs = inputs.replace("_", "")
                    outputs = outputs.replace("_", "")
                    row_inputs = ""
                    for _, (input_char, output_char, input_mask) in enumerate(
                        zip(inputs, outputs, inputs_mask)
                    ):
                        if input_mask == "I":
                            row_inputs += input_char
                        elif input_mask == "F":
                            if output_char == "Z":
                                row_inputs += input_char
                            else:
                                row_inputs += output_char
                    row_outputs = ""
                    for _, (input_char, output_char, output_mask) in enumerate(
                        zip(inputs, outputs, outputs_mask)
                    ):
                        if output_mask == "O" or output_mask == "T":
                            row_outputs += "-" if output_char == "Z" else output_char
                    for _, (input_char, output_char, output_mask) in enumerate(
                        zip(inputs, outputs, outputs_mask)
                    ):
                        if output_mask == "T":
                            row_outputs += "1" if output_char == "Z" else "0"
                    if row_inputs in rows:
                        assert (
                            rows[row_inputs] == row_outputs
                        ), f"{rows[row_inputs]} != {row_outputs}"
                    else:
                        rows.update({row_inputs: row_outputs})
                        output_file.write(f"{row_inputs} {row_outputs}\n")
                # add missing combinations
                for i in range(2**inputs_count):
                    inputs = format(i, f"0{inputs_count}b")
                    if inputs not in rows:
                        output_file.write(f"{inputs} {"-" * outputs_count}\n")
