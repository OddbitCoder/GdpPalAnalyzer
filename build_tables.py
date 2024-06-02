import analyzer

analyzer.read_from_file("full_read_ic12.json")

nodes = analyzer.nodes


def create_table_entry(file, feedbacks: int, inputs: int, outputs: int):
    file.write(f"{feedbacks:08b}{inputs:08b} {outputs:08b}\n")


with open("tables.txt", "w", encoding="utf-8") as file:
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
            # if node.outputs == 236 and inputs == 232 and child_node.outputs == 77:
            #     print("DEBUG")
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
