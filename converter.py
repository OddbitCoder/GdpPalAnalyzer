import json

from node import Node


class Converter:
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

    @staticmethod
    def _read_from_file(file_name: str) -> dict[int, Node]:
        with open(file_name, "r", encoding="utf-8") as file:
            data_json = file.read()
            nodes = json.loads(data_json)
            return {int(k): Converter._create_node(v) for k, v in nodes.items()}

    @staticmethod
    def _create_table_entry(file, feedbacks: int, inputs: int, outputs: int):
        file.write(f"{feedbacks:08b}{inputs:08b} {outputs:08b}\n")

    @staticmethod
    def _get_child_node(
        nodes: dict[int, Node], node: Node, inputs: int, clock: bool = False
    ):
        if clock:
            node_id = [o for i, o in node.clock_outlinks if inputs == i][0]
        else:
            node_id = [o for i, o in node.outlinks if inputs == i][0]
        return nodes[node_id]

    @staticmethod
    def convert_to_table_16l8(input_file_name: str, output_file_name: str):
        nodes = Converter._read_from_file(input_file_name)
        tabu = {}
        with open(output_file_name, "w", encoding="utf-8") as file:
            file.write("# PAL16L8\n")
            file.write(".i 16\n")
            file.write(".o 8\n")
            file.write(
                ".ilb fio12 fio19 fio13 r14 r15 r16 r17 fio18 i9 i8 i7 i6 i5 i4 i3 i2\n"
            )
            file.write(".ob io12 io19 io13 ir14 ir15 ir16 ir17 io18\n")
            file.write(".phase 00000000\n")

    @staticmethod
    def convert_to_table(input_file_name: str, output_file_name: str):
        nodes = Converter._read_from_file(input_file_name)
        tabu = {}
        with open(output_file_name, "w", encoding="utf-8") as file:
            file.write("# PAL16R4\n")
            file.write(".i 16\n")
            file.write(".o 8\n")
            file.write(
                ".ilb fio12 fio19 fio13 r14 r15 r16 r17 fio18 i9 i8 i7 i6 i5 i4 i3 i2\n"
            )
            file.write(".ob io12 io19 io13 ir14 ir15 ir16 ir17 io18\n")
            file.write(".phase 00000000\n")
            for node in nodes.values():
                for inputs, child_node_id in node.outlinks:
                    child_node = nodes[child_node_id]
                    # here we have: node --inputs--> child_node
                    clock_node = Converter._get_child_node(nodes, node, inputs, True)
                    # assertion 1: child_node --inputs--> child_node
                    should_be_child_node = Converter._get_child_node(
                        nodes, child_node, inputs
                    )
                    if should_be_child_node.outputs != child_node_id:
                        print("WARNING: Child node is not connected to itself!")
                        print(f"Node: {node.outputs}")
                        print(f"Child node: {child_node_id}")
                        print(f"Inputs: {inputs}")
                        print(f"Child node connects to: {should_be_child_node.outputs}")
                    # assertion 2: child_node --inputs+clock--> clock_node
                    should_be_clock_node = Converter._get_child_node(
                        nodes, child_node, inputs, True
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
                        clock_node_child = Converter._get_child_node(
                            nodes, clock_node, inputs, True
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
                            Converter._create_table_entry(
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
                        Converter._create_table_entry(
                            file,
                            node.outputs,
                            inputs,
                            outputs,
                        )
                        tabu[key] = outputs
                    # NO-CLOCK TRANSITION END STATE:
                    # inputs: child_node.outputs feedbacks, inputs
                    # outputs: child_node.outputs (input into registers from node.clock_outlinks)
                    # key = f"{child_node.outputs:08b}{inputs:08b}"
                    # outputs = (child_node.outputs & 0b11100001) + reg_inputs
                    # if key in tabu:
                    #     if tabu[key] != outputs:
                    #         print(
                    #             f"WARNING: Entry already exists but with different outputs: {key} -> {tabu[key]:08b} instead of {outputs:08b} [3]"
                    #         )
                    # else:
                    #     Converter._create_table_entry(
                    #         file,
                    #         child_node.outputs,
                    #         inputs,
                    #         outputs,
                    #     )
                    #     tabu[key] = outputs
