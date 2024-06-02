import json
import random
import time

import analyzer
import usb_relay

from analyzer import analyze, save_to_file
from pal import Pal16R4DuPAL, Pal16R4IC12

#
pal = Pal16R4DuPAL(port="COM5")
# open file for writing
with open("C:\\Work\\pal_tester\\output_new.txt", "w") as file:
    while True:
        if False:  # random.randint(0, 3) == 0:
            pal.clock()
            file.write("Clock\n")
        else:
            inputs = random.randint(0, 255)
            inputs = inputs | 0b10000000
            file.write(f"{str(inputs)}\n")
            pal.set_inputs(inputs)
        pal.read_outputs()
        file.write(f"{str(pal.outputs_as_byte)}\n")
        print(pal)
        time.sleep(0.1)
        file.flush()

# pal = Pal16R4IC12()

# print(pal)

# with open("C:\\Work\\pal_tester\\output.txt", "r") as file:
#     lines = file.readlines()
#
# for inputs, outputs in zip(lines[0::2], lines[1::2]):
#     if inputs == "Clock\n":
#         pal.clock()
#         print("Clock")
#     else:
#         pal.set_inputs(int(inputs))
#         print(f"inputs: {int(inputs)}")
#     pal.read_outputs(outputs=int(outputs))
#     print(pal)


# def reset_dupal(handle):
#     usb_relay.relay_off(handle)
#     time.sleep(0.5)
#     usb_relay.relay_on(handle)
#
#
# handle, devices = usb_relay.initialize_relay_device()
#
# reset_dupal(handle)
#
# done = False
# while not done:
#     # pal = Pal16R4IC12()
#     pal = Pal16R4DuPAL(port="COM5")
#     done = analyze(pal, set_one_mask=0b10000000)
#     save_to_file("C:\\Work\\pal_tester\\full_read_ic12.json")
#     time.sleep(0.5)
#     reset_dupal(handle)
#
# usb_relay.finalize_relay_device(handle, devices)

# analyzer.read_from_file("C:\\Work\\pal_tester\\full_read_ic12.json")
# # analyzer.save_tables("C:\\Work\\pal_tester\\tables.json")
# #inverted_nodes = analyzer.build_inverted_graph(analyzer.nodes)
# #inverted_inverted_nodes = analyzer.build_inverted_graph(inverted_nodes)
# #analyzer.nodes = inverted_inverted_nodes
# #analyzer.save_to_file("C:\\Work\\pal_tester\\output_check.json")
# analyzer.build_tables("C:\\Work\\pal_tester\\tables.txt")
